# XMind 测试用例数据格式

本文档定义了用于生成 XMind 思维导图的 JSON 数据格式规范。

## 完整数据结构

```json
{
  "project_name": "string - 项目名称",
  "api_version": "string - API 版本号",
  "modules": [
    {
      "name": "string - 模块名称",
      "endpoints": [
        {
          "method": "string - HTTP 方法 (GET/POST/PUT/DELETE/PATCH)",
          "path": "string - API 路径",
          "test_categories": {
            "normal": "array - 正常流程测试用例",
            "error": "array - 错误处理测试用例",
            "boundary": "array - 边界情况测试用例",
            "security": "array - 安全测试用例"
          }
        }
      ]
    }
  ]
}
```

## 测试用例对象结构

每个测试用例对象包含以下字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 测试用例编号，如 "TC-001" |
| title | string | 是 | 测试用例标题 |
| priority | string | 是 | 优先级：P0/P1/P2/P3 |
| description | string | 否 | 详细描述 |
| preconditions | array | 否 | 前置条件列表 |
| steps | array | 否 | 测试步骤列表 |
| test_data | object | 否 | 测试数据 |
| expected_result | object | 否 | 预期结果 |

### expected_result 结构

```json
{
  "status_code": 200,
  "response": {
    "field": "expected_value"
  }
}
```

## 完整示例

