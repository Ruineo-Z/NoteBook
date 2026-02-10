## 输出格式规范（示例模板）

> 重要说明：
> 1. 本文件仅用于定义输出结构与字段，不是可直接交付内容。
> 2. 下方数字、段落名、时间范围均为示例，必须替换为当前歌曲真实数据。
> 3. 禁止直接照抄示例文本。

# {song_name} 结构分析报告

## 一、基础信息

- 音频文件：{audio_path}
- 歌曲名称：{song_name}
- 歌手：{artist}
- BPM：{bpm}
- 时长：{duration_mmss}

## 二、段落结构

| 段落 | 功能 | 行数 | 时间范围 |
|------|------|------|----------|
| Verse 1 | 叙事铺垫 | {line_count}行 | {start}-{end} |
| Pre-Chorus 1 | 情感累积 | {line_count}行 | {start}-{end} |
| Chorus 1 | 情感爆发 | {line_count}行 | {start}-{end} |

## 三、词格分析

### 各段音节模式
- Verse 1：{syllable_pattern}
- Chorus 1：{syllable_pattern}

### 押韵系统
- 韵脚：{ending_stats}
- 押韵模式：{rhyme_pattern_summary}

## 四、双信号判定记录

- 分段间隔阈值：LRC间隔 > (60/BPM)*4*2 秒
- 能量跳变阈值：RMS跳变 > 50%
- {segment_name} 起点：{判定结果}（间隔 {gap_seconds}s, RMS跳变 {jump_percent}%）

## 五、交接建议

分析阶段完成。请确认以上结构与词格统计。
确认后可进入下一步歌词创作（ziqi-lyricist）。
