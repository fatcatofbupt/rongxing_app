#!/usr/bin/env python3
"""
调试登录 - 查看原始响应
"""
import requests

BASE_URL = "http://localhost:32461"

# 1. 初始化
resp = requests.post(f"{BASE_URL}/init", json={"password": "123456"})
session_id = resp.json()["session_id"]
print(f"Session: {session_id}\n")

# 2. 登录并打印原始响应
print("登录响应:")
resp = requests.post(f"{BASE_URL}/login/{session_id}")
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.json()}")
