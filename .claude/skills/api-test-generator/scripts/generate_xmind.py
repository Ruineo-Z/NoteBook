#!/usr/bin/env python3
"""
XMind 测试用例生成器

将测试用例数据转换为 XMind 思维导图格式。
支持从 JSON 文件读取测试用例，生成可直接打开的 .xmind 文件。

依赖: pip install xmind
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    import xmind
    from xmind.core.topic import TopicElement
except ImportError:
    print("错误: 请先安装 xmind 库")
    print("运行: pip install xmind")
    exit(1)


def create_test_case_xmind(test_data: dict, output_path: str) -> str:
    """
    从测试数据创建 XMind 文件

    Args:
        test_data: 测试用例数据字典
        output_path: 输出文件路径

    Returns:
        生成的文件路径
    """
    workbook = xmind.load(output_path)
    sheet = workbook.getPrimarySheet()
    sheet.setTitle(test_data.get("project_name", "API 测试用例"))

    # 根节点
    root = sheet.getRootTopic()
    root.setTitle(f"{test_data.get('project_name', 'API')} 测试用例")

    # 添加文档信息作为备注
    doc_info = f"""项目: {test_data.get('project_name', 'N/A')}
版本: {test_data.get('api_version', 'N/A')}
生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    root.setPlainNotes(doc_info)

    # 按模块分组添加测试用例
    modules = test_data.get("modules", [])
    for module in modules:
        module_topic = root.addSubTopic()
        module_topic.setTitle(f"📦 {module.get('name', '未命名模块')}")

        # 添加接口信息
        endpoints = module.get("endpoints", [])
        for endpoint in endpoints:
            endpoint_topic = module_topic.addSubTopic()
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            endpoint_topic.setTitle(f"🔗 {method} {path}")

            # 按测试类别分组
            categories = endpoint.get("test_categories", {})

            # 正常流程
            if "normal" in categories:
                normal_topic = endpoint_topic.addSubTopic()
                normal_topic.setTitle("✅ 正常流程")
                add_test_cases(normal_topic, categories["normal"], "P1")

            # 错误处理
            if "error" in categories:
                error_topic = endpoint_topic.addSubTopic()
                error_topic.setTitle("❌ 错误处理")
                add_test_cases(error_topic, categories["error"], "P1")

            # 边界情况
            if "boundary" in categories:
                boundary_topic = endpoint_topic.addSubTopic()
                boundary_topic.setTitle("⚠️ 边界情况")
                add_test_cases(boundary_topic, categories["boundary"], "P2")

            # 安全测试
            if "security" in categories:
                security_topic = endpoint_topic.addSubTopic()
                security_topic.setTitle("🔒 安全测试")
                add_test_cases(security_topic, categories["security"], "P0")

    xmind.save(workbook, output_path)
    return output_path


def add_test_cases(parent_topic: TopicElement, test_cases: list, default_priority: str):
    """
    向父节点添加测试用例

    Args:
        parent_topic: 父节点
        test_cases: 测试用例列表
        default_priority: 默认优先级
    """
    for tc in test_cases:
        tc_topic = parent_topic.addSubTopic()

        # 测试用例标题
        tc_id = tc.get("id", "TC-XXX")
        title = tc.get("title", "未命名测试")
        priority = tc.get("priority", default_priority)

        # 优先级标记
        priority_icon = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}.get(priority, "⚪")
        tc_topic.setTitle(f"{priority_icon} {tc_id}: {title}")

        # 添加详细信息作为备注
        notes = build_test_case_notes(tc)
        if notes:
            tc_topic.setPlainNotes(notes)

        # 添加测试步骤作为子节点
        steps = tc.get("steps", [])
        if steps:
            steps_topic = tc_topic.addSubTopic()
            steps_topic.setTitle("📋 测试步骤")
            for i, step in enumerate(steps, 1):
                step_topic = steps_topic.addSubTopic()
                step_topic.setTitle(f"{i}. {step}")

        # 添加预期结果
        expected = tc.get("expected_result", {})
        if expected:
            expected_topic = tc_topic.addSubTopic()
            expected_topic.setTitle("🎯 预期结果")

            if "status_code" in expected:
                status_topic = expected_topic.addSubTopic()
                status_topic.setTitle(f"状态码: {expected['status_code']}")

            if "response" in expected:
                resp_topic = expected_topic.addSubTopic()
                resp_topic.setTitle("响应体验证")
                resp_topic.setPlainNotes(json.dumps(expected["response"], indent=2, ensure_ascii=False))


