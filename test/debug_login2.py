#!/usr/bin/env python3
"""
调试登录 - 直接调用 FinancialPlatformAPI
"""
import sys
sys.path.insert(0, '/home/ubuntu/tmp/rongxing')

from main import FinancialPlatformAPI
import config

api = FinancialPlatformAPI(
    base_url=config.base_url,
    app_id=config.app_id,
    private_key=config.private_key,
    username=config.username,
    password=config.password
)

# 直接调用 login 方法
print("直接调用 login 方法:")
print(f"URL: {config.base_url}/app-api/system/third/login")
print(f"Username: {config.username}")
print(f"AppId: {config.app_id}")

# 查看签名字符串
import time
timestamp = int(time.time() * 1000)
params = {
    'appId': config.app_id,
    'password': str(config.password),
    'timestamp': str(timestamp),
    'username': config.username
}
sorted_keys = sorted(params.keys())
sign_string = '&'.join([f'{key}={params[key]}' for key in sorted_keys])
print(f"\n签名字符串: {sign_string}")

result = api.login()
print(f"\n登录结果: {result}")
