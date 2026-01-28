# Pytest + httpx 模式

使用 pytest 和 httpx 进行 API 测试的常用模式和最佳实践。

## 数据策略概述

| 策略 | 依赖 | 适用场景 |
|------|------|----------|
| 真实数据 | httpx | Agent 服务、端到端验证 |
| Mock 数据 | respx / pytest-mock | CI/CD、快速反馈、隔离测试 |

---

## 一、真实数据模式（集成测试）

### 基础设置

### conftest.py

```python
import pytest
import httpx
from typing import AsyncGenerator

# 基础 URL 配置
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session")
def base_url() -> str:
    """API 请求的基础 URL。"""
    return BASE_URL


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """用于 API 请求的异步 HTTP 客户端。"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
async def authenticated_client(client: httpx.AsyncClient) -> httpx.AsyncClient:
    """带认证令牌的客户端。"""
    # 登录并获取令牌
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    slow: 标记为慢速测试
    integration: 标记为集成测试
```

## 常用测试模式

### 正常流程测试

```python
import pytest
import httpx


@pytest.mark.asyncio
async def test_create_user_success(client: httpx.AsyncClient):
    """测试成功创建用户。"""
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePass123!"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "password" not in data  # 密码不应返回
```

### 错误处理测试

```python
@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: httpx.AsyncClient):
    """测试邮箱已存在时返回 409 冲突。"""
    payload = {"username": "user1", "email": "existing@example.com", "password": "Pass123!"}

    # 创建第一个用户
    await client.post("/users", json=payload)

    # 尝试创建重复用户
    payload["username"] = "user2"
    response = await client.post("/users", json=payload)

    assert response.status_code == 409
    assert "邮箱已存在" in response.json()["detail"].lower() or "email already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_user_not_found(client: httpx.AsyncClient):
    """测试用户不存在时返回 404。"""
    response = await client.get("/users/99999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user_validation_error(client: httpx.AsyncClient):
    """测试无效输入返回 422。"""
    payload = {
        "username": "",  # 空用户名
        "email": "invalid-email",  # 无效邮箱格式
        "password": "123"  # 太短
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("username" in str(e).lower() for e in errors)
```

### 认证测试

```python
@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: httpx.AsyncClient):
    """测试无令牌访问受保护接口返回 401。"""
    response = await client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: httpx.AsyncClient):
    """测试无效令牌返回 401。"""
    client.headers["Authorization"] = "Bearer invalid_token"
    response = await client.get("/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_success(authenticated_client: httpx.AsyncClient):
    """测试成功访问受保护接口。"""
    response = await authenticated_client.get("/users/me")

    assert response.status_code == 200
    assert "username" in response.json()
```