def build_test_case_notes(tc: dict) -> str:
    """构建测试用例的备注内容"""
    notes_parts = []

    if tc.get("description"):
        notes_parts.append(f"描述: {tc['description']}")

    if tc.get("preconditions"):
        notes_parts.append(f"\n前置条件:")
        for pre in tc["preconditions"]:
            notes_parts.append(f"  - {pre}")

    if tc.get("test_data"):
        notes_parts.append(f"\n测试数据:")
        notes_parts.append(json.dumps(tc["test_data"], indent=2, ensure_ascii=False))

    return "\n".join(notes_parts)


def create_from_test_points(test_points_path: str, output_path: str, project_name: str = "API") -> str:
    """
    从 test_points.md 或 JSON 文件创建 XMind

    Args:
        test_points_path: 测试点文件路径
        output_path: 输出 XMind 文件路径
        project_name: 项目名称

    Returns:
        生成的文件路径
    """
    test_points_file = Path(test_points_path)

    if test_points_file.suffix == ".json":
        with open(test_points_file, "r", encoding="utf-8") as f:
            test_data = json.load(f)
    else:
        # 如果是其他格式，创建示例结构
        test_data = {
            "project_name": project_name,
            "api_version": "1.0",
            "modules": []
        }

    return create_test_case_xmind(test_data, output_path)


