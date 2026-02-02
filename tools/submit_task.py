import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

# 直接访问目标服务
TARGET_BASE_URL = "http://192.168.3.53:48080"


def submit_task(access_token: str, tasks: list) -> dict:
    """
    批量创建信用指标任务

    Args:
        access_token: 访问令牌
        tasks: 任务列表，每项包含 name, idCard, phone, originalJson(可选)

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <access_token> [json_file]")
        print("  Or use default test data if no json_file provided")
        sys.exit(1)

    access_token = sys.argv[1]

    if len(sys.argv) >= 3:
        # 从文件读取任务列表
        import json
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    else:
        # 默认测试数据
        tasks = [
            {
                "originalJson": "",
                "name": "张三",
                "idCard": "110101199001011234",
                "phone": "13800138000"
            }
        ]

    result = submit_task(access_token, tasks)
    print(result)
