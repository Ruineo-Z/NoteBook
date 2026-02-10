## 子期分析师工作清单（LLM终稿版）

### 步骤0：输入收集

只收集两个输入：
- `audioPath`：音频绝对路径
- `songUrl`：网易云/QQ 歌曲链接

约束：
- 不主动扫描目录。
- 未拿到两个输入前，不进入后续步骤。

---

### 步骤1：音频特征提取（脚本）

执行命令：

```bash
node skills/ziqi-analyst/scripts/extract_audio_features_cli.js   --audio /abs/path/song.mp3
```

产物（与音频同目录）：
- `{song}.features.csv`
- `{song}.features.meta.json`

说明：
- 需要系统安装 `ffmpeg`。
- 默认每 5 秒采样一次 RMS。

---

### 步骤2：歌词抓取（脚本）

执行命令：

```bash
node skills/ziqi-analyst/scripts/fetch_lyrics_cli.js   --url "https://music.163.com/song?id=xxxx"   --output /abs/path/{song}-lyrics.txt
```

产物：
- `{song}-lyrics.txt`

说明：
- 输出必须是 `.txt`。
- 内容格式：歌名、歌手、空行、带时间戳歌词。

---

### 步骤3：最终报告生成（LLM）

1. 强制加载并遵循：
   - `references/analyst-methodology.md`
   - `references/analysis-rules.md`
   - `references/report-template.md`
2. 基于以下数据文件，由 LLM 生成最终报告：
   - `{song}.features.csv`
   - `{song}.features.meta.json`
   - `{song}-lyrics.txt`
3. 将最终报告写入：
   - `/abs/path/{song}-analysis.md`

---

### 步骤4：用户确认与交接

确认文案：

```text
请确认以上分析是否正确？
```

交接文案：

```text
分析阶段完成！分析报告已生成：{song}-analysis.md
请激活 ziqi-lyricist 继续创作歌词。
```
