---
name: api-test-generator
description: 此技能用于生成完整的 API 测试文档和 pytest 测试脚本。当需要分析项目接口、梳理测试点、生成测试文档和创建可执行测试脚本时使用此技能。支持 XMind 思维导图格式输出，便于直观查看测试用例层级结构。采用双 AI 审核机制（Claude Code 生成，Codex 审核）确保质量和覆盖度。
---

# API 测试生成器

## 概述

此技能通过四阶段工作流自动生成 API 测试产物：
1. 接口分析 - 理解项目接口和功能
2. 测试点梳理 - 提取全面的测试场景
3. 测试文档生成 - 创建结构化测试文档
4. 测试脚本生成 - 生成可执行的 pytest + httpx 脚本

每个阶段采用双 AI 审核机制：Claude Code 生成，Codex 审核，自动修复重试（最多 3 轮）。

## 前置条件

- Python 3.8+
- 已安装 pytest 和 httpx（`pip install pytest httpx`）
- 已安装 xmind（`pip install xmind`）- 用于生成思维导图
- 已配置 Codex CLI（用于审核功能）
- 项目包含 RESTful API 接口

## 工作流程

### 阶段 1：接口分析

**目标：** 识别所有 API 接口、请求方法、参数和业务逻辑。

**步骤：**
1. 扫描项目中的路由定义（FastAPI、Flask、Django 等）
2. 提取接口信息：
   - HTTP 方法（GET、POST、PUT、DELETE、PATCH）
   - URL 路径和路径参数
   - 查询参数和请求体结构
   - 响应模型和状态码
   - 认证要求
3. 记录业务逻辑和接口间的依赖关系

**输出：** `analysis/api_inventory.md` - 完整的接口清单

**Codex 审核提示词：**
```
审核此 API 分析文档的完整性。检查：
1. 代码库中是否有遗漏的接口？
2. HTTP 方法或路径是否正确？
3. 是否有遗漏的请求/响应参数？
4. 认证要求是否已记录？
返回 JSON：{"passed": bool, "issues": [...], "suggestions": [...]}
```

### 阶段 2：测试点梳理

**目标：** 为每个接口生成全面的测试场景。

**需覆盖的测试类别：**

| 类别 | 示例 |
|------|------|
| 正常流程 | 有效输入、预期响应 |
| 输入验证 | 缺失字段、无效类型、边界值 |
| 错误处理 | 400、401、403、404、500 场景 |
| 边界情况 | 空数组、null 值、最大长度 |
| 安全测试 | SQL 注入、XSS、认证绕过尝试 |
| 业务逻辑 | 状态转换、数据一致性 |

**输出：** `analysis/test_points.md` - 结构化测试点列表

**Codex 审核提示词：**
```
审核此 API 的测试点覆盖度。检查：
1. 每个接口是否覆盖了正常流程？
2. 是否识别了错误情况（4xx、5xx）？
3. 边界情况和边界条件？
4. 是否包含安全测试场景？
5. 业务逻辑验证测试？
返回 JSON：{"passed": bool, "coverage_score": 0-100, "missing": [...]}
```

### 阶段 3：测试文档生成

**目标：** 从测试点创建正式的测试文档。

**文档结构：**
- 使用 `assets/test_document_template.md` 中的模板
- 每个测试用例包含：编号、描述、前置条件、步骤、预期结果、优先级

**输出：** `docs/test_document.md` - 正式测试文档

**XMind 输出：** 同时生成 `docs/test_cases.xmind` - 思维导图格式的测试用例

**Codex 审核提示词：**
```
审核测试文档质量。检查：
1. 是否包含阶段 2 的所有测试点？
2. 测试步骤是否清晰可复现？
3. 预期结果是否具体（非模糊描述）？
4. 优先级分配是否合理？
5. 格式是否一致？
返回 JSON：{"passed": bool, "issues": [...], "completeness": 0-100}
```

### 阶段 4：测试脚本生成

**目标：** 生成可执行的 pytest 脚本。

**⚠️ 用户确认：数据策略选择**

在生成测试脚本前，必须询问用户选择数据策略：

```
请选择测试数据策略：

1. 真实数据（集成测试）
   - 直接调用真实 API
   - 需要启动服务
   - 适合：Agent 服务、端到端验证、验收测试

2. Mock 数据（单元测试）
   - 使用 pytest-mock 模拟 API 响应
   - 不需要启动服务
   - 适合：CI/CD 流水线、快速反馈、隔离测试

3. 两者都生成
   - 生成两套测试文件
   - tests/unit/ - Mock 测试
   - tests/integration/ - 集成测试
```

**根据用户选择生成不同的脚本：**

| 策略 | 输出目录 | 特点 |
|------|----------|------|
| 真实数据 | `tests/` | httpx.AsyncClient 直接调用 API |
| Mock 数据 | `tests/unit/` | 使用 @patch 或 pytest-mock |
| 两者都生成 | `tests/unit/` + `tests/integration/` | 分别生成两套 |

**脚本要求：**
- 使用 pytest fixtures 进行 setup/teardown
- 真实数据模式：使用 httpx.AsyncClient 进行 API 调用
- Mock 数据模式：使用 pytest-mock 或 respx 模拟响应
- 包含状态码和响应体的正确断言
- 按接口或功能组织测试
- 需要时包含测试数据工厂

**输出：** `tests/` 目录下的 pytest 脚本（结构取决于用户选择）

