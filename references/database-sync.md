# PostgreSQL 同步口径

当系统已启用 PostgreSQL 索引层时，创建 agent 不只是文件动作，还必须补正式数据层。

## 最低要求

至少要能在数据库中查到：

- `agent_runtime.agents`
- `agent_runtime.sessions`
- `core.resources`
- `core.resource_versions`
- `agent_runtime.agent_resource_links`

## agent 档案

`agent_runtime.agents` 至少应具备：

- `code`
- `display_name`
- `role_type`
- `status`
- 所属 `department_id`
- 需要时的 `parent_agent_id`

## 文档资源

基础工作区文件至少应有资源索引：

- `AGENTS.md`
- `IDENTITY.md`
- `HEARTBEAT.md`
- `MEMORY.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`

## 会话资源

如已建立主会话，应同时同步：

- `agent_runtime.sessions`
- 对应的 `session_log` 资源索引

## 汇报约束

如果数据库未同步完成，只能说：

- 已建立 workspace 骨架
- 已建立可运行内部 agent（数据库未同步）

不能直接说“已建立完整 agent”。
