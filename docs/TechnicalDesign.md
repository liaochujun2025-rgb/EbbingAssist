# Ebbing Assist 技术设计（v1.1，MVP 聚焦知识库）

> 范围：仅实现账号体系、知识管理（条目/标签/简单卡片）、学习记录。复习（review）、情绪（mood）、AI 教练、数据面板等模块保留文件/蓝图占位，保持可导入不报错，业务逻辑留待后续。

## 1. 技术栈
- Backend：Python 3.11 + Flask + SQLAlchemy + Marshmallow/Pydantic（校验）+ Redis（可选）+ Gunicorn。Flask-Migrate 做迁移。
- DB：PostgreSQL；缓存 Redis（可选，用于热门搜索或短期 token）。
- Frontend：Vue3 + Vite + Element Plus + Pinia；axios API 封装。
- AI/调度：无强制实现，review/mood/notify 保持占位。

## 2. 数据库设计（MVP 表）
| 表 | 关键字段 | 说明 |
| --- | --- | --- |
| users | id, email, phone, password_hash, nickname, avatar, timezone, prefs(jsonb), created_at | 基础用户 |
| auth_tokens | user_id, refresh_token, expires_at | 刷新管理（可选持久化黑名单） |
| topics | id, user_id, name, desc, created_at | 主题/分类（可选） |
| knowledge_entries | id, user_id, topic_id?, title, content, tags(text[]), links(jsonb), created_at, updated_at | 知识条目/卡片 |
| study_logs | id, user_id, entry_id, note, logged_at | 学习记录（关联条目） |

> 预留表（V1.1+ 不开发）：review_plans/review_logs, moods, ai_feedback, notifications, pomodoro_sessions 等可按需保留空模型。

索引：`users.email/phone` 唯一；`knowledge_entries.tags` gin；`knowledge_entries.title/content` 可后续全文索引；`study_logs.logged_at`；`topics.user_id`。

## 3. API 规范
- 响应：`{ code: 0, message: "ok", data: {...} }`；错误码非 0。
- 鉴权：Bearer Token；注册/登录/健康检查可匿名。
- 分页：`page`, `page_size`；排序 `sort_by`, `order`.
- 错误码：1001 参数错误；1002 未认证；1003 无权限；200x 业务类。

### Auth
- `POST /api/auth/register` `{email?, phone?, password}` -> tokens（access/refresh）。
- `POST /api/auth/login` `{email_or_phone, password}` -> tokens。
- `POST /api/auth/refresh` `{refresh_token}` -> 新 access。
- `POST /api/auth/logout` -> 204。

### User
- `GET /api/user/profile` -> 个人资料+偏好。
- `PUT /api/user/profile` `{nickname, avatar, timezone, prefs}`。

### Knowledge
- `GET /api/knowledge/topics` -> 列表；`POST /api/knowledge/topics` 创建；`PUT/DELETE /api/knowledge/topics/{id}`。
- `GET /api/knowledge/entries` 筛选：`keyword`（title/content 模糊）、`tag`、`topic_id`、分页/排序。
- `POST /api/knowledge/entries` `{title, content, tags?, topic_id?, links?}`。
- `GET /api/knowledge/entries/{id}` 详情。
- `PUT /api/knowledge/entries/{id}` 更新字段。
- `DELETE /api/knowledge/entries/{id}` 删除。

### StudyLog
- `POST /api/study/logs` `{entry_id, note?, logged_at?}`（缺省为今日）。
- `GET /api/study/logs` 查询近 7 天或指定日期区间。

### 预留接口（占位，不在 MVP 实现）
- review：`/api/review/*`
- mood/coach：`/api/mood/*`
- notify/dashboard：`/api/notify/*`, `/api/dashboard/*`

## 4. 核心逻辑（MVP）
- 知识条目：支持 tags 数组；links 可存储外链/附件 URL；模糊搜索（先用 ILIKE，后续可全文索引）。
- 学习记录：记录 entry_id + note + logged_at；限制同一条目同日可多条或去重逻辑由前端控制（MVP 可允许多条）。
- 认证：JWT access/refresh；黑名单表可选。

## 5. 缓存与性能
- 可选 Redis 缓存：热门搜索结果 `knowledge:search:{user}:{hash}`；基础速率限制留占位。
- 登录后或写操作后清理相关缓存（如后续接入）。

## 6. 校验与错误处理
- Schema 校验必填字段；title/entry_id 等空值报 1001。
- 身份校验：资源均按 `user_id` 过滤；跨用户访问返回 404/403。

## 7. 前端对接要点
- axios 拦截器已处理 1002/2003 触发重登；后端返回 code=0 的 data 结构。
- 路由仅保留知识管理与登录；其他页面入口隐藏但文件保留。
- 组件：知识列表/搜索、编辑表单、学习记录表单+列表；标签多选。

## 8. 测试策略
- 后端：Auth/Knowledge/StudyLog 的 Service + API 测试（pytest + flask test client）。
- 前端：Vitest 针对知识列表/表单、学习记录表单与展示；基础路由守卫。
- 预留模块（review/mood/notify）仅需 import 不报错，无需业务测试。
