---
name: openclaw-agent-builder
description: 为 OpenClaw 创建或补全新 agent 的标准技能。用于“建立新成员”“补全 agent 运行链”“把 workspace 骨架升级成可运行 agent”“检查 agent 是否创建完整”这类任务。按统一流程处理 workspace、agentDir、sessions、heartbeat、openclaw.json、渠道绑定、数据库同步与最终验收。
metadata:
  openclaw:
    emoji: "🧩"
---

# OpenClaw Agent Builder

把“创建一个 agent”当成正式交付，而不是只建几个文件。

当前版目标是：

- 通过初始化向导建立“瘦身版可运行 agent”
- 不在这一版里强行展开完整角色卡
- 默认由当前调用者创建自己的直属下级

初始化向导当前版合同见：

- [references/init-wizard-v1.md](references/init-wizard-v1.md)
- [references/database-sync.md](references/database-sync.md)

## 什么时候使用

- 用户要求新增一个 OpenClaw agent
- 现有 agent 只有 workspace 骨架，需要补成可运行状态
- 需要给 agent 接 Telegram / WhatsApp / 其他渠道入口
- 需要验收一个 agent 是否真的创建完整

## 不要误判完成

以下情况都**不能**叫“已建立 agent”：

- 只建立了 workspace 文件
- 只建立了 `IDENTITY.md / AGENTS.md / MEMORY.md`
- 只加入了 `agents.list`
- 只接了 bot，没有独立 workspace / sessions / heartbeat / 数据库

只有运行链闭环后，才能说“已建立”。

## 这次复盘补上的坑

以下坑位已经在真实建 agent 过程中踩过，后面都要按本 skill 避开：

- 在上级 workspace 里面又嵌套建了一份子 agent 目录
- 只建了 workspace，却没有 `agentDir`、`sessions`、live agent 和数据库记录
- 建了主会话，但没写 `displayName`，UI 里直接显示成裸 `main`
- 虽然写了 `displayName`，但界面仍显示成 `中文名 (agent-id)` 或 `中文名 / heartbeat`
- 误以为 heartbeat 可以直接指向任意 direct session key；当前版本不支持
- 数据库没同步，却把 agent 说成“已建立”
- 内部 `accountId` 直接用中文，导致 Telegram 兼容性问题

后续必须把这些都当成标准风险项处理。

## 标准流程

### 1. 先收最小输入

至少确认这些：

- 正式显示名
- 内部 `agentId`
- 当前阶段是否需要外部 bot / route

如未明确，按下面的默认规则推断：

- 这是当前调用者的直属下级
- 所属部门继承当前调用者
- 当前阶段优先做**内部 agent**
- 不自动接外部入口
- 不主动追问角色卡和完整职责
- 用户可见名称一律先按用户给出的中文名落地，不额外拼内部 `agentId / accountId`

### 2. 建立 workspace 骨架

优先用脚手架：

```bash
/Users/huahua/.openclaw/skills/openclaw-agent-builder/scripts/scaffold_workspace.sh --help
```

这一步必须先做的检查：

- `agentId` 必须是英文 / 拼音 / kebab-case
- `department` slug 必须能对应 `~/.openclaw/shared-rules/departments/<slug>.md`
- workspace 不能嵌套在其他 agent workspace 里面

这一步至少负责：

- `AGENTS.md`
- `IDENTITY.md`
- `HEARTBEAT.md`
- `MEMORY.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `memory/`

如需一次补到运行层，优先使用：

```bash
/Users/huahua/.openclaw/skills/openclaw-agent-builder/scripts/scaffold_workspace.sh \
  --agent-id <agent-id> \
  --display-name <显示名> \
  --workspace <workspace路径> \
  --department <department-slug> \
  --role <角色名> \
  --agent-dir <agentDir路径> \
  --init-runtime \
  --seed-main-session
