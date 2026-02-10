## 输出格式规范（示例模板）

> 重要说明：
> 1. 本文件只定义输出结构，不是可直接交付内容。
> 2. 示例中的风格、乐器、人声、句子均为占位，必须替换为本次真实结果。
> 3. 禁止直接照抄示例文本。

```text
【编曲提示词 - 英文版】（用于 Suno）

[Suno Prompt]

[Style]
{style_prompt}

[Lead]
{lead_prompt}

[Backing]
{backing_prompt}

[Vocals]
{vocals_prompt}

[Structure]
{structure_prompt}

---

【编曲提示词 - 中文版】（便于理解）

[风格]
{style_cn}

[主奏]
{lead_cn}

[伴奏]
{backing_cn}

[人声]
{vocals_cn}

[结构]
{structure_cn}

请确认编曲提示词是否满意？
```

### 必须满足

- 英文区块使用 `[Style]/[Lead]/[Backing]/[Vocals]/[Structure]` 五部分结构
- 英文区块字符数 `<= 1000`
- 不出现 `Title:`、`Prompt:`、`[Genre:]` 等禁用格式
- 中文版与英文版语义一致