def create_sample_xmind(output_path: str) -> str:
    """
    创建示例 XMind 文件，展示测试用例结构

    Args:
        output_path: 输出文件路径

    Returns:
        生成的文件路径
    """
    sample_data = {
        "project_name": "示例 API",
        "api_version": "1.0",
        "modules": [
            {
                "name": "用户管理",
                "endpoints": [
                    {
                        "method": "POST",
                        "path": "/api/users",
                        "test_categories": {
                            "normal": [
                                {
                                    "id": "TC-001",
                                    "title": "创建用户成功",
                                    "priority": "P0",
                                    "description": "使用有效数据创建新用户",
                                    "preconditions": ["用户未存在", "数据库连接正常"],
                                    "steps": [
                                        "准备有效的用户数据",
                                        "发送 POST /api/users 请求",
                                        "验证响应状态码和数据"
                                    ],
                                    "test_data": {
                                        "username": "testuser",
                                        "email": "test@example.com",
                                        "password": "SecurePass123"
                                    },
                                    "expected_result": {
                                        "status_code": 201,
                                        "response": {"id": "number", "username": "testuser"}
                                    }
                                }
                            ],
                            "error": [
                                {
                                    "id": "TC-002",
                                    "title": "缺少必填字段",
                                    "priority": "P1",
                                    "description": "验证缺少必填字段时返回 400 错误",
                                    "steps": [
                                        "准备缺少 email 的请求数据",
                                        "发送 POST /api/users 请求",
                                        "验证返回 400 错误"
                                    ],
                                    "expected_result": {
                                        "status_code": 400,
                                        "response": {"error": "email is required"}
                                    }
                                },
                                {
                                    "id": "TC-003",
                                    "title": "邮箱格式无效",
                                    "priority": "P1",
                                    "description": "验证邮箱格式校验",
                                    "steps": [
                                        "准备无效邮箱格式的数据",
                                        "发送 POST /api/users 请求",
                                        "验证返回 400 错误"
                                    ],
                                    "expected_result": {
                                        "status_code": 400
                                    }
                                }
                            ],
                            "boundary": [
                                {
                                    "id": "TC-004",
                                    "title": "用户名最大长度",
                                    "priority": "P2",
                                    "description": "验证用户名 50 字符限制",
                                    "steps": [
                                        "准备 51 字符的用户名",
                                        "发送请求",
                                        "验证返回错误"
                                    ],
                                    "expected_result": {
                                        "status_code": 400
                                    }
                                }
                            ],
                            "security": [
                                {
                                    "id": "TC-005",
                                    "title": "SQL 注入防护",
                                    "priority": "P0",
                                    "description": "验证 SQL 注入攻击被阻止",
                                    "steps": [
                                        "在用户名中注入 SQL 语句",
                                        "发送请求",
                                        "验证请求被拒绝或安全处理"
                                    ],
                                    "test_data": {
                                        "username": "'; DROP TABLE users; --"
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
                        "path": "/api/users/{id}",
                        "test_categories": {
                            "normal": [
                                {
                                    "id": "TC-006",
                                    "title": "获取用户详情",
                                    "priority": "P0",
                                    "description": "根据 ID 获取用户信息",
                                    "steps": [
                                        "使用有效用户 ID",
                                        "发送 GET 请求",
                                        "验证返回用户数据"
                                    ],
                                    "expected_result": {
                                        "status_code": 200
                                    }
                                }
                            ],
                            "error": [
                                {
                                    "id": "TC-007",
                                    "title": "用户不存在",
                                    "priority": "P1",
                                    "description": "查询不存在的用户 ID",
                                    "steps": [
                                        "使用不存在的用户 ID",
                                        "发送 GET 请求",
                                        "验证返回 404"
                                    ],
                                    "expected_result": {
                                        "status_code": 404
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
                        "path": "/api/auth/login",
                        "test_categories": {
                            "normal": [
                                {
                                    "id": "TC-008",
                                    "title": "登录成功",
                                    "priority": "P0",
                                    "description": "使用正确凭据登录",
                                    "steps": [
                                        "准备有效的登录凭据",
                                        "发送 POST /api/auth/login",
                                        "验证返回 token"
                                    ],
                                    "expected_result": {
                                        "status_code": 200,
                                        "response": {"token": "string"}
                                    }
                                }
                            ],
                            "error": [
                                {
                                    "id": "TC-009",
                                    "title": "密码错误",
                                    "priority": "P0",
                                    "description": "使用错误密码登录",
                                    "steps": [
                                        "准备错误的密码",
                                        "发送登录请求",
                                        "验证返回 401"
                                    ],
                                    "expected_result": {
                                        "status_code": 401
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    return create_test_case_xmind(sample_data, output_path)


def main():
    parser = argparse.ArgumentParser(
        description="生成 XMind 格式的测试用例思维导图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成示例 XMind 文件
  python generate_xmind.py --sample -o test_cases.xmind

  # 从 JSON 文件生成
  python generate_xmind.py -i test_data.json -o test_cases.xmind

  # 指定项目名称
  python generate_xmind.py -i test_data.json -o test_cases.xmind --project "我的项目"
"""
    )

    parser.add_argument("-i", "--input", help="输入的测试数据文件 (JSON 格式)")
    parser.add_argument("-o", "--output", required=True, help="输出的 XMind 文件路径")
    parser.add_argument("--project", default="API", help="项目名称")
    parser.add_argument("--sample", action="store_true", help="生成示例 XMind 文件")

    args = parser.parse_args()

    if args.sample:
        output = create_sample_xmind(args.output)
        print(f"✅ 示例 XMind 文件已生成: {output}")
    elif args.input:
        output = create_from_test_points(args.input, args.output, args.project)
        print(f"✅ XMind 文件已生成: {output}")
    else:
        parser.print_help()
        print("\n错误: 请指定 --input 或 --sample 参数")
        exit(1)


if __name__ == "__main__":
    main()
