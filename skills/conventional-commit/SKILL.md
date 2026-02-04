---
name: conventional-commit
description: 创建符合 Conventional Commits 规范的 git commit 与 commit message。用户要求“提交代码”“写 commit message”“按 Conventional Commits 提交”或需要检查变更、确认后执行 git commit 时使用。包含 .gitignore 检查、变更分析、中文祈使语 commit message 生成与确认流程，并禁止自动 push/pull/merge/rebase。
---

# Conventional Commit

## Overview
规范化生成 Conventional Commits 提交信息，并在确认后执行 `git commit`。

## Workflow

### 1) Check .gitignore
- 检查项目根目录是否存在 `.gitignore`。
- 若不存在，明确警告并停止后续操作，询问是否继续；未确认前不要继续。

### 2) Analyze changes
运行并阅读以下信息：
- `git status`
- `git diff --cached`
- `git diff`
- `git log --oneline -5`

### 3) Staging rules
- 若暂存区为空，先询问用户需要暂存哪些文件。
- 根据用户选择使用 `git add -A` 或 `git add <文件>`。
- 依赖 `.gitignore` 自动忽略规则，不要手动排除以 `.` 开头的文件或目录。

### 4) Generate commit message
使用 Conventional Commits 格式：

```
<type>[可选作用域]: <描述>

[可选正文]

[可选脚注]
```

**Type 选项**（择一）：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`chore`、`ci`。

**格式要求**：
- 使用中文描述
- 祈使语气
- 描述以小写字母开头
- 简洁明了，<= 72 字符

### 5) Show and confirm
- 展示变更文件列表与完整 commit message。
- 询问是否确认提交。

### 6) Commit only after confirmation
- 仅在用户明确确认后执行：`git commit -m "<message>"`。
- 若用户不确认，不执行任何 git 操作。

## Hard constraints
- 禁止自动执行 `git push` / `git pull` / `git merge` / `git rebase` / 任何分支操作。
- 若无变更，明确告知当前没有需要提交的内容。