```json
{
  "project_name": "用户管理系统",
  "api_version": "2.0",
  "modules": [
    {
      "name": "用户管理",
      "endpoints": [
        {
          "method": "POST",
          "path": "/api/v2/users",
          "test_categories": {
            "normal": [
              {
                "id": "TC-001",
                "title": "创建用户成功",
                "priority": "P0",
                "description": "使用有效数据创建新用户，验证返回正确的用户信息",
                "preconditions": [
                  "用户邮箱未被注册",
                  "数据库连接正常"
                ],
                "steps": [
                  "准备有效的用户注册数据",
                  "发送 POST /api/v2/users 请求",
                  "验证响应状态码为 201",
                  "验证响应体包含用户 ID 和基本信息"
                ],
                "test_data": {
                  "username": "testuser",
                  "email": "test@example.com",
                  "password": "SecurePass123!",
                  "role": "user"
                },
                "expected_result": {
                  "status_code": 201,
                  "response": {
                    "id": "number",
                    "username": "testuser",
                    "email": "test@example.com",
                    "role": "user",
                    "created_at": "datetime"
                  }
                }
              },
              {
                "id": "TC-002",
                "title": "创建管理员用户",
                "priority": "P1",
                "description": "创建具有管理员权限的用户",
                "steps": [
                  "使用管理员凭据认证",
                  "发送创建用户请求，role 设为 admin",
                  "验证用户创建成功"
                ],
                "test_data": {
                  "username": "admin_user",
                  "email": "admin@example.com",
                  "password": "AdminPass123!",
                  "role": "admin"
                },
                "expected_result": {
                  "status_code": 201
                }
              }
            ],
            "error": [
              {
                "id": "TC-003",
                "title": "缺少必填字段 - email",
                "priority": "P1",
                "description": "验证缺少 email 字段时返回 400 错误",
                "steps": [
                  "准备缺少 email 的请求数据",
                  "发送 POST 请求",
                  "验证返回 400 错误和错误信息"
                ],
                "test_data": {
                  "username": "testuser",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400,
                  "response": {
                    "error": "email is required"
                  }
                }
              },
              {
                "id": "TC-004",
                "title": "邮箱格式无效",
                "priority": "P1",
                "description": "验证邮箱格式校验功能",
                "test_data": {
                  "username": "testuser",
                  "email": "invalid-email",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400
                }
              },
              {
                "id": "TC-005",
                "title": "邮箱已被注册",
                "priority": "P1",
                "description": "验证重复邮箱注册被拒绝",
                "preconditions": [
                  "邮箱 existing@example.com 已存在"
                ],
                "test_data": {
                  "username": "newuser",
                  "email": "existing@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 409
                }
              }
            ],
            "boundary": [
              {
                "id": "TC-006",
                "title": "用户名最小长度",
                "priority": "P2",
                "description": "验证用户名最小长度限制（3 字符）",
                "test_data": {
                  "username": "ab",
                  "email": "test@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400
                }
              },
              {
                "id": "TC-007",
                "title": "用户名最大长度",
                "priority": "P2",
                "description": "验证用户名最大长度限制（50 字符）",
                "test_data": {
                  "username": "a]".repeat(51),
                  "email": "test@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400
                }
              },
              {
                "id": "TC-008",
                "title": "密码复杂度不足",
                "priority": "P2",
                "description": "验证密码必须包含大小写字母和数字",
                "test_data": {
                  "username": "testuser",
                  "email": "test@example.com",
                  "password": "simple"
                },
                "expected_result": {
                  "status_code": 400
                }
              }
            ],
            "security": [
              {
                "id": "TC-009",
                "title": "SQL 注入防护",
                "priority": "P0",
                "description": "验证 SQL 注入攻击被正确处理",
                "test_data": {
                  "username": "'; DROP TABLE users; --",
                  "email": "test@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400
                }
              },
              {
                "id": "TC-010",
                "title": "XSS 防护",
                "priority": "P0",
                "description": "验证 XSS 攻击被正确处理",
                "test_data": {
                  "username": "<script>alert('xss')</script>",
                  "email": "test@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 400
                }
              }
            ]
          }
        },
        {
          "method": "GET",
          "path": "/api/v2/users/{id}",
          "test_categories": {
            "normal": [
              {
                "id": "TC-011",
                "title": "获取用户详情",
                "priority": "P0",
                "description": "根据用户 ID 获取用户详细信息",
                "preconditions": [
                  "用户 ID 1 存在"
                ],
                "steps": [
                  "发送 GET /api/v2/users/1 请求",
                  "验证返回用户完整信息"
                ],
                "expected_result": {
                  "status_code": 200,
                  "response": {
                    "id": 1,
                    "username": "string",
                    "email": "string"
                  }
                }
              }
            ],
            "error": [
              {
                "id": "TC-012",
                "title": "用户不存在",
                "priority": "P1",
                "description": "查询不存在的用户 ID",
                "steps": [
                  "发送 GET /api/v2/users/99999 请求",
                  "验证返回 404 错误"
                ],
                "expected_result": {
                  "status_code": 404
                }
              },
              {
                "id": "TC-013",
                "title": "无效的用户 ID 格式",
                "priority": "P2",
                "description": "使用非数字 ID 查询",
                "steps": [
                  "发送 GET /api/v2/users/abc 请求",
                  "验证返回 400 错误"
                ],
                "expected_result": {
                  "status_code": 400
                }
              }
            ],
            "boundary": [],
            "security": [
              {
                "id": "TC-014",
                "title": "未授权访问",
                "priority": "P0",
                "description": "未登录用户无法查看其他用户信息",
                "steps": [
                  "不携带认证 token",
                  "发送 GET /api/v2/users/1 请求",
                  "验证返回 401 错误"
                ],
                "expected_result": {
                  "status_code": 401
                }
              }
            ]
          }
        }
      ]
    },
    {
      "name": "认证模块",
      "endpoints": [
        {
          "method": "POST",
          "path": "/api/v2/auth/login",
          "test_categories": {
            "normal": [
              {
                "id": "TC-015",
                "title": "登录成功",
                "priority": "P0",
                "description": "使用正确的凭据登录",
                "steps": [
                  "准备有效的登录凭据",
                  "发送 POST /api/v2/auth/login 请求",
                  "验证返回 access_token 和 refresh_token"
                ],
                "test_data": {
                  "email": "test@example.com",
                  "password": "SecurePass123!"
                },
                "expected_result": {
                  "status_code": 200,
                  "response": {
                    "access_token": "string",
                    "refresh_token": "string",
                    "token_type": "bearer"
                  }
                }
              }
            ],
            "error": [
              {
                "id": "TC-016",
                "title": "密码错误",
                "priority": "P0",
                "description": "使用错误密码登录",
                "test_data": {
                  "email": "test@example.com",
                  "password": "WrongPassword"
                },
                "expected_result": {
                  "status_code": 401
                }
              },
              {
                "id": "TC-017",
                "title": "用户不存在",
                "priority": "P1",
                "description": "使用未注册的邮箱登录",
                "test_data": {
                  "email": "nonexistent@example.com",
                  "password": "AnyPassword123!"
                },
                "expected_result": {
                  "status_code": 401
                }
              }
            ],
            "boundary": [],
            "security": [
              {
                "id": "TC-018",
                "title": "暴力破解防护",
                "priority": "P0",
                "description": "验证连续失败登录后账户被锁定",
                "steps": [
                  "连续 5 次使用错误密码登录",
                  "验证第 6 次登录被拒绝",
                  "验证返回账户锁定提示"
                ],
                "expected_result": {
                  "status_code": 429
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

## 生成 XMind 的层级映射

JSON 数据到 XMind 节点的映射关系：

```
project_name          → 根节点标题
└── modules[].name    → 一级子节点 (📦 模块名)
    └── endpoints[]   → 二级子节点 (🔗 METHOD /path)
        └── test_categories
            ├── normal    → 三级子节点 (✅ 正常流程)
            ├── error     → 三级子节点 (❌ 错误处理)
            ├── boundary  → 三级子节点 (⚠️ 边界情况)
            └── security  → 三级子节点 (🔒 安全测试)
                └── test_case → 四级子节点 (优先级图标 TC-XXX: 标题)
                    ├── steps         → 五级子节点 (📋 测试步骤)
                    └── expected_result → 五级子节点 (🎯 预期结果)
```

## 注意事项

1. **编号唯一性**：每个测试用例的 `id` 必须在整个项目中唯一
2. **优先级规范**：只能使用 P0/P1/P2/P3 四个级别
3. **空数组处理**：如果某个类别没有测试用例，使用空数组 `[]`
4. **特殊字符**：JSON 中的特殊字符需要正确转义
5. **中文支持**：完全支持中文内容，确保文件使用 UTF-8 编码
