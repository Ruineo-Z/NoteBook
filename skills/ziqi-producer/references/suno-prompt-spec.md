## Suno 编曲提示词规范（Skill版）

### 1. 唯一允许的英文结构

```text
[Suno Prompt]

[Style]
...

[Lead]
...

[Backing]
...

[Vocals]
...

[Structure]
...
```

说明：
- 以上标签名称必须原样使用
- 标签顺序固定，不可调整
- 每个标签下至少 1 行有效内容

### 2. 中文解释结构（用于给用户确认）

```text
[风格]
...

[主奏]
...

[伴奏]
...

[人声]
...

[结构]
...
```

说明：
- 中文版必须与英文版逐段对齐
- 中文版只做解释，不做独立改写

### 3. 禁止格式

以下格式禁止出现（任一命中即不合格）：

- `Title:`
- `Style Tags:`
- `Prompt:`
- `[Genre:]`
- `[Instruments:]`
- `[Emotion:]`
- `## 标题`（Markdown 标题）
- `**Style Prompts:**`（Markdown 粗体标签）

### 4. 字符限制

- 只统计英文 `[Suno Prompt]` 区块字符数
- 该区块总字符数必须 `<= 1000`

### 5. 内容建议

- [Style]：风格 + 情绪 + BPM 区间
- [Lead]：主导乐器 + 演奏手法 + 段落差异
- [Backing]：铺底层 + 节奏层 + 厚度变化
- [Vocals]：音色 + 唱法 + 情绪释放方式
- [Structure]：能量曲线 + 对比 + 高潮 + 收束

### 6. 校验命令

```bash
node skills/ziqi-producer/scripts/validate_arrangement_prompt.js --file /abs/path/{song}-arrangement.txt
```

返回 `"success": true` 才可进入交付环节。
