# Ebbing Assist 系统架构（v1.1）

> 范围调整：当前架构聚焦账号与个人知识库 + 学习记录。艾宾浩斯复习、情绪日志、AI 教练、数据面板等作为扩展位保留设计，不在 MVP 交付。

## 1. 目标与原则
- 支撑 MVP：认证、知识条目 CRUD/搜索、学习记录。
- 可扩展：为后续复习/AI/通知等模块预留独立 Blueprint/Service，避免大改。
- 安全与维护：JWT 鉴权、模块化、可迁移数据库表。

## 2. 整体架构
- **前端**：Vue3 + Vite + Element Plus，基于 Admin 模板；路由模块化（auth/knowledge/logs/...）；状态管理 Pinia；axios 封装。
- **后端**：Flask + Blueprint；Service/Repository 分层；SQLAlchemy（PostgreSQL），Redis 缓存（可选）；Gunicorn + Nginx；APScheduler 预留。
- **扩展位**：`review`（复习）、`mood`（情绪/AI）、`notify`（提醒）、`dashboard` 在 V1.1+ 启用。

## 3. 前端架构要点
- 目录：`src/router/` 路由与守卫；`src/common/apis/` 接口；`src/pages/knowledge`（列表/表单/搜索）、`src/pages/logs`（学习记录）；`src/pinia/stores/` 管理 auth/user/knowledge/logs。
- UI：复用 Admin 布局，列表/表单/日历等 Element Plus 组件；保留 i18n 占位。
- 网络：axios 注入 JWT；统一业务 code 处理；401 时重登。

## 4. 后端模块
- Blueprint 划分（MVP 启用）：`auth`（注册/登录/刷新/注销）、`user`（资料）、`knowledge`（主题/标签/条目 CRUD + 搜索）、`study_log`（学习记录）。
- 预留 Blueprint（V1.1+）：`review`（艾宾浩斯计划/打卡）、`mood`（情绪/AI）、`notify`（提醒）、`dashboard`。
- 分层：Blueprint -> Service（业务/事务） -> Repository/Model（SQLAlchemy）。
- 基础设施：配置分环境；统一错误码/响应；JWT；日志；（可选）APScheduler。

## 5. 数据存储
- PostgreSQL：用户、主题/分类、知识条目、学习记录；预留复习计划/打卡、情绪日志、通知表。
- Redis（可选）：短期缓存（热门搜索结果、首页统计占位）、token 黑名单、速率限制。
- 对象存储占位：附件/链接暂用 URL 字段，未来接入 OSS。

## 6. 核心流程（MVP）
- 认证：注册/登录 -> JWT；刷新/注销。
- 知识条目：创建/编辑/删除 -> 列表/搜索（关键词、标签、主题）；分页。
- 学习记录：选择条目 + 备注 -> 写入记录表；近 7 天查询。

## 7. 可扩展设计（V1.1+）
- **复习系统**：独立 `review` Blueprint + 表（review_plans/review_logs），可用 APScheduler 生成/提醒。
- **情绪/AI**：`mood` Blueprint，AI Provider 适配层（OpenAI/本地）；敏感词/超时/重试。
- **通知**：`notify` Blueprint + 任务调度；站内/邮件。
- **数据面板**：`dashboard` 汇总查询 + 缓存。

## 8. 部署与运维
- Docker Compose：frontend（静态）、backend（Gunicorn）、postgres、redis（可选）、nginx。
- CI/CD：GitHub Actions 进行 lint/test/build，镜像推送；`.env` 管理配置与密钥。
- 监控占位：健康检查 `/health`，后续可接入 metrics。

## 9. 安全
- JWT + Refresh；密码哈希；资源按 user_id 过滤。
- CORS 按前端域白名单；输入校验；日志审计。

## 10. 性能与演进
- MVP 以简单查询为主；搜索先用 SQL 模糊，未来可切换全文索引/专用搜索。
- 模块隔离：新增 Blueprint 不影响现有路由；DB 迁移通过 Alembic/Flask-Migrate。
