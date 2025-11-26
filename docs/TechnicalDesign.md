# Ebbing Assist 技术设计（v1.0）

## 1. 范围
定义 MVP 的后端接口、数据结构、核心算法（艾宾浩斯复习）、调度与缓存策略，前端调用约定。

## 2. 技术栈
- Backend：Python 3.11 + Flask + SQLAlchemy + Marshmallow/Pydantic（校验）+ Redis + APScheduler + Gunicorn。
- DB：PostgreSQL；缓存 Redis。
- Frontend：Vue3 + Vite + Element Plus + Pinia；axios API 封装。
- AI：OpenAI 或本地模型，通过统一 `ai.provider` 适配。

## 3. 数据库设计（关键表）
| 表 | 关键字段 | 说明 |
| --- | --- | --- |
| users | id, email, phone, password_hash, nickname, avatar, timezone, prefs(jsonb), created_at | 基础用户 |
| auth_tokens | user_id, refresh_token, expires_at | 刷新管理 |
| plans | id, user_id, title, goal, deadline, priority, tags(text[]), status, progress, created_at, updated_at | 学习计划 |
| tasks | id, plan_id, title, desc, estimate_minutes, priority, status, due_date, tags(text[]), order_no, focus_minutes, created_at, updated_at | 任务/子任务 |
| pomodoro_sessions | id, task_id, user_id, start_at, end_at, focus_minutes, note | 番茄记录 |
| cards | id, user_id, subject, title, content, tags(text[]), difficulty, attachment_url, created_at | 知识点/卡片 |
| review_plans | id, card_id, schedule jsonb, next_review_at, last_result | 复习计划 |
| review_logs | id, card_id, review_at, result, note | 复习打卡 |
| moods | id, user_id, score, tags(text[]), text, created_at | 情绪日志 |
| ai_feedback | id, mood_id, advice_text, model, tokens, created_at | AI 反馈 |
| notifications | id, user_id, type, target_id, channel, schedule_at, sent_at, status, payload jsonb | 提醒/通知 |

索引：`users.email/phone` 唯一；`tasks.due_date`, `review_plans.next_review_at`, `moods.created_at`，`notifications.schedule_at`；tags 使用 gin（text[]）。

## 4. API 规范
- **通用响应**：`{ code: 0, message: "ok", data: {...} }`；错误码非 0。
- **鉴权**：Bearer Token；部分访客接口允许匿名（注册/登录/健康检查）。
- **分页**：`page`, `page_size`；排序 `sort_by`, `order`.
- **错误码**：1001 参数错误；1002 未认证；1003 无权限；200x 业务类。

### Auth
- `POST /api/auth/register` `{email?, phone?, password, code?}` -> 201, 返回 token。
- `POST /api/auth/login` `{email/phone, password}` -> tokens（access, refresh）。
- `POST /api/auth/refresh` `{refresh_token}`.
- `POST /api/auth/logout` -> 204。

### User
- `GET /api/user/profile` -> 个人资料+偏好。
- `PUT /api/user/profile` `{nickname, avatar, timezone, prefs}`.

### Plan & Task
- `GET /api/plans`（筛选：status, priority, tag, date range）。
- `POST /api/plans` `{title, goal, deadline, priority, tags}`.
- `GET /api/plans/{id}` -> 计划+任务列表。
- `PUT /api/plans/{id}` `{title, goal, deadline, priority, tags, status}`.
- `DELETE /api/plans/{id}`.
- `POST /api/plans/{id}/tasks` `{title, desc, estimate_minutes, priority, due_date, tags}`.
- `PUT /api/tasks/{id}` `{title?, desc?, estimate_minutes?, priority?, due_date?, tags?, status?, order_no?}`.
- `POST /api/tasks/{id}/complete` -> 标记完成并更新时间/进度。
- `POST /api/tasks/{id}/pomodoro` `{start_at?, end_at?, focus_minutes, note?}` -> 记录番茄。

### Review（艾宾浩斯）
- `POST /api/review/cards` `{subject, title, content, tags, difficulty, attachment_url?}` -> 创建卡片并生成复习计划。
- `GET /api/review/cards`（筛选：subject/tag/difficulty/text）。
- `GET /api/review/today` -> 今日待复习列表（带 next_review_at）。
- `POST /api/review/{card_id}/log` `{result: remember|fuzzy|forgot, note?}` -> 打卡并重算计划。
- `GET /api/review/stats` -> 完成率、遗忘率、下次复习预估。

### Mood & AI Coach
- `POST /api/mood/logs` `{score(1-5), tags, text}` -> 创建日志。
- `GET /api/mood/logs`（日期范围/标签）。
- `GET /api/mood/trends` -> 周/月趋势，词频。
- `POST /api/mood/{id}/advice` -> 触发/刷新 AI 反馈（若不存在自动生成）。

### Notify
- `GET /api/notify` -> 用户通知列表。
- `POST /api/notify/test` -> 触发测试通知（dev）。

### Dashboard
- `GET /api/dashboard/summary` -> 今日待办/复习数量、完成率、番茄累计、情绪今日状态、近 7 天趋势。

## 5. 核心逻辑设计
### 艾宾浩斯复习调度
- 默认间隔：`[1, 2, 4, 7, 15, 30]` 天（可在配置中调整）。
- 算法：
```
init: next_review_at = today + 1d
log(result):
  if result == remember: interval_index += 1
  if result == fuzzy: interval_index = max(interval_index - 1, 1)
  if result == forgot: interval_index = 1
  next_review_at = today + intervals[interval_index]
  append review_logs
```
- AI 调整：在 `remember` 连续 N 次后，调用 AI 推荐更长间隔；返回值写入 schedule 覆盖后续间隔。

### 计划进度与番茄
- 任务完成更新 `tasks.status=done`，记录 `completed_at`，累积 `focus_minutes`。
- 计划进度 = 完成任务数 / 总任务数；写回 plans.progress。

### 缓存策略
- Redis key 约定：`dash:{user_id}:summary`（30-60s）；`review:{user_id}:today`（5m）。
- 打卡/完成任务后删除相关缓存；登录后加载基础缓存。

### 通知调度
- APScheduler 每 5 分钟扫描 `notifications.schedule_at <= now and status=pending`。
- 对复习/计划到期生成通知记录：`type=review_due/task_due`，channel=site/email。
- 发送后写入 `sent_at` 与状态；失败重试最多 3 次。

## 6. 校验与错误处理
- 入参使用 Schema 校验；统一错误码。
- 身份校验：所有资源以 `user_id` 过滤；禁止跨用户访问。
- 乐观锁：任务排序/批量调整可带 `updated_at`（可选）。

## 7. 前端对接要点
- axios 拦截器：401 触发刷新或跳转登录；错误提示统一处理。
- 路由守卫：登录态校验；敏感页面（设置、情绪）需登录。
- 组件复用：表格（计划/任务/卡片）、表单弹窗、图表卡片、计时器、情绪评分组件。
- i18n 预留：文案 key 形式存放。

## 8. 测试策略（概要）
- 单元：Service、算法（艾宾浩斯）、通知生成、AI 适配器。
- 集成：Auth、Plan/Task、Review、Mood 流程的 API 测试（pytest + test client）。
- 前端：组件渲染、store 动作（Vitest）；关键表单校验；计时器逻辑。