**Codex 审核提示词：**
```
代码审查这些 pytest 脚本。检查：
1. 断言是否具体且正确？
2. 测试隔离是否保持（无共享状态）？
3. 测试中的错误处理是否正确？
4. fixtures 使用是否恰当？
5. 测试是否与测试文档匹配？
返回 JSON：{"passed": bool, "code_issues": [...], "suggestions": [...]}
```

## 审核机制

### 双 AI 审核流程

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Claude Code │ ──▶ │   Codex     │ ──▶ │    结果     │
│    生成     │     │    审核     │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
              ┌───────────┐
              │  通过？   │
              └─────┬─────┘
                    │
         ┌─────────┴─────────┐
         ▼                   ▼
    ┌─────────┐         ┌─────────┐
    │   是    │         │   否    │
    │  下一   │         │  修复   │
    │  阶段   │         │  重试   │
    └─────────┘         └────┬────┘
                             │
                      (最多 3 轮)
```

### 调用 Codex 审核

使用 collaborating-with-codex 技能调用 Codex 进行审核：

```bash
python .claude/skills/collaborating-with-codex/scripts/codex_bridge.py \
  --cd "/项目路径" \
  --PROMPT "审核提示词" \
  --return-all-messages
```

### 处理审核失败

当 Codex 返回 `"passed": false` 时：
1. 解析响应中的问题列表
2. 对生成的产物进行修复
3. 重新提交审核
4. 如果 3 轮后仍失败，输出当前状态并附带警告

## 输出结构

完成后生成以下产物：

```
project/
├── analysis/
│   ├── api_inventory.md      # 阶段 1 输出
│   ├── test_points.md        # 阶段 2 输出
│   └── test_points.json      # 阶段 2 输出 (JSON 格式，用于生成 XMind)
├── docs/
│   ├── test_document.md      # 阶段 3 输出 (Markdown 表格)
│   └── test_cases.xmind      # 阶段 3 输出 (XMind 思维导图)
└── tests/
    ├── conftest.py           # 共享 fixtures
    ├── test_auth.py          # 认证接口测试
    ├── test_users.py         # 用户接口测试
    └── ...                   # 其他接口测试
```

## XMind 思维导图

### 结构说明

XMind 文件采用以下层级结构展示测试用例：

```
API 测试用例
├── 📦 用户管理模块
│   ├── 🔗 POST /api/users
│   │   ├── ✅ 正常流程
│   │   │   └── 🔴 TC-001: 创建用户成功
│   │   ├── ❌ 错误处理
│   │   │   ├── 🟠 TC-002: 缺少必填字段
│   │   │   └── 🟠 TC-003: 邮箱格式无效
│   │   ├── ⚠️ 边界情况
│   │   │   └── 🟡 TC-004: 用户名最大长度
│   │   └── 🔒 安全测试
│   │       └── 🔴 TC-005: SQL 注入防护
│   └── 🔗 GET /api/users/{id}
│       └── ...
└── 📦 认证模块
    └── ...
```

### 优先级标记

| 图标 | 优先级 | 说明 |
|------|--------|------|
| 🔴 | P0 | 严重 - 核心功能 |
| 🟠 | P1 | 高 - 重要功能 |
| 🟡 | P2 | 中 - 次要功能 |
| 🟢 | P3 | 低 - 锦上添花 |

### 生成 XMind 文件

使用 `scripts/generate_xmind.py` 脚本生成：

```bash
# 从 JSON 测试数据生成
python scripts/generate_xmind.py -i analysis/test_points.json -o docs/test_cases.xmind

# 生成示例文件（查看结构）
python scripts/generate_xmind.py --sample -o docs/sample_test_cases.xmind
```

### JSON 数据格式

阶段 2 生成的 `test_points.json` 需遵循以下格式：

```json
{
  "project_name": "项目名称",
  "api_version": "1.0",
  "modules": [
    {
      "name": "模块名称",
      "endpoints": [
        {
          "method": "POST",
          "path": "/api/users",
          "test_categories": {
            "normal": [
              {
                "id": "TC-001",
                "title": "测试用例标题",
                "priority": "P0",
                "description": "描述",
                "preconditions": ["前置条件1"],
                "steps": ["步骤1", "步骤2"],
                "test_data": {"key": "value"},
                "expected_result": {
                  "status_code": 200,
                  "response": {"field": "value"}
                }
              }
            ],
            "error": [],
            "boundary": [],
            "security": []
          }
        }
      ]
    }
  ]
}
```

## 资源文件

### scripts/

- `generate_xmind.py` - XMind 思维导图生成脚本

### assets/

- `test_document_template.md` - 测试文档格式模板

### references/

- `review_prompts.md` - 各阶段完整的 Codex 审核提示词
- `pytest_patterns.md` - 常用 pytest + httpx 模式和最佳实践
- `xmind_data_format.md` - XMind 测试用例 JSON 数据格式规范

## 使用示例

触发此技能的方式：
- "为这个项目生成 API 测试"
- "创建测试文档和测试脚本"
- "分析接口并生成完整的测试覆盖"
- "生成 XMind 格式的测试用例"

技能将自动：
1. 扫描项目中的 API 定义
2. 按顺序生成并审核每个阶段
3. 生成 JSON 格式的测试点数据
4. 调用 `generate_xmind.py` 生成思维导图
5. 将所有产物输出到相应目录