### 参数化测试

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "@missing-local.com",
    "missing-domain@",
    "spaces in@email.com",
    "",
])
async def test_create_user_invalid_email_formats(
    client: httpx.AsyncClient,
    invalid_email: str
):
    """测试各种无效邮箱格式。"""
    payload = {
        "username": "testuser",
        "email": invalid_email,
        "password": "ValidPass123!"
    }

    response = await client.post("/users", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("status_filter,expected_count", [
    ("active", 3),
    ("inactive", 2),
    ("pending", 1),
])
async def test_list_users_by_status(
    client: httpx.AsyncClient,
    status_filter: str,
    expected_count: int
):
    """测试按状态筛选用户。"""
    response = await client.get(f"/users?status={status_filter}")

    assert response.status_code == 200
    assert len(response.json()) == expected_count
```

### 边界值测试

```python
@pytest.mark.asyncio
async def test_username_minimum_length(client: httpx.AsyncClient):
    """测试用户名最小长度（3 字符）。"""
    payload = {"username": "abc", "email": "test@example.com", "password": "Pass123!"}
    response = await client.post("/users", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_username_below_minimum_length(client: httpx.AsyncClient):
    """测试用户名低于最小长度。"""
    payload = {"username": "ab", "email": "test@example.com", "password": "Pass123!"}
    response = await client.post("/users", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_username_maximum_length(client: httpx.AsyncClient):
    """测试用户名最大长度（50 字符）。"""
    payload = {"username": "a" * 50, "email": "test@example.com", "password": "Pass123!"}
    response = await client.post("/users", json=payload)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_username_exceeds_maximum_length(client: httpx.AsyncClient):
    """测试用户名超过最大长度。"""
    payload = {"username": "a" * 51, "email": "test@example.com", "password": "Pass123!"}
    response = await client.post("/users", json=payload)
    assert response.status_code == 422
```

### 安全测试

```python
@pytest.mark.asyncio
async def test_sql_injection_in_search(client: httpx.AsyncClient):
    """测试 SQL 注入尝试被安全处理。"""
    malicious_query = "'; DROP TABLE users; --"
    response = await client.get(f"/users/search?q={malicious_query}")

    # 不应导致服务器错误
    assert response.status_code in [200, 400, 422]
    assert response.status_code != 500


@pytest.mark.asyncio
async def test_xss_payload_sanitized(client: httpx.AsyncClient):
    """测试 XSS 负载在响应中被清理。"""
    payload = {
        "username": "<script>alert('xss')</script>",
        "email": "test@example.com",
        "password": "Pass123!"
    }

    response = await client.post("/users", json=payload)

    if response.status_code == 201:
        # 如果接受，确保响应中已清理
        assert "<script>" not in response.text
```

## 测试数据工厂

```python
from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class UserFactory:
    """生成测试用户数据的工厂。"""

    @staticmethod
    def build(
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "TestPass123!"
    ) -> dict:
        unique_id = uuid.uuid4().hex[:8]
        return {
            "username": username or f"user_{unique_id}",
            "email": email or f"user_{unique_id}@example.com",
            "password": password
        }

    @staticmethod
    def build_invalid() -> dict:
        """构建无效用户数据用于负面测试。"""
        return {
            "username": "",
            "email": "invalid",
            "password": "123"
        }


# 在测试中使用
@pytest.mark.asyncio
async def test_create_multiple_users(client: httpx.AsyncClient):
    """测试创建多个唯一用户。"""
    for _ in range(5):
        payload = UserFactory.build()
        response = await client.post("/users", json=payload)
        assert response.status_code == 201
```

## 清理模式

```python
@pytest.fixture
async def created_user(client: httpx.AsyncClient) -> dict:
    """创建用户并在测试后清理。"""
    payload = UserFactory.build()
    response = await client.post("/users", json=payload)
    user = response.json()

    yield user

    # 清理：测试后删除用户
    await client.delete(f"/users/{user['id']}")


@pytest.mark.asyncio
async def test_update_user(authenticated_client: httpx.AsyncClient, created_user: dict):
    """测试更新用户。"""
    response = await authenticated_client.patch(
        f"/users/{created_user['id']}",
        json={"username": "updated_name"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "updated_name"
```

## 响应验证辅助函数

```python
def assert_pagination_response(response: httpx.Response, expected_total: int = None):
    """断言响应遵循分页结构。"""
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    if expected_total is not None:
        assert data["total"] == expected_total


def assert_error_response(response: httpx.Response, status_code: int, message_contains: str = None):
    """断言错误响应结构。"""
    assert response.status_code == status_code
    data = response.json()

    assert "detail" in data
    if message_contains:
        assert message_contains.lower() in data["detail"].lower()
```

---

## 二、Mock 数据模式（单元测试）

使用 `respx` 库模拟 HTTP 响应，无需启动真实服务。

### 安装依赖

```bash
pip install respx pytest-asyncio
```

### conftest.py (Mock 模式)

```python
import pytest
import httpx
import respx
from typing import AsyncGenerator

BASE_URL = "http://localhost:8000"


@pytest.fixture
def mock_api():
    """启用 respx mock。"""
    with respx.mock(base_url=BASE_URL, assert_all_called=False) as respx_mock:
        yield respx_mock


@pytest.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """HTTP 客户端（配合 respx 使用）。"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client
```

### Mock 测试示例

```python
import pytest
import httpx
import respx
from httpx import Response


@pytest.mark.asyncio
async def test_create_user_success_mock(mock_api, client: httpx.AsyncClient):
    """Mock 测试：成功创建用户。"""
    # 设置 mock 响应
    mock_api.post("/users").mock(return_value=Response(
        201,
        json={
            "id": 1,
            "username": "newuser",
            "email": "newuser@example.com"
        }
    ))

    # 发送请求
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePass123!"
    }
    response = await client.post("/users", json=payload)

    # 断言
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_get_user_not_found_mock(mock_api, client: httpx.AsyncClient):
    """Mock 测试：用户不存在。"""
    mock_api.get("/users/99999").mock(return_value=Response(
        404,
        json={"detail": "User not found"}
    ))

    response = await client.get("/users/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_validation_error_mock(mock_api, client: httpx.AsyncClient):
    """Mock 测试：验证错误。"""
    mock_api.post("/users").mock(return_value=Response(
        422,
        json={
            "detail": [
                {"loc": ["body", "email"], "msg": "invalid email format"}
            ]
        }
    ))

    response = await client.post("/users", json={"email": "invalid"})

    assert response.status_code == 422
```

### Mock 认证流程

```python
@pytest.fixture
def mock_auth(mock_api):
    """Mock 认证相关接口。"""
    # Mock 登录
    mock_api.post("/auth/login").mock(return_value=Response(
        200,
        json={
            "access_token": "mock_token_12345",
            "refresh_token": "mock_refresh_token",
            "token_type": "bearer"
        }
    ))

    # Mock token 验证（受保护接口）
    mock_api.get("/users/me").mock(return_value=Response(
        200,
        json={"id": 1, "username": "testuser", "email": "test@example.com"}
    ))

    return mock_api


@pytest.mark.asyncio
async def test_login_and_access_protected_mock(mock_auth, client: httpx.AsyncClient):
    """Mock 测试：登录并访问受保护接口。"""
    # 登录
    login_response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 访问受保护接口
    client.headers["Authorization"] = f"Bearer {token}"
    me_response = await client.get("/users/me")
    assert me_response.status_code == 200
```

### Mock 参数化测试

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("status_code,error_msg", [
    (400, "Bad request"),
    (401, "Unauthorized"),
    (403, "Forbidden"),
    (404, "Not found"),
    (500, "Internal server error"),
])
async def test_error_responses_mock(
    mock_api,
    client: httpx.AsyncClient,
    status_code: int,
    error_msg: str
):
    """Mock 测试：各种错误响应。"""
    mock_api.get("/test-endpoint").mock(return_value=Response(
        status_code,
        json={"detail": error_msg}
    ))

    response = await client.get("/test-endpoint")

    assert response.status_code == status_code
    assert error_msg in response.json()["detail"]
```

### Mock Agent 流式响应

```python
import json


@pytest.mark.asyncio
async def test_agent_stream_response_mock(mock_api, client: httpx.AsyncClient):
    """Mock 测试：Agent 流式响应。"""
    # 模拟 SSE 流式响应
    stream_data = [
        'data: {"type": "thinking", "content": "分析问题..."}\n\n',
        'data: {"type": "content", "content": "这是回答的第一部分"}\n\n',
        'data: {"type": "content", "content": "这是回答的第二部分"}\n\n',
        'data: {"type": "done"}\n\n',
    ]

    mock_api.post("/agent/chat").mock(return_value=Response(
        200,
        content="".join(stream_data),
        headers={"content-type": "text/event-stream"}
    ))

    response = await client.post("/agent/chat", json={"message": "你好"})

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
```

### Mock 与真实测试对比

```python
# tests/unit/test_users_mock.py - Mock 测试
@pytest.mark.asyncio
async def test_create_user_mock(mock_api, client):
    mock_api.post("/users").mock(return_value=Response(201, json={"id": 1}))
    response = await client.post("/users", json={...})
    assert response.status_code == 201


# tests/integration/test_users_real.py - 真实测试
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_user_real(client):
    response = await client.post("/users", json={...})
    assert response.status_code == 201
    # 真实测试可以验证更多细节
    assert response.json()["id"] > 0
```

### 运行不同类型的测试

```bash
# 只运行 mock 测试（快速，CI 用）
pytest tests/unit/ -v

# 只运行集成测试（需要服务运行）
pytest tests/integration/ -v -m integration

# 运行所有测试
pytest tests/ -v
```
