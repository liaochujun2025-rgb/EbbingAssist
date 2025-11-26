# Observability (Logging + ES/Kibana)

## 启动
```bash
docker compose up -d
```
- Backend: http://localhost:8000
- Frontend: http://localhost:8080
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601

## 日志采集
- 后端日志：JSON 格式输出到 stdout 和 `backend/logs/app.log`，Fluent Bit tail 文件并写入 Elasticsearch 索引 `ebbingassist-logs`。
- 核心字段：timestamp, level, logger, trace_id, path, method, status_code, user_id, error_message, stack, duration_ms。

## Kibana 查看
1) 打开 http://localhost:5601
2) 在 Discover 选择索引模式 `ebbingassist-logs*`
3) 常用过滤：
   - trace_id: 在搜索栏输入 `trace_id:<your-trace-id>`
   - 路径：`path:/api/auth/login`
   - 用户：`user_id:123`
4) 可视化：按 level/status_code/路径聚合；或按 trace_id 关联请求/错误日志。

## 注意
- ES/Kibana 未开启安全认证（单机调试）。生产需启用 xpack security。
- Fluent Bit 读取的路径：`/app/logs/app.log`（容器内），如需调整请同步后端日志目录与 docker-compose 卷。
