#!/usr/bin/env python3
"""
直接测试远程金融平台服务器登录
"""
import requests
import time
import base64
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# 远程服务器配置
TARGET_URL = "http://192.168.3.53:48080"
USERNAME = "lvguangzhineng"
PASSWORD = "zhineng@123789!#"
APP_ID = "lvguang123"
PRIVATE_KEY = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCyfKyVUfrHQBdDHHbGcCvlDBp4vn6fegRJ1wneGv3pb7hlHpVOo4q865uNwFbijb0z3hkIW2Eh11QkGskPCPhp9pKehgxBUa4C7uRBHAAn+j/YLD3t0fOBJSQjyw9oUqb7wUJl3HG+0PJBVjMCkFkpy6o8Y/LZPP9WJQJcPNuOEvljAft2xsOa5+Vr7SJaMmzvLi5FgGEWN1GgXWhGcLimQ3BvjjjfSfyAlVXd89M89b9cUPcSKXPG7cqBzxmyebnrED29nJfti7UzO19n3aNXh6To/aEZYOzN2boLSyUifORDnn4HlPghhrGRXoCKwVZVHPM4qUX/+TC4YOPtvMW9AgMBAAECggEANAWlkbH+u2NhRFTAA69/A7fm4Ul4g4ffRxxPinZoikjfQE3NK8n77ntnb8XfLRIt0rfJqQdlRKVLp2hNML4nFU9iRaUBXmptovo4+gcsvnowcJPYiv/2Dq6iHXKab4gjll4qOaEqX/jrmwKCRJ2I92cem5JwHkQqkdOgn/y26238tvqjbLMXzTNib+6Kmm6YRYscQkkrbQeg/lg9qmQDNOj6F1M5HEBVU0jqHXFqdUYqub43+lKjCvVId7QLD7Oe3TPbUlLfFLLYBIy8O5utX9BFeljtqgvsv0pRYDk3Gwk6cDA2uQBle0tojD+5NpY84cOf9LS+FumteQm7kb/cCwKBgQDYnXu7YSFUNZGgflByNKMsGG3KbNEVv2qPd1mdtUcIQY/2xo/9AoQFRbFSP4Q/x8jZA0r7J1+eZypM965UQYE9m4Rq6ohz3Mjrz7iaZCYQi8v0T7Pvr72LifJbds03OFxvL508/JF/u1fpcCXNNi6/YMjE/PBOJ92MMoozTgcYHwKBgQDS8Hydkq/+9+7pFgvkNR3jlB4v6+JaeVs8WPACeNsT6V9iQYt8a6yAMOxKkJPiMvsVkIP18iorZORrmd5d95lRBISxfAJpRCb24i8YuChFliZQHZTFeB4zDwStdtT1RpAvJ2OUZrBe8i60FbgHDkXKFw21n5sLRLcFdQy9NyJWowKBgDpp1XkFS2CTBY9bIMR7b1kvyUOiLowHz2uayr7dqKcQTwtEJoYbDJEDZzr/x+EPNhlXavvpdT6ZIW4aCJfOBlUfwAi48E0WR9RXcrentCAYIsriR2qmYJ3leEaz9ckjWMHe/C77CR2B3sYjqP3604ZmSh3c+8yHsZXh9yS4sO8PAoGAat/n85pfy4ppJPXDnqN++lCQnu0f6YE1RbU2HbqIHWWPq2PUPXz8kJK5Fep80w3Lg5iOE63Xyda7mP0D2o5Zwt/ML3TKb/VU3J+rBxY/aUpzLQJf31FF087XKuBbc86FvS5y2LzSvbhtC1c5v3Fu0L6vdodgcewl4wD0LGZj4osCgYA7HCL/zCi62tOlZj1LZGc6ofFPCcUw8VsYCrJt+SW1vKROxXk26KlJ800qmmTB5Ir514BbRJj8Vv9Sf2HfM3lndtLspiLJszhp4qkAxIeI5GruUumEdutv8u7XTWgWu7nhcIJm7XWsVGVhxVlizWFZNOjpNd3q/4lwOH9jSoKC7Q=="


def generate_signature(timestamp):
    """生成签名"""
    params = {
        'appId': APP_ID,
        'password': str(PASSWORD),
        'timestamp': str(timestamp),
        'username': USERNAME
    }
    sorted_keys = sorted(params.keys())
    sign_string = '&'.join([f'{key}={params[key]}' for key in sorted_keys])
    print(f"签名字符串: {sign_string}")

    key_bytes = base64.b64decode(PRIVATE_KEY.strip())
    rsa_key = RSA.import_key(key_bytes)
    hash_obj = SHA256.new(sign_string.encode('utf-8'))
    signature = pkcs1_15.new(rsa_key).sign(hash_obj)
    return base64.b64encode(signature).decode('utf-8')


def test_direct_login():
    """直接测试远程服务器登录"""
    print("=" * 50)
    print("直接测试远程服务器登录")
    print(f"目标: {TARGET_URL}/app-api/system/third/login")
    print("=" * 50)

    url = f"{TARGET_URL}/app-api/system/third/login"
    timestamp = int(time.time() * 1000)

    data = {
        "username": USERNAME,
        "password": str(PASSWORD),
        "timestamp": timestamp,
        "appId": APP_ID,
        "sign": generate_signature(timestamp)
    }

    print(f"\n请求数据: {data}")
    print("\n发送请求...")

    resp = requests.post(url, json=data, headers={"Content-Type": "application/json"})

    print(f"\n状态码: {resp.status_code}")
    print(f"响应: {resp.json()}")

    result = resp.json()

    # 检查返回的 code
    code = result.get('code')
    print(f"\n后端返回的 code: {code}")

    if code == 200:
        print("✓ 登录成功！")
        print(f"  userId: {result['data'].get('userId')}")
        print(f"  accessToken: {result['data'].get('accessToken')}")
    elif code == 0:
        print("✓ 登录成功！ (code=0)")
        print(f"  userId: {result['data'].get('userId')}")
        print(f"  accessToken: {result['data'].get('accessToken')}")
    else:
        print(f"✗ 登录失败: {result.get('msg')} (code={code})")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_direct_login()
