#!/usr/bin/env python3
"""
金融平台 API 代理服务测试脚本
测试所有 API 端点
"""

import asyncio
import aiohttp
import sys

BASE_URL = "http://localhost:32461"


async def test_all_endpoints():
    """测试所有 API 端点"""
    async with aiohttp.ClientSession() as session:
        session_id = None
        task_id = None

        print("=" * 60)
        print("金融平台 API 代理服务测试")
        print("=" * 60)

        # 1. 初始化会话
        print("\n[1] 初始化会话...")
        async with session.post(f"{BASE_URL}/init", json={"password": "123456"}) as resp:
            data = await resp.json()
            if "session_id" in data:
                session_id = data["session_id"]
                print(f"    ✓ 成功: session_id = {session_id}")
            else:
                print(f"    ✗ 失败: {data}")
                return

        # 2. 登录
        print("\n[2] 登录...")
        async with session.post(f"{BASE_URL}/login/{session_id}") as resp:
            data = await resp.json()
            print(f"    响应: {data}")
            if data.get("status") == "success":
                print("    ✓ 登录成功")
            else:
                print("    ✗ 登录失败")

        # 3. 创建信用指标任务 (1.7)
        print("\n[3] 创建信用指标任务 (1.7)...")
        credit_tasks = [
            {
                "originalJson": "{}",
                "name": "张三",
                "idCard": "110101199001011234",
                "phone": "13800138000"
            }
        ]
        async with session.post(
            f"{BASE_URL}/create_credit_task/{session_id}",
            json=credit_tasks
        ) as resp:
            data = await resp.json()
            print(f"    响应: {data}")
            if isinstance(data, dict) and "http_status" in data:
                print(f"    HTTP状态码: {data['http_status']}")
            # 注意：1.7 接口创建后直接返回解密结果，data 是已解密的 JSON

        # 4. 创建设备信息任务 (1.3)
        print("\n[4] 创建设备信息任务 (1.3)...")
        device_tasks = [
            {
                "idType": "010105",  # PHONE
                "exid": "13800138000"
            }
        ]
        async with session.post(
            f"{BASE_URL}/create_device_task/{session_id}",
            json=device_tasks
        ) as resp:
            data = await resp.json()
            print(f"    响应: {data}")
            if isinstance(data, dict) and "http_status" in data:
                device_task_id = data.get("data") or data.get("task_id")
                print(f"    device_task_id: {device_task_id}")

        # 5. 查询设备任务结果 (1.4)
        print("\n[5] 查询设备任务结果 (1.4 GET)...")
        if device_task_id:
            async with session.get(
                f"{BASE_URL}/query_device_task/{session_id}",
                params={"task_id": device_task_id, "max_retries": 1, "retry_interval": 5}
            ) as resp:
                data = await resp.json()
                print(f"    响应: {data}")
        else:
            print("    无 device_task_id，跳过查询")

        # 6. 登出
        print("\n[6] 登出...")
        async with session.post(f"{BASE_URL}/logout/{session_id}") as resp:
            data = await resp.json()
            print(f"    响应: {data}")
            if data.get("status") == "success":
                print("    ✓ 登出成功")
            else:
                print("    ✗ 登出失败")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)


async def test_invalid_session():
    """测试无效 session_id 的错误处理"""
    print("\n[测试] 无效 session_id 错误处理...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/create_credit_task/invalid-session-id") as resp:
            data = await resp.json()
            print(f"    响应状态码: {resp.status}")
            print(f"    响应: {data}")
            if resp.status == 401:
                print("    ✓ 正确返回 401 未授权")


async def test_wrong_password():
    """测试错误密码"""
    print("\n[测试] 错误密码...")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/init", json={"password": "wrong"}) as resp:
            data = await resp.json()
            print(f"    响应状态码: {resp.status}")
            print(f"    响应: {data}")
            if resp.status == 401:
                print("    ✓ 正确返回 401 未授权")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API 测试脚本")
    parser.add_argument("--url", default=BASE_URL, help=f"API 基础URL (默认: {BASE_URL})")
    parser.add_argument("--quick", action="store_true", help="仅运行基本测试")
    args = parser.parse_args()

    print("目标服务器:", args.url)
    print()

    if args.quick:
        asyncio.run(test_all_endpoints())
    else:
        asyncio.run(test_all_endpoints())
        asyncio.run(test_invalid_session())
        asyncio.run(test_wrong_password())
