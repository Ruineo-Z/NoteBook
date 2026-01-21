# Codex 审核提示词

本文档包含 API 测试生成工作流各阶段的完整审核提示词。

## 阶段 1：接口分析审核

```
你正在审核一份 API 分析文档。你的任务是验证其完整性和准确性。

背景：该文档列出了项目中发现的所有 REST API 接口。

审核清单：
1. 完整性：是否包含代码库中的所有接口？
   - 检查所有框架文件中的路由定义（FastAPI routers、Flask blueprints、Django urls）
   - 查找动态注册的路由

2. 准确性：每个接口是否正确记录？
   - HTTP 方法与代码匹配
   - URL 路径正确（包括路径参数）
   - 查询参数已列出
   - 请求体结构与 Pydantic 模型/dataclasses 匹配

3. 响应模型：是否记录了响应？
   - 成功和错误情况的状态码
   - 响应体结构

4. 认证：是否记录了认证要求？
   - 哪些接口需要认证
   - 认证类型（Bearer token、API key 等）

输出格式（JSON）：
{
  "passed": true/false,
  "issues": [
    {"severity": "high/medium/low", "endpoint": "/路径", "issue": "问题描述"}
  ],
  "suggestions": ["建议 1", "建议 2"],
  "missing_endpoints": ["/可能遗漏的/接口"]
}
```

## 阶段 2：测试点覆盖度审核

```
你正在审核一份测试点文档。你的任务是确保测试覆盖全面。

背景：该文档列出了 REST API 接口的测试场景。

覆盖类别（全部必需）：

1. 正常流程（每个接口必需）
   - 包含所有必填字段的有效请求
   - 包含可选字段的有效请求
   - 预期的成功响应

2. 输入验证（必需）
   - 缺失必填字段
   - 无效字段类型（字符串代替整数等）
   - 无效字段值（负数、空字符串）
   - 边界值（最小值、最大值、边界值）

3. 错误处理（必需）
   - 400 Bad Request 场景
   - 401 Unauthorized（如需认证）
   - 403 Forbidden（权限拒绝）
   - 404 Not Found（资源不存在）
   - 409 Conflict（重复、状态冲突）
   - 422 Validation Error
   - 500 Internal Server Error（如适用）

4. 边界情况（必需）
   - 空数组/列表
   - 允许的 null 值
   - 最大长度字符串
   - Unicode 和特殊字符
   - 大型负载

5. 安全测试（必需）
   - SQL 注入尝试
   - XSS 负载处理
   - 认证绕过尝试
   - 授权边界测试
   - 速率限制（如适用）

6. 业务逻辑（视情况而定）
   - 状态转换
   - 跨接口数据一致性
   - 级联效应（删除父级影响子级）

输出格式（JSON）：
{
  "passed": true/false,
  "coverage_score": 0-100,
  "missing": [
    {"endpoint": "/路径", "category": "类别", "missing_tests": ["测试1", "测试2"]}
  ],
  "recommendations": ["建议 1"]
}
```

## 阶段 3：测试文档质量审核

```
你正在审核一份正式测试文档。你的任务是确保质量和一致性。

背景：该文档包含 API 测试的结构化测试用例。

质量清单：

1. 完整性
   - 阶段 2 的所有测试点都已转换为测试用例
   - 没有遗漏测试场景
   - 每个接口都有足够的覆盖

2. 清晰度
   - 测试步骤清晰可复现
   - 任何人都可以在没有额外上下文的情况下执行测试
   - 没有模糊语言（"应该可以"、"可能失败"）

3. 具体性
   - 预期结果具体（确切的状态码、响应字段）
   - 测试数据具体，非占位符
   - 断言可验证

4. 一致性
   - 测试用例编号遵循模式
   - 优先级分配一致
   - 格式统一

5. 可追溯性
   - 测试用例可追溯到需求/接口
   - 类别正确分配

输出格式（JSON）：
{
  "passed": true/false,
  "completeness": 0-100,
  "issues": [
    {"test_id": "TC-001", "issue": "问题描述", "severity": "high/medium/low"}
  ],
  "formatting_issues": ["问题 1"],
  "suggestions": ["建议 1"]
}
```

## 阶段 4：测试脚本代码审查

```
你正在审查 pytest 测试脚本。你的任务是确保代码质量和正确性。

背景：使用 pytest 和 httpx 进行 API 测试的 Python 测试文件。

代码审查清单：

1. 断言
   - 存在状态码断言
   - 响应体断言具体
   - 适用时有错误消息断言
   - 没有过于宽泛的断言（assert response is not None）

2. 测试隔离
   - 测试不依赖执行顺序
   - 测试间无共享可变状态
   - 使用 fixtures 正确设置/清理
   - 测试间数据库状态重置

3. Fixtures
   - 适当的作用域（function、class、module、session）
   - 处理清理（yield fixtures 或 finalizers）
   - 通用设置的可复用 fixtures

4. 异步处理
   - 正确使用 async/await 与 httpx.AsyncClient
   - 需要时有 pytest-asyncio 标记
   - 异步测试中无阻塞调用

5. 测试数据
   - 测试数据真实
   - 复杂数据使用工厂或 fixtures
   - 无硬编码敏感数据

6. 错误处理
   - 测试处理预期异常
   - API 调用有超时处理
   - 测试失败时正确清理

7. 文档
   - 测试函数名称描述性强
   - 复杂测试有文档字符串
   - 代码中测试目的清晰

输出格式（JSON）：
{
  "passed": true/false,
  "code_issues": [
    {"file": "test_file.py", "line": 42, "issue": "问题描述", "severity": "high/medium/low"}
  ],
  "suggestions": ["建议 1"],
  "best_practices_violations": ["违规 1"]
}
```

## 使用说明

1. 始终解析 Codex 的 JSON 输出
2. 如果 `passed` 为 `false`，迭代修复
3. 每阶段最多 3 轮审核
4. 记录所有审核反馈以便追溯
