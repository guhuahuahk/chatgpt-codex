---
name: openclaw-agent-builder
description: 为 OpenClaw 创建或补全新 agent 的标准技能。用于“建立新成员”“补全 agent 运行链”“把 workspace 骨架升级成可运行 agent”“检查 agent 是否创建完整”这类任务。按统一流程处理 workspace、agentDir、sessions、heartbeat、openclaw.json、渠道绑定、数据库同步与最终验收。
metadata:
  openclaw:
    emoji: "🧩"
---

# OpenClaw Agent Builder

把“创建一个 agent”当成正式交付，而不是只建几个文件。

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

## 标准流程

### 1. 先收最小输入

至少确认这些：

- 正式显示名
- 内部 `agentId`
- 所属部门
- 直接上级
- 当前阶段是否需要外部 bot / route

如未明确，优先做**内部 agent**，不要自动接外部入口。

### 2. 建立 workspace 骨架

优先用脚手架：

```bash
/Users/huahua/.openclaw/skills/openclaw-agent-builder/scripts/scaffold_workspace.sh --help
```

这一步只负责：

- `AGENTS.md`
- `IDENTITY.md`
- `HEARTBEAT.md`
- `MEMORY.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `memory/`

### 3. 建立运行层

至少补齐：

- `agents.list`
- 独立 `agentDir`
- 独立 `sessions store`
- `heartbeat`
- 需要时复制 `models.json` / `auth-profiles.json`

### 4. 需要渠道时再做绑定

规则：

- 一个 bot 默认只归一个 agent
- `accountId` 一律用英文 / 拼音 / ASCII
- 显示名可以用中文
- 未明确要求时，不要自动抢占现有默认渠道

### 5. 同步数据库

如果当前系统已启用 PostgreSQL 索引层，则必须同步：

- `agent_runtime.agents`
- 必要的 `sessions`
- 资源索引与状态记录

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

## 建议输出格式

完成一次创建后，按下面 7 项汇报：

1. 是否已加入 `openclaw agents.list`
2. 是否已建立独立 `agentDir`
3. 是否已建立 `sessions store`
4. 是否已配置 `heartbeat`
5. 是否已进入当前 live agent 列表
6. 是否已同步数据库
7. 当前还缺什么才能算完整可运行

## 命名规则

- `agentId`：英文 / 拼音 / kebab-case
- `accountId`：英文 / 拼音 / ASCII
- 显示名：中文

不要把中文直接用作内部 `accountId`，除非已经验证该版本完全兼容。
