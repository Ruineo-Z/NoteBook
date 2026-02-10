---
name: ziqi-lyricist
description: 用于基于分析报告创作一首新歌词；先做情感提炼、禁用清单、意象检索与手法分配，再由LLM按固定Suno标签结构生成歌词并通过质量门禁。
---

# 歌词创作技能


## 目标

在分析报告已完成的前提下，完成“主题-词眼驱动”的歌词创作流程。

保留高质量约束：
- 结构严格对齐分析报告
- 意象先行（先检索再创作）
- 最终歌词由 LLM 生成

## 触发条件

在以下请求触发本技能：
- “根据这份分析报告写新歌词”
- “生成 demo 级歌词（Suno格式）”
- “按段落结构和词眼写词”

不在以下场景触发：
- 音频结构分析
- 编曲提示词生成

## 输入输出契约

### 输入（必须）

- `{song}-analysis.md`（分析报告）
- 原歌词文本（仅用于提取禁用清单）
- 用户主题（必填）
- 用户词眼（必填，3-6字）
- 情感线索（可选）

### 输出（固定）

- 终版歌词文本（Suno标签格式）
- 用户确认后保存为 `{song}-lyrics.txt`

### 强约束

- 段落数量、顺序、行数必须与分析报告一致。
- 禁止使用时间戳格式输出歌词。
- 禁止未检索意象就直接创作。
- 自检不通过不得展示。

## 任务执行协议（必须）

使用本技能时，必须先建立任务，再按任务推进：

1. 创建一个父任务：`{song} 歌词创作任务`。
2. 按 `references/task-protocol.md` 建立 10 个子任务（对应步骤1-10）。
3. 每次只执行一个 `in_progress` 子任务，完成后标记 `completed` 再进入下一步。
4. 用户提出修改意见时，不新建父任务；在同一父任务下新增“修订轮次子任务”（如 `步骤7-R2`、`步骤8-R2`）并继续迭代。
5. 只有当用户明确“确认最终版本”后，才可完成父任务并进入交接。

> 目的：让用户在同一任务中进行多轮微调，直到确认最终结果。

## 执行流程

完整流程见 `references/workflow-checklist.md`（保持原角色 1-10 步结构，并映射到任务）。

### 步骤0：读取输入与结构约束

- 读取分析报告，锁定段落结构与行数。
- 读取原歌词，仅用于禁用清单提取。

### 步骤1：情感提炼 + 禁用清单

- 按“四问法”提炼核心情感。
- 输出 8 类禁用清单并向用户确认。

### 步骤2：收集主题与词眼

- 主题和词眼必须由用户提供。
- 词眼长度控制在 3-6 字。

### 步骤3：检索本地意象库（必须）

执行：

```bash
node skills/ziqi-lyricist/scripts/query_imagery_local.js --action list
node skills/ziqi-lyricist/scripts/query_imagery_local.js --action query --category 思念 --limit 120
```

然后基于词眼风格筛选意象。

### 步骤4：分配表现手法

参考 `references/emotion-techniques.md`：
- 主要手法 1-2 种
- 辅助手法 1-2 种
- 按段落分配手法

### 步骤5：LLM 生成歌词终稿

必须加载并遵循：
- `references/lyricist-methodology.md`
- `references/blacklists.md`
- `references/lyric-tags.md`
- `references/lyric-output-template.md`
- `references/quality-gates.md`

说明：
- `lyric-output-template.md` 只是格式示例，禁止照抄示例文本。

### 步骤6：质量门禁与交付

1. 先做格式硬校验：

```bash
node skills/ziqi-lyricist/scripts/validate_lyrics_output.js --file /abs/path/{song}-lyrics.txt
```

2. 再做语义门禁（`quality-gates.md`）。
3. 全部通过后展示给用户。
4. 用户确认后保存为 `{song}-lyrics.txt`，并交接 `ziqi-producer`。

## 资源索引

- `references/task-protocol.md`：任务创建与多轮修订协议
- `references/lyricist-methodology.md`：方法论与硬约束
- `references/workflow-checklist.md`：步骤清单
- `references/emotion-techniques.md`：情感类型与手法映射
- `references/blacklists.md`：禁用词/禁用意象
- `references/lyric-tags.md`：Suno 标签规范
- `references/lyric-output-template.md`：输出格式示例（禁止照抄）
- `references/quality-gates.md`：交付前自检
- `scripts/query_imagery_local.js`：本地意象检索
- `scripts/validate_lyrics_output.js`：歌词格式校验

## 禁止越界

不要执行：
- 自行分析音频结构
- 生成编曲提示词
- 绕过用户输入直接决定主题/词眼
- 将模板示例原样作为结果交付
