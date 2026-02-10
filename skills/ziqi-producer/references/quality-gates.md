## 质量门禁清单（不通过不得交付）

### A. 输入完整性

- [ ] 已读取 `{song}-analysis.md`
- [ ] 已读取 `{song}-lyrics.txt`
- [ ] 已明确 BPM 与段落结构
- [ ] 已明确用户偏好（若用户提供）

### B. 结构合规（最高优先）

- [ ] 英文版包含 `[Suno Prompt]`
- [ ] 英文版包含 `[Style]`
- [ ] 英文版包含 `[Lead]`
- [ ] 英文版包含 `[Backing]`
- [ ] 英文版包含 `[Vocals]`
- [ ] 英文版包含 `[Structure]`
- [ ] 标签顺序正确且无缺失

### C. 格式安全

- [ ] 无 `Title:` / `Style Tags:` / `Prompt:`
- [ ] 无 `[Genre:]` / `[Instruments:]` / `[Emotion:]`
- [ ] 无 Markdown 标题（`##`）
- [ ] 无 Markdown 粗体标签式小标题（`**xxx:**`）
- [ ] 英文区块字符数 `<= 1000`

### D. 音乐一致性

- [ ] [Style] 与 BPM、情绪一致
- [ ] [Lead] 与 [Backing] 没有冲突（例如“极简”却写“密集层叠”）
- [ ] [Vocals] 与歌曲情绪推进一致
- [ ] [Structure] 体现段落能量变化，不是平铺描述
- [ ] 中文版与英文版语义一致

### E. 交付门禁

- [ ] 已执行格式校验脚本且返回 `success: true`
- [ ] 已向用户展示英中双版本
- [ ] 已获得用户明确确认
- [ ] 已保存 `{song}-arrangement.txt`
