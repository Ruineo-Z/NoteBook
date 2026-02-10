## 歌词标签规范（Suno格式）

### 1) 结构标签（推荐）

| 段落类型 | 标签格式 | 说明 |
|---|---|---|
| 主歌 | `[Verse 1]`, `[Verse 2]` | 普通段落 |
| 预副歌 | `[Pre-Chorus - Gradual Build Up]` | 必须包含能量标签 |
| 副歌 | `[Chorus - Powerful & Emotional]` | 必须包含爆发标签 |
| 副歌中段 | `[Keep Power]` | Chorus 超过 3 句时插入 |
| 桥段 | `[Bridge - Silence]` 或 `[Bridge - Building]` | 对比/转折 |
| 最终副歌 | `[Final Chorus - Soaring High]` | 必须包含超越标签 |
| 尾段 | `[Outro]` | 结束段 |

### 2) 允许的能量控制标签

- `(Build-up)`
- `(Crescendo)`
- `(Diminuendo)`
- `(Explosion)`
- `(Stop)`
- `(Silence)`
- `(pause)`

### 3) 禁止格式

- `## Verse 1`（Markdown 标题）
- `(Verse 1)`（圆括号段落标签）
- `**Verse 1**`（加粗标题）
- `[00:15.50]`（LRC 时间戳）

### 4) 最终检查

- 所有段落标签使用方括号
- 标签与分析报告段落结构一致
- 无任何时间戳格式残留
