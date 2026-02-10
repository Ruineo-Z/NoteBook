---
name: ziqi-producer
description: 用于基于分析报告与歌词生成 Suno 五部分编曲提示词；按 [Style]/[Lead]/[Backing]/[Vocals]/[Structure] 输出英中双版本，校验通过后保存为 {song}-arrangement.txt。
---

# 编曲提示词生成技能


## 目标

在分析报告与歌词已完成的前提下，生成可直接用于 Suno 的编曲提示词（英文版）和解释版（中文版）。

保持“编曲提示词生成”边界：
- 负责结构化编曲提示词设计与校验
- 不修改歌词，不回退重做结构分析

## 触发条件

在以下请求触发本技能：
- “根据分析报告和歌词生成编曲提示词”
- “输出 Suno 用的 arrangement prompt”
- “生成 `{song}-arrangement.txt`”

不在以下场景触发：
- 音频结构分析
- 歌词创作或改词

## 输入输出契约

### 输入（必须）

- `{song}-analysis.md`（BPM、结构、风格线索）
- `{song}-lyrics.txt`（段落结构、情绪推进）
- 用户偏好（可选：性别声线、乐器倾向、年代感）

### 输出（固定）

- 可展示草稿：英中双版本编曲提示词
- 最终文件：`{song}-arrangement.txt`

### 强约束

- 英文版必须使用五部分结构：`[Style] [Lead] [Backing] [Vocals] [Structure]`
- 英文版 `[Suno Prompt]` 区块总字符数必须 `<= 1000`
- 禁止 `Title:`、`Prompt:`、`[Genre:]`、Markdown 标题等格式
- 最终交付文案由 LLM 生成；脚本仅做格式硬校验

## 任务执行协议（必须）

使用本技能时，必须先建立任务，再按任务推进：

1. 创建父任务：`{song} 编曲提示词任务`
2. 按 `references/task-protocol.md` 建立固定子任务
3. 同时仅允许 1 个 `in_progress` 子任务
4. 用户要求调整时，在同一父任务追加修订子任务（如 `P4-R2`、`P5-R2`）
5. 仅在用户明确确认终版后，完成父任务并保存文件

## 执行流程

完整流程见 `references/workflow-checklist.md`。

### 步骤0：读取输入与边界确认

- 读取分析报告，提取 BPM、段落结构、风格关键词
- 读取歌词，提取段落能量走向（Verse -> Pre-Chorus -> Chorus -> Bridge -> Final Chorus）
- 确认本阶段不改歌词正文

### 步骤1：确定编曲设计约束

必须加载：
- `references/producer-methodology.md`
- `references/suno-prompt-spec.md`

产出：
- 风格方向
- 乐器层次设计
- 人声设计
- 段落动态曲线

### 步骤2：LLM 生成编曲提示词终稿

必须加载：
- `references/arrangement-output-template.md`
- `references/quality-gates.md`

说明：
- `arrangement-output-template.md` 只定义输出格式，禁止照抄示例文本
- 英文版与中文版语义应保持一致

### 步骤3：格式硬校验（脚本）

先将草稿写入临时文件，再执行：

```bash
node skills/ziqi-producer/scripts/validate_arrangement_prompt.js --file /abs/path/{song}-arrangement-draft.txt
```

校验失败时：
- 回到步骤2修订
- 重新校验直至通过

### 步骤4：展示、确认、保存

1. 展示英中双版本并请求用户确认
2. 用户确认后保存为 `{song}-arrangement.txt`
3. 给出完成说明并标记父任务完成

## 资源索引

- `references/task-protocol.md`：任务创建与修订协议
- `references/workflow-checklist.md`：步骤清单与执行顺序
- `references/producer-methodology.md`：编曲提示词方法论
- `references/suno-prompt-spec.md`：Suno 五部分结构与禁用格式
- `references/arrangement-output-template.md`：输出结构示例（禁止照抄）
- `references/quality-gates.md`：交付前质量门禁
- `scripts/validate_arrangement_prompt.js`：格式校验脚本

## 禁止越界

不要执行：
- 修改或重写歌词内容
- 回退到分析阶段重做结构识别
- 直接交付未通过校验的提示词
- 将模板示例原样当作最终结果
