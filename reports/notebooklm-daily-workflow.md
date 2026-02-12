# NotebookLM 每日执行流程（V2）

> 目标：每天固定产出可用于 PPT 的 5 条精选来源。

## 步骤 1：创建当天笔记本

命名建议：`AI日报-fast-YYYY-MM-DD`

```bash
notebooklm create "AI日报-fast-2026-02-12" --json
```

记录返回的 `notebook.id`，后续命令都带 `-n <notebook_id>`。

---

## 步骤 2：按 4 个模板依次检索并导入来源（fast）

每个分类单独执行一次（避免单次检索上限影响召回）：

```bash
notebooklm source add-research "<新模型模板>" -n <notebook_id> --mode fast --no-wait
notebooklm research wait -n <notebook_id> --timeout 600 --import-all

notebooklm source add-research "<新Agent模板>" -n <notebook_id> --mode fast --no-wait
notebooklm research wait -n <notebook_id> --timeout 600 --import-all

notebooklm source add-research "<实用工具/Skill模板>" -n <notebook_id> --mode fast --no-wait
notebooklm research wait -n <notebook_id> --timeout 600 --import-all

notebooklm source add-research "<AIGC模板>" -n <notebook_id> --mode fast --no-wait
notebooklm research wait -n <notebook_id> --timeout 600 --import-all
```

说明：
- 总来源不一定是 40（会跨分类去重）。
- 允许少量 `error` 来源（网络/站点限制）。

---

## 步骤 3：在“当前对话”中 ask（不要新建会话）

先查当前对话 ID：

```bash
notebooklm history -n <notebook_id> -l 5
```

然后在当前对话继续提问（关键：`-c`，不要 `--new`）：

```bash
notebooklm ask -n <notebook_id> -c <conversation_id> "<强制输出5条JSON的筛选提示词>"
```

### 筛选提示词要点（硬约束）
- 时间窗：`2026-02-11 00:00` 到 `2026-02-12 23:59`（按你定义的自然日范围）
- 类别：新模型 / 新Agent / 实用工具Skill / AIGC
- 排除：向量模型、Embedding、向量数据库/检索基础设施、无发布时间、纯观点、二次搬运、营销软文
- 去重：同一事件只保留一个主来源
- 输出：**只输出 JSON 数组，长度必须为 5**

---

## 步骤 4：将 5 条结果映射为 source_id

PPT 生成使用的是 `source_id`，不是 URL。先导出来源列表：

```bash
notebooklm source list -n <notebook_id> --json
```

把第 3 步返回的 5 个 `source_url`，逐一匹配为对应 `source_id`。

---

## 步骤 5：只基于这 5 个来源生成 PPT

```bash
notebooklm generate slide-deck \
  -n <notebook_id> \
  -s <source_id_1> -s <source_id_2> -s <source_id_3> -s <source_id_4> -s <source_id_5> \
  --format presenter \
  --length short \
  --language zh_Hans \
  --wait \
  --json \
  "基于这5条来源生成10页以内中文简报：概览-重点-趋势-结论"
```

---

## 步骤 6：下载 PPT

```bash
notebooklm download slide-deck -n <notebook_id> --latest ./reports/today-brief.pdf
```

---

## 本次实测参数（2026-02-12）

- 笔记本：`AI日报-fast-2026-02-12`
- Notebook ID：`de495eb7-72b0-481c-93e6-d94a0e9b1df5`
- 当前对话 ID：`4c62c46b-4322-45ef-b08a-74a2948e2130`
- 已确认：使用 `ask -c <conversation_id>` 才符合“页面只看当前对话”的方式
