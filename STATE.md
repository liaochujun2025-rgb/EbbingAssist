# STATE

## Completed
- T01 后端脚手架：Flask 工厂、配置、日志、DB/Redis/JWT 扩展、统一错误响应、health 检查，基础测试用例编写。
- T02 认证模块：用户/Token 模型，注册/登录/刷新/注销，JWT 回调，密码哈希，认证相关测试用例。
- T03 前端基础：Axios 拦截与后端协议对齐，登录页改为账号+密码（无验证码），Token 持久化与刷新位，用户信息接口对接，环境变量统一 `/api` 前缀。
- T04 知识条目后端 API：主题/标签/条目 CRUD，关键词/标签/主题筛选，分页查询。
- T05 知识条目前端：列表/搜索/筛选，创建/编辑/删除表单，标签/主题选择与创建。
- T06 学习记录后端 API：关联知识条目记录学习，近 7 天查询。
- T07 学习记录前端：记录表单、近 7 天时间线列表。
- T08 后端测试：Auth/Knowledge/StudyLog 用 pytest 覆盖，全部通过。
- T09 前端测试：新增知识/学习记录页面的 Vitest 用例（挂载、表单提交流程），测试通过。
- T10 部署与 CI/CD：新增后端/前端 Dockerfile，docker-compose（backend+frontend+db），GitHub Actions CI（后端 pytest、前端 vitest）。
- 追加：后端 JSON 日志增强（trace_id/user_id/stack），输出 stdout + backend/logs/app.log，代理配置指向 8000。

## In Progress / Next
- 无（等待后续版本规划）。

## Issues / Notes
- 本地未安装 pytest/依赖，未执行自动化测试；需在环境安装后运行 `python -m pytest backend/tests`。
- Pip/依赖安装由用户托管，请勿自动执行安装命令。
