# OpenClaw Agent 验收清单

一个 agent 只有满足下面清单，才能算“已建立”。

## 最小可运行标准

1. 已加入 `openclaw.json` 的 `agents.list`
2. 已建立独立 workspace
3. 已建立独立 `agentDir`
4. 已建立独立 `sessions/sessions.json`
5. 已明确 `heartbeat` 策略（开启或关闭）
6. 已能出现在 `openclaw agents list --bindings`
7. 主会话如已创建，`displayName` 已标准化，不显示成裸 `main`
8. 用户可见名称严格等于用户给出的中文名，不拼内部 `agentId / accountId`

## 完整标准

9. 如系统启用数据库索引层，已同步 PostgreSQL
10. 如需要外部入口，已完成 channel/account 绑定
11. 如需要外部入口，已完成首次可用性验证
12. 未在其他 agent workspace 下遗留错误副本
13. 内部 `agentId / accountId` 均为英文 / 拼音 / ASCII
14. 如要求单窗口展示，已说明 heartbeat 会话处理方式；若保留 heartbeat，已绑定到真实会话 `session key` 或采取等效单窗口方案
15. 如本次接入了 bot，已引导用户发送首条消息激活真实会话
16. 如本次接入了 bot，重复窗口已完成收口或已明确说明待收口

## 不合格的常见情况

- 只建了 `.md` 文件
- `sessions.json` 为空且从未初始化会话
- 加了 `agents.list` 但没建 `agentDir`
- 接了 bot 但没做路由绑定
- 已建独立 workspace，但数据库无对应档案
- 在上级 workspace 下又复制出一份同名子目录
- 主会话存在，但 UI 里显示成 `main`
- 顶部 agent 分组或会话选项里混入 `(rnd-b1)`、`(whatsapp)` 这类内部备注
- 会话名里残留 `/ heartbeat`
- 把 heartbeat 直接指向 direct session key，导致配置无效
- 明明要求单窗口，却仍保留独立 `agent:<id>:main` heartbeat 窗口
- 只完成 pairing 或只完成 bot token 配置，就说“入口已接好”
- token 写进去后就结束，没有继续引导用户激活第一条真实会话
- 新 bot 已接入，但重复窗口还挂在界面里没收口

## 建议验收命令

```bash
openclaw agents list --bindings
openclaw channels status --probe
openclaw sessions --agent <agent-id> --json
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
4. heartbeat 策略：开启 / 关闭 / 未明确
5. live 列表：是 / 否
6. 会话显示名：是 / 否
7. 中文名纯净显示：是 / 否
8. 数据库：是 / 否
9. 外部入口：是 / 否 / 不需要
10. 路径误建副本：无 / 有
11. 首条真实外部会话：是 / 否 / 不需要
12. 重复窗口收口：已完成 / 未完成 / 不需要

剩余缺口：
- ...
```
