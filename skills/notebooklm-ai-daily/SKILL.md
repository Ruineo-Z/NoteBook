---
name: notebooklm-ai-daily
description: 用于执行 NotebookLM 的 AI 日报流水线：创建当日笔记本、按4类中文检索模板用 fast 模式导入来源、在同一对话中筛选出5条可用资讯、继续生成中文视频文案，并可选仅基于这5条来源生成 PPT。适用于用户提出“每日AI资讯/AI日报/NotebookLM检索筛选/视频文案或简报生成”等请求。
---

# NotebookLM AI Daily

## Overview

用一套固定流程完成每日 AI 资讯采集与内容产出，重点保证：
- 来源足够（按 4 类分开检索）
- 结果可控（强制 5 条 JSON）
- 对话连续（同一 conversation）

## Input Parameters

执行前先明确以下参数（未提供时按默认）：
- `DATE`: 默认今天（例如 `2026-02-12`）
- `WINDOW_START`: 默认 `DATE-1 00:00`
- `WINDOW_END`: 默认 `DATE 23:59`
- `LANGUAGE`: 默认 `zh_Hans`
- `TOP_N`: 固定 `5`

## Workflow

1. 校验 NotebookLM 状态
   - `notebooklm status`
   - 若未登录：`notebooklm login`

2. 创建当天笔记本
   - 命名：`AI日报-fast-YYYY-MM-DD`
   - 命令：`notebooklm create "AI日报-fast-<DATE>" --json`
   - 记录 `notebook_id`

3. 依次执行 4 个检索模板（fast）
   - 模板在 `references/search-templates-zh.md`
   - 每条模板单独执行：
     - `notebooklm source add-research "<query>" -n <notebook_id> --mode fast --no-wait`
     - `notebooklm research wait -n <notebook_id> --timeout 600 --import-all`

4. 核对来源状态（避免误读）
   - `notebooklm source list -n <notebook_id> --json`
   - 统计 `total / ready / error`
   - 不要把 ask 返回中的 `references` 数量当成来源总数

5. 在同一对话发起第一次 ask（筛选）
   - 不要用 `--new`
   - 首轮可直接：
     - `notebooklm ask -n <notebook_id> "<筛选提示词>" --json`
   - 拿到 `conversation_id` 后，后续必须带 `-c <conversation_id>`
   - 提示词模板见 `references/ask-prompts-zh.md`（要求只输出长度为 5 的 JSON）

6. 在同一对话发起第二次 ask（视频文案）
   - `notebooklm ask -n <notebook_id> -c <conversation_id> "<视频文案提示词>" --json`
   - 产出 90–120 秒中文介绍视频脚本

7. （可选）仅基于 5 条来源生成 PPT
   - 先把第 5 步 JSON 中的 `source_url` 映射到 `source_id`
   - 再执行：
     - `notebooklm generate slide-deck -n <notebook_id> -s <id1> -s <id2> -s <id3> -s <id4> -s <id5> --format presenter --length short --language zh_Hans --wait --json "基于这5条来源生成10页以内中文简报：概览-重点-趋势-结论"`
   - 下载：
     - `notebooklm download slide-deck -n <notebook_id> --latest ./reports/today-brief.pdf`

## Hard Constraints

- 时间窗用自然日：`WINDOW_START` 到 `WINDOW_END`（非滚动 24 小时）
- 首轮筛选 ask 必须输出：JSON 数组，长度严格等于 5
- 排除：向量/Embedding/向量数据库/纯检索基础设施、无发布时间、纯观点、二次搬运、营销软文
- 同一事件只保留一个主来源，优先官方或一手来源
- 所有后续 ask 必须在同一 `conversation_id` 中继续

## Deliverables

每次执行后至少输出：
- `notebook_id`
- `conversation_id`
- 来源统计（`total/ready/error`）
- 5 条筛选 JSON（含标题、时间、来源、价值、入选理由）
- 视频文案（90–120 秒）
