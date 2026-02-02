import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import base64
import time
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 配置
TARGET_BASE_URL = "http://192.168.3.53:48080"
APP_ID = "lvguang123"
USERNAME = "lvguangzhineng"
PASSWORD = "zhineng@123789!#"
PRIVATE_KEY = "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCyfKyVUfrHQBdDHHbGcCvlDBp4vn6fegRJ1wneGv3pb7hlHpVOo4q865uNwFbijb0z3hkIW2Eh11QkGskPCPhp9pKehgxBUa4C7uRBHAAn+j/YLD3t0fOBJSQjyw9oUqb7wUJl3HG+0PJBVjMCkFkpy6o8Y/LZPP9WJQJcPNuOEvljAft2xsOa5+Vr7SJaMmzvLi5FgGEWN1GgXWhGcLimQ3BvjjjfSfyAlVXd89M89b9cUPcSKXPG7cqBzxmyebnrED29nJfti7UzO19n3aNXh6To/aEZYOzN2boLSyUifORDnn4HlPghhrGRXoCKwVZVHPM4qUX/+TC4YOPtvMW9AgMBAAECggEANAWlkbH+u2NhRFTAA69/A7fm4Ul4g4ffRxxPinZoikjfQE3NK8n77ntnb8XfLRIt0rfJqQdlRKVLp2hNML4nFU9iRaUBXmptovo4+gcsvnowcJPYiv/2Dq6iHXKab4gjll4qOaEqX/jrmwKCRJ2I92cem5JwHkQqkdOgn/y26238tvqjbLMXzTNib+6Kmm6YRYscQkkrbQeg/lg9qmQDNOj6F1M5HEBVU0jqHXFqdUYqub43+lKjCvVId7QLD7Oe3TPbUlLfFLLYBIy8O5utX9BFeljtqgvsv0pRYDk3Gwk6cDA2uQBle0tojD+5NpY84cOf9LS+FumteQm7kb/cCwKBgQDYnXu7YSFUNZGgflByNKMsGG3KbNEVv2qPd1mdtUcIQY/2xo/9AoQFRbFSP4Q/x8jZA0r7J1+eZypM965UQYE9m4Rq6ohz3Mjrz7iaZCYQi8v0T7Pvr72LifJbds03OFxvL508/JF/u1fpcCXNNi6/YMjE/PBOJ92MMoozTgcYHwKBgQDS8Hydkq/+9+7pFgvkNR3jlB4v6+JaeVs8WPACeNsT6V9iQYt8a6yAMOxKkJPiMvsVkIP18iorZORrmd5d95lRBISxfAJpRCb24i8YuChFliZQHZTFeB4zDwStdtT1RpAvJ2OUZrBe8i60FbgHDkXKFw21n5sLRLcFdQy9NyJWowKBgDpp1XkFS2CTBY9bIMR7b1kvyUOiLowHz2uayr7dqKcQTwtEJoYbDJEDZzr/x+EPNhlXavvpdT6ZIW4aCJfOBlUfwAi48E0WR9RXcrentCAYIsriR2qmYJ3leEaz9ckjWMHe/C77CR2B3sYjqP3604ZmSh3c+8yHsZXh9yS4sO8PAoGAat/n85pfy4ppJPXDnqN++lCQnu0f6YE1RbU2HbqIHWWPq2PUPXz8kJK5Fep80w3Lg5iOE63Xyda7mP0D2o5Zwt/ML3TKb/VU3J+rBxY/aUpzLQJf31FF087XKuBbc86FvS5y2LzSvbhtC1c5v3Fu0L6vdodgcewl4wD0LGZj4osCgYA7HCL/zCi62tOlZj1LZGc6ofFPCcUw8VsYCrJt+SW1vKROxXk26KlJ800qmmTB5Ir514BbRJj8Vv9Sf2HfM3lndtLspiLJszhp4qkAxIeI5GruUumEdutv8u7XTWgWu7nhcIJm7XWsVGVhxVlizWFZNOjpNd3q/4lwOH9jSoKC7Q=="