```

默认会创建今天和昨天的 daily memory 文件，不再留 `YYYY-MM-DD.md` 这种占位骨架。

### 3. 建立运行层

至少补齐：

- `agents.list`
- 独立 `agentDir`
- 独立 `sessions store`
- 明确的 `heartbeat` 策略（开启或关闭，不能留成模糊默认）
- 需要时复制 `models.json` / `auth-profiles.json`
- 如创建了主会话，必须写 `displayName`，避免 UI 显示成裸 `main`

用户可见窗口名规则：

- 用户给什么中文名，窗口就显示什么中文名
- 不在用户可见名称里拼接内部 `agentId / accountId`
- 不在用户可见名称里保留 `/ heartbeat`

如果一个 agent 只是内部席位，允许先不接外部入口；但仍然要有完整运行层。

### 4. 需要渠道时再做绑定

规则：

- 一个 bot 默认只归一个 agent
- `accountId` 一律用英文 / 拼音 / ASCII
- 显示名可以用中文
- 未明确要求时，不要自动抢占现有默认渠道
- 需要首次私聊配对时，要把 pairing 审批也算进接入完成
- 用户给完 token 后，流程不能停，必须继续引导用户发第一条消息来激活真实会话
- 如果激活后同时出现 heartbeat 主会话和真实私聊窗口，必须继续执行会话收口

如果目标是“一个外部直聊窗口 + 保留 heartbeat 且不额外显示 heartbeat 窗口”，更稳的做法是：

- 外部入口先走独立 direct 会话
- 等第一条真实外部会话激活后，记录该会话的显式 `session key`
- 将 heartbeat 的运行上下文切到这条真实会话：
  - `heartbeat.session: "<显式 session key>"`
- 发送策略按需要选择：
  - 静默巡检：`target: "none"`
  - 需要沿最后外部渠道发提醒：`target: "last"`
- 备份冗余 `agent:<id>:main` 会话
- 从 live 会话索引中移除多余主会话
- 数据库中同步删除旧 heartbeat 会话记录

如果目标是“一个外部直聊窗口 + 暂时不需要 heartbeat”，可以用更简单的做法：

- 将 heartbeat 调整为 `every: "0m"`
- 保留真实外部直聊会话
- 清理冗余主会话

如果目标是“内部席位先占位、暂时没有外部入口”，更稳的做法是：

- 允许保留一个中文主会话
- heartbeat 可以关闭，或保留为单一内部主会话
- 不要再额外造第二个用户可见窗口

### 5. 同步数据库

如果当前系统已启用 PostgreSQL 索引层，则必须同步：

- `agent_runtime.agents`
- 必要的 `sessions`
- 资源索引与状态记录

没有完成数据库同步时，只能汇报“已建立 workspace 骨架”或“已建立可运行内部 agent（未同步数据库）”，不能直接说“已建立完整 agent”。

数据库口径见：

- [references/database-sync.md](references/database-sync.md)

### 6. 验收

创建完成后，必须对照验收清单逐项确认：

- 见 [references/acceptance-checklist.md](references/acceptance-checklist.md)

## 交付口径

汇报时只能用这三种结论：

- `已建立 workspace 骨架`
- `已建立可运行内部 agent`
- `已建立可运行 agent，并已绑定外部入口`

不要用含混表述。

## 当前环境约束

- 当前团队采用共享规则继承
- 优先复用：
  - `~/.openclaw/shared-rules/constitution.md`
  - `~/.openclaw/shared-rules/departments/*.md`
- 本 skill 自带可发布脚手架：
  - `scripts/scaffold_workspace.py`
  - `assets/templates/*.template`
- 初始化向导当前版只负责“瘦身版可运行 agent”
- 外部 bot 接入可在同一向导的第二阶段继续，但不应反过来跳过第一阶段

## 建议输出格式

完成一次创建后，按下面 7 项汇报：

1. 是否已加入 `openclaw agents.list`
2. 是否已建立独立 `agentDir`
3. 是否已建立 `sessions store`
4. 是否已配置 `heartbeat`
5. 是否已进入当前 live agent 列表
6. 是否已同步数据库
7. 当前还缺什么才能算完整可运行

如发现失败或半成品，必须明确写出失败点，不要把“失败”包装成“已建立”。

## 命名规则

- `agentId`：英文 / 拼音 / kebab-case
- `accountId`：英文 / 拼音 / ASCII
- 显示名：严格等于用户给出的中文名

不要把中文直接用作内部 `accountId`，除非已经验证该版本完全兼容。
