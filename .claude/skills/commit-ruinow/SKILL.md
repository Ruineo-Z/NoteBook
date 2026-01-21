---
name: commit-ruinow
description: 此技能用于创建符合 Conventional Commits 规范的 git commit。当用户需要提交代码变更、创建 commit 时使用此技能。技能会严格分析分支变更内容，生成规范的 commit message，并在用户确认后才执行提交。
---

# Git Commit 技能

## 概述

此技能帮助创建符合 Conventional Commits 规范的 git commit。技能会自动分析当前分支的所有变更，生成规范的 commit message，并在用户明确确认后才执行提交操作。

## 工作流程

### 第一步：确认分支状态

#### 1.1 获取远程最新状态

```bash
# 从远程仓库获取最新信息（不合并）
git fetch origin
```

#### 1.2 检查分支状态

```bash
# 查看当前分支名称
git branch --show-current

# 查看分支与远程的同步状态（领先/落后多少提交）
git status -sb

# 查看本地与远程的差异
git log --oneline HEAD..origin/$(git branch --show-current) 2>/dev/null || echo "无远程跟踪分支"

# 查看最近的 commit 历史
git log --oneline -5
```

#### 1.3 向用户展示状态并确认

```
## 分支状态

- 当前分支: feature/user-auth
- 远程跟踪: origin/feature/user-auth
- 同步状态: 本地领先 2 个提交，落后 1 个提交
- 最近本地提交:
  - abc1234 feat(api): 添加用户认证接口
  - def5678 refactor(auth): 重构认证逻辑
- 未拉取的远程提交:
  - ghi9012 fix(auth): 修复登录问题

⚠️ 警告: 远程有未拉取的提交，建议先执行 git pull 合并远程变更

是否在此分支上继续提交？(继续/先拉取远程变更/取消)
```

#### 1.4 处理远程变更

如果检测到远程有未拉取的提交：
- **建议用户先拉取**：提示执行 `git pull` 或 `git pull --rebase`
- **用户选择继续**：警告可能产生合并冲突，但允许继续
- **用户选择取消**：终止提交流程

**必须**等待用户确认分支状态正确后才能继续。

### 第二步：分析变更内容

执行以下命令收集变更信息：

```bash
# 查看工作区状态（不使用 -uall 标志）
git status

# 查看已暂存的变更
git diff --cached

# 查看未暂存的变更
git diff
```

### 第三步：生成 Commit Message

根据变更内容，按照 Conventional Commits 规范生成 commit message。

#### Commit Message 格式

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

#### 类型标签（type）

| 类型 | 说明 | 示例场景 |
|------|------|----------|
| `feat` | 新功能 | 添加新的 API 端点、新的用户界面功能 |
| `fix` | 修复 bug | 修复登录失败、修复数据显示错误 |
| `docs` | 文档变更 | 更新 README、添加 API 文档 |
| `style` | 代码格式（不影响代码运行） | 格式化代码、删除空白行 |
| `refactor` | 重构（既不是新功能也不是修复 bug） | 重命名变量、提取函数 |
| `perf` | 性能优化 | 优化查询速度、减少内存使用 |
| `test` | 添加或修改测试 | 添加单元测试、修复测试用例 |
| `chore` | 构建过程或辅助工具的变动 | 更新依赖、修改配置文件 |
| `ci` | CI 配置变更 | 修改 GitHub Actions、更新部署脚本 |
| `build` | 构建系统或外部依赖变更 | 修改 webpack 配置、更新 npm 包 |
| `revert` | 回滚之前的 commit | 回滚某个功能 |

#### Scope（可选）

scope 用于说明 commit 影响的范围，例如：
- `feat(api)`: API 相关的新功能
- `fix(auth)`: 认证模块的修复
- `docs(readme)`: README 文档更新

#### Subject 规则

- 使用祈使句，现在时态（"add" 而不是 "added" 或 "adds"）
- 首字母小写
- 结尾不加句号
- 简洁明了，不超过 50 个字符

#### Body（可选）

- 解释变更的动机和与之前行为的对比
- 使用祈使句，现在时态
- 每行不超过 72 个字符

### 第四步：向用户确认

**必须**在执行 commit 之前向用户展示以下信息并获得确认：

1. **变更文件列表**：列出所有将被提交的文件
2. **变更摘要**：简要说明每个文件的变更内容
3. **生成的 Commit Message**：完整展示将要使用的 commit message
4. **询问确认**：明确询问用户是否确认提交

示例确认格式：

```
## 变更分析

### 变更文件
- src/api/user.py (新增)
- src/models/user.py (修改)
- tests/test_user.py (新增)

### 变更摘要
- 新增用户 API 端点，支持用户注册和登录
- 在 User 模型中添加了 email 验证字段
- 添加了用户相关的单元测试

### Commit Message
feat(api): 添加用户注册和登录功能

- 新增 /api/user/register 和 /api/user/login 端点
- User 模型添加 email_verified 字段
- 添加相关单元测试

---
是否确认提交？(确认/取消/修改)
```

### 第五步：执行提交

只有在用户明确确认后才执行以下操作：

```bash
# 添加变更到暂存区（根据用户确认的文件）
git add <files>

# 执行 commit（使用 HEREDOC 确保格式正确）
git commit -m "$(cat <<'EOF'
<commit message>
EOF
)"

# 验证提交成功
git status
```

## 重要约束

1. **禁止自动提交**：必须在用户确认后才能执行 `git commit`
2. **禁止强制推送**：不执行 `git push --force` 或类似危险操作
3. **禁止修改 git 配置**：不执行 `git config` 命令
4. **禁止跳过钩子**：不使用 `--no-verify` 或 `--no-gpg-sign` 标志
5. **严格遵循规范**：commit message 必须符合 Conventional Commits 规范

## 特殊情况处理

### 没有变更时
如果工作区没有任何变更，告知用户没有需要提交的内容。

### 包含敏感文件时
如果检测到可能包含敏感信息的文件（如 `.env`、`credentials.json` 等），警告用户并建议不要提交这些文件。

### 用户要求修改时
如果用户对生成的 commit message 不满意，根据用户反馈修改后重新确认。

### Pre-commit 钩子失败时
如果 commit 因为 pre-commit 钩子失败，分析失败原因，修复问题后创建新的 commit（不使用 `--amend`）。