def generate_signature(timestamp):
    """生成RSA签名"""
    params = {
        'appId': APP_ID,
        'password': PASSWORD,
        'timestamp': str(timestamp),
        'username': USERNAME
    }
    sorted_keys = sorted(params.keys())
    sign_string = '&'.join([f'{key}={params[key]}' for key in sorted_keys])

    key_bytes = base64.b64decode(PRIVATE_KEY.strip())
    rsa_key = RSA.import_key(key_bytes)
    hash_obj = SHA256.new(sign_string.encode('utf-8'))
    signature = pkcs1_15.new(rsa_key).sign(hash_obj)
    return base64.b64encode(signature).decode('utf-8')


def login() -> tuple:
    """
    登录获取 access_token 和 user_id

    Returns:
        (access_token, user_id)
    """
    url = f"{TARGET_BASE_URL}/app-api/system/third/login"
    timestamp = int(time.time() * 1000)

    data = {
        "username": USERNAME,
        "password": str(PASSWORD),
        "timestamp": timestamp,
        "appId": APP_ID,
        "sign": generate_signature(timestamp)
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    result = response.json()

    if result.get('code') != 200:
        raise Exception(f"登录失败: {result.get('msg')}")

    access_token = result['data']['accessToken']
    user_id = str(result['data']['userId'])

    print(f"[登录成功] user_id: {user_id}")
    print(f"[登录成功] access_token: {access_token}")

    return access_token, user_id


def submit_task(access_token: str, tasks: list) -> dict:
    """
    批量创建信用指标任务

    Args:
        access_token: 访问令牌
        tasks: 任务列表

    Returns:
        响应结果
    """
    url = f"{TARGET_BASE_URL}/app-api/system/third/checkCreditTaskBatch"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    request_body = [{
        "originalJson": item.get("originalJson", ""),
        "name": item["name"],
        "idCard": item["idCard"],
        "phone": item["phone"]
    } for item in tasks]

    response = requests.post(url, json=request_body, headers=headers)
    response.raise_for_status()
    return response.json()


def decrypt_data(cipher_text: str, user_id: str) -> str:
    """解密数据（AES-256 ECB）"""
    sha256 = hashlib.sha256(user_id.encode('utf-8')).hexdigest()
    key = sha256[:16].encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_bytes = base64.b64decode(cipher_text)
    decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted_bytes.decode('utf-8')


def query_task_result(access_token: str, task_id: str, user_id: str) -> dict:
    """查询任务结果"""
    url = f"{TARGET_BASE_URL}/app-api/system/third/queryCreditTaskResult"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"taskId": task_id}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    result = response.json()

    # 解密数据
    encrypted_data = result.get('data')
    if encrypted_data:
        result['data'] = decrypt_data(encrypted_data, user_id)

    return result


def run(tasks: list):
    """
    执行完整的登录和任务提交流程

    Args:
        tasks: 任务列表，每项包含 name, idCard, phone
    """
    # 1. 登录
    access_token, user_id = login()
    print()

    # 2. 提交任务
    print(f"[提交任务] 共 {len(tasks)} 条")
    result = submit_task(access_token, tasks)
    print(f"[提交结果] {result}")
    print()

    # 3. 查询任务结果
    task_id = result.get('data')
    if task_id:
        print(f"[查询结果] task_id: {task_id}")
        query_result = query_task_result(access_token, task_id, user_id)
        print(f"[查询响应] {query_result}")
    else:
        print("[警告] 未返回 task_id")

    return result


if __name__ == "__main__":
    # 示例任务数据
    tasks = [
        {
            "originalJson": "",
            "name": "张三",
            "idCard": "110101199001011234",
            "phone": "13800138000"
        }
    ]

    run(tasks)
