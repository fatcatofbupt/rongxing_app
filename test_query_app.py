#!/usr/bin/env python3
"""测试 queryAppSingle 接口"""
import sys
import json
import time
import base64
import requests
import config
from main import FinancialPlatformAPI

async def test_query():
    """测试 queryAppSingle 接口"""
    api = FinancialPlatformAPI(
        base_url="http://192.168.3.53:48080",
        app_id=config.app_id,
        private_key=config.private_key,
        username=config.username,
        password=config.password
    )

    # 登录
    print("【登录中...】")
    success = api.login()
    if not success:
        print("登录失败!")
        return
    access_token = api.access_token
    print(f"登录成功! access_token: {access_token}")

    # 查询单个应用
    url = f"{api.base_url}/app-api/system/third/queryAppSingle"
    data = {
        "idType": "010105",
        "exid": "13775297293"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    print(f"\n【查询请求】URL: {url}")
    print(f"【请求数据】{json.dumps(data, indent=2)}")

    session = await api.get_session()
    resp = await session.post(url, json=data, headers=headers)
    result = await resp.text()

    print(f"【查询响应】状态码: {resp.status}")
    print(f"【查询响应】原始内容: {result}")

    # 解密数据
    try:
        result_json = json.loads(result)
        if result_json.get("code") == 200 and result_json.get("data"):
            encrypted_data = result_json["data"]
            decrypted = api.decrypt_data(encrypted_data)
            decrypted_json = json.loads(decrypted)
            print(f"\n【解密后内容】:")
            print(json.dumps(decrypted_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"解密失败: {e}")

    await api.close_session()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_query())
