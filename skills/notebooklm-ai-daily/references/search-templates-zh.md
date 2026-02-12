# NotebookLM 检索模板（中文，4分类）

> 用法：每次单独执行一条，避免单次检索结果上限影响召回。  
> 日期占位符：`{START_DATE}`、`{END_DATE}`。

## 1) 新模型发布

请检索 {START_DATE} 到 {END_DATE} 之间发布的 AI 新模型或模型升级信息（不限厂商），重点关注：大语言模型、多模态、视觉、语音、AIGC 生成模型。排除：向量模型、Embedding 模型、向量数据库相关更新。优先来源：官方公告、发布说明、研究页面、GitHub Release。过滤掉无明确发布时间、纯观点和二次搬运内容。

## 2) 新 Agent

请检索 {START_DATE} 到 {END_DATE} 之间发布的 AI Agent 相关更新，包括：通用 Agent、编程 Agent、Computer Use Agent、Agent 框架与自动化工作流。排除仅涉及向量/Embedding 的更新（除非与重大 Agent 发布直接相关）。优先来源：官方文档、官方公告、GitHub Release。

## 3) 实用工具 / Skill

请检索 {START_DATE} 到 {END_DATE} 之间发布的实用 AI 工具/技能更新，重点关注内容创作与自动化工作流（如视频生成、设计、代码、生产力工具，例如 Remotion、Pencil）。排除向量数据库与 Embedding-only 更新，排除纯营销软文。

## 4) AIGC 相关

请检索 {START_DATE} 到 {END_DATE} 之间的 AIGC 更新，重点关注图像、视频、音频、多模态生成模型与可落地工作流。排除：向量/Embedding 模型更新、检索基础设施类更新。仅保留有明确发布时间和来源链接的内容。
