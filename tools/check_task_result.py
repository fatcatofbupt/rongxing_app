import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 直接访问目标服务
TARGET_BASE_URL = "http://192.168.3.53:48080"


def query_task_result(access_token: str, task_id: str) -> dict:
    """
    直接查询信用指标任务结果

    Args:
        access_token: 访问令牌
        task_id: 任务ID

    Returns:
        任务结果字典（已自动解密）
    """
    url = f"{TARGET_BASE_URL}/app-api/system/third/queryCreditTaskResult"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"taskId": task_id}

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    result = response.json()
    print(result)
    # 自动解密数据
    encrypted_data = result.get('data')
    print(encrypted_data)
    if encrypted_data:
        result['data'] = _decrypt_data(encrypted_data)
    print(result)
    return result


def _decrypt_data(cipher_text: str, user_id: str = None) -> str:
    """解密数据（AES-256 ECB）"""
    try:
        # 生成 AES key: SHA-256 的前16字节
        sha256 = hashlib.sha256(user_id.encode('utf-8')).hexdigest() if user_id else hashlib.sha256(b'').hexdigest()
        key = sha256[:16].encode('utf-8')

        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_bytes = base64.b64decode(cipher_text)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)

        return decrypted_bytes.decode('utf-8')
    except Exception:
        # 解密失败时返回原始数据
        return cipher_text


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print(f"Usage: python {sys.argv[0]} <access_token> <task_id>")
    #     sys.exit(1)

    access_token = "436c65d3ad5b405c8c31746cb0fc1fe3"
    task_id = "2017088101078118401"

    result = query_task_result(access_token, task_id)
    print(result)
