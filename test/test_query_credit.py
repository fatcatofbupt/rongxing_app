#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 /app-api/system/third/queryCredit 接口

用法: python test/test_query_credit.py
"""

import pyrootutils

# 设置项目根目录
root = pyrootutils.setup_root(__file__, pythonpath=True)

import requests
import json
import config
from main import FinancialPlatformAPI


def test_query_credit():
    """测试 queryCredit 接口"""

    # 1. 登录获取 token
    print("=" * 50)
    print("[1] 登录中...")

    api = FinancialPlatformAPI(
        base_url=config.base_url,
        app_id=config.app_id,
        private_key=config.private_key,
        username=config.username,
        password=config.password
    )
    api.login()

    access_token = api.access_token
    user_id = api.user_id

    print(f"    user_id: {user_id}")
    print(f"    access_token: {access_token}")
    print()

    # 2. 调用 queryCredit 接口
    print("[2] 调用 queryCredit 接口...")
    url = "http://192.168.3.53:48080/app-api/system/third/queryCredit"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = [
        {
            "originalJson": "{}",
            "name": "于磊",
            "idCard": "130622199704083635",
            "phone": "15732264495"
        },
        {
            "originalJson": "{}",
            "name": "于秀伟",
            "idCard": "120110197712310945",
            "phone": "13920751301"
        },
        {
            "originalJson": "{}",
            "name": "于精贺",
            "idCard": "211203198812260067",
            "phone": "15710592712"
        }
    ]

    print(f"    URL: {url}")
    print(f"    Data: {json.dumps(data, ensure_ascii=False)}")
    print()

    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        print(f"    HTTP Status: {resp.status_code}")
        print(f"    Response: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.ReadTimeout:
        print("    ERROR: 请求超时 (15s)")
    except Exception as e:
        print(f"    ERROR: {e}")
    print()

    return None


if __name__ == "__main__":
    test_query_credit()
