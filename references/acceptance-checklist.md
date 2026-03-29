# OpenClaw Agent 验收清单

一个 agent 只有满足下面清单，才能算“已建立”。

## 最小可运行标准

1. 已加入 `openclaw.json` 的 `agents.list`
2. 已建立独立 workspace
3. 已建立独立 `agentDir`
4. 已建立独立 `sessions/sessions.json`
5. 已配置 `heartbeat`
6. 已能出现在 `openclaw agents list --bindings`

## 完整标准

7. 如系统启用数据库索引层，已同步 PostgreSQL
8. 如需要外部入口，已完成 channel/account 绑定
9. 如需要外部入口，已完成首次可用性验证
10. 未在其他 agent workspace 下遗留错误副本

## 不合格的常见情况

- 只建了 `.md` 文件
- `sessions.json` 为空且从未初始化会话
- 加了 `agents.list` 但没建 `agentDir`
- 接了 bot 但没做路由绑定
- 已建独立 workspace，但数据库无对应档案
- 在上级 workspace 下又复制出一份同名子目录

## 建议验收命令

```bash
openclaw agents list --bindings
openclaw channels status --probe
psql -d openclaw -P pager=off -x -c "select code, display_name, status from agent_runtime.agents;"
```

## 汇报模板

```text
状态结论：
- 已建立 workspace 骨架 / 已建立可运行内部 agent / 已建立可运行 agent 并已绑定外部入口

验收结果：
1. agents.list：是 / 否
2. agentDir：是 / 否
3. sessions：是 / 否
4. heartbeat：是 / 否
5. live 列表：是 / 否
6. 数据库：是 / 否
7. 外部入口：是 / 否 / 不需要

剩余缺口：
- ...
```
