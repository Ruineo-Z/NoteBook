---
name: ziqi-analyst
description: 用于分析一首歌的结构；基于音频与时间戳歌词识别段落（Verse/Pre-Chorus/Chorus/Bridge）、统计词格与押韵，并输出 {song}-analysis.md。
---

# 歌曲结构分析技能


## 目标

在通用 CLI 环境执行歌曲结构分析流程：提取音频特征、抓取时间戳歌词、应用双信号规则，并输出结构化分析报告。

保持“分析先行、创作后置”的边界，只做分析，不写新歌词。

## 核心原则

- 最终交付给用户的分析文本必须由 LLM 生成。
- 脚本只负责数据提取，不直接产出最终分析文案。
- 分析方法论以 `references/analyst-methodology.md` 为准。
- 输出结构以 `references/report-template.md` 为准；示例内容必须替换，禁止照抄。

## 何时触发

在以下请求触发本技能：
- “先分析这首歌结构，再写词”
- “给我 BPM、段落、词格、押韵分析”
- “生成 `{song}-analysis.md` 报告”

不在以下场景触发：
- 直接创作歌词
- 生成编曲提示词

## 输入输出契约

### 输入（必须）

- `audioPath`：音频绝对路径（mp3/wav/flac/m4a等）
- `songUrl`：网易云或QQ音乐链接（支持短链）

### 输出（固定）

- `{song}.features.csv`
- `{song}.features.meta.json`
- `{song}-lyrics.txt`
- `{song}-analysis.md`（LLM 生成的最终报告）

### 约束（必须遵守）

- 不主动扫描目录。
- 歌词源文件只读，不修改内容。
- 分析结果仅写入 `{song}-analysis.md`。
- 展示报告后必须向用户确认再交接。

## 执行流程

完整检查清单见 `references/workflow-checklist.md`。

### 步骤0：收集输入

询问并获取 `audioPath` 与 `songUrl`。
未收到完整输入时，不进入下一步。

### 步骤1：提取音频特征（脚本）

执行：

```bash
node skills/ziqi-analyst/scripts/extract_audio_features_cli.js   --audio /abs/path/song.mp3
```

### 步骤2：抓取时间戳歌词（脚本）

执行：

```bash
node skills/ziqi-analyst/scripts/fetch_lyrics_cli.js   --url "https://music.163.com/song?id=xxxx"   --output /abs/path/song-lyrics.txt
```

### 步骤3：生成最终分析报告（LLM）

- 必须加载并遵循：
  - `references/analyst-methodology.md`
  - `references/analysis-rules.md`
  - `references/report-template.md`
- 读取数据文件：
  - `{song}.features.csv`
  - `{song}.features.meta.json`
  - `{song}-lyrics.txt`
- 由 LLM 生成最终 `{song}-analysis.md`。

### 步骤4：确认与交接

向用户展示报告摘要并询问：

```text
请确认以上分析是否正确？
```

用户确认后交接：

```text
分析阶段完成！分析报告已生成：{song}-analysis.md
请激活 ziqi-lyricist 继续创作歌词。
```

## 质量门禁

交接前逐项检查：
- 特征文件存在且可读（csv + meta）
- 歌词文件为 `.txt` 且包含时间戳行
- 报告结构完整（见 `references/report-template.md`）
- 分段记录包含双信号依据（间隔 + RMS跳变）
- 行数、音节、押韵来自源歌词统计

## 异常处理

- 音频提取失败：校验路径/格式，确认本机 `ffmpeg` 可用，再重试。
- 歌词抓取失败：校验平台与链接格式；短链先展开；必要时让用户换链接。
- LLM 报告生成失败：保留中间文件，返回具体报错并停止后续步骤。

## 资源索引

- `references/analyst-methodology.md`：分析方法论与角色边界（Skill版）
- `references/workflow-checklist.md`：执行顺序与命令模板
- `references/analysis-rules.md`：双信号规则与段落判定
- `references/report-template.md`：输出格式规范与示例模板
- `scripts/extract_audio_features_cli.js`：音频特征提取
- `scripts/fetch_lyrics_cli.js`：歌词抓取

## 禁止越界

不要执行：
- 歌词创作
- 编曲提示词生成
- 对源歌词做改写或润色
