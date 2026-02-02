# 金融平台 API 代理服务

基于 FastAPI 的代理服务，用于安全访问金融平台 API，提供信用指标任务管理功能。

## 项目功能

- **会话管理**：初始化会话、登录、登出
- **信用指标任务**：批量创建任务、查询任务结果
- **数据解密**：自动解密 AES-256 ECB 加密的响应数据
- **签名认证**：RSA-SHA256 签名确保请求安全

## 项目结构

```
rongxing/
├── api.py                      # FastAPI 应用，包含所有 REST API 端点
├── main.py                     # FinancialPlatformAPI 核心类
├── config.py                   # 配置文件（密钥、凭据等）
├── rongxing_server.py          # 服务启动入口
├── start.sh                    # 启动脚本（后台运行）
├── start_vpn.sh                # VPN 连接脚本
├── tools/
│   └── check_task_result.py    # 查询任务结果工具
├── deps/
│   ├── configs.txt             # 配置文件备份
│   └── *.pdf                   # 接口文档
├── CLAUDE.md                   # Claude Code 开发指南
└── README.md                   # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pydantic aiohttp requests loguru pycryptodome pyrootutils
```

### 2. 启动服务

```bash
# 方法1：直接启动
python rongxing_server.py [端口]

# 方法2：使用启动脚本
./start.sh [端口]

# 默认端口：32461
```

### 3. VPN 连接（内网访问）

如需访问内网服务，先连接 VPN：

```bash
./start_vpn.sh
```

## API 接口

### 1. 初始化会话

```http
POST /init
Content-Type: application/json

{
    "password": "123456"
}
```

**响应：**
```json
{
    "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### 2. 登录

```http
POST /login/{session_id}
```

**响应：**
```json
{
    "status": "success",
    "message": "登录成功"
}
```

### 3. 登出

```http
POST /logout/{session_id}
```

### 4. 批量创建信用指标任务

```http
POST /create_credit_task/{session_id}
Content-Type: application/json

[
    {
        "originalJson": "",
        "name": "张三",
        "idCard": "110101199001011234",
        "phone": "13800138000"
    }
]
```

### 5. 查询任务结果

```http
GET /query_credit_task/{session_id}?task_id=xxx&max_retries=3&retry_interval=5
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |
| task_id | string | 是 | 任务ID |
| max_retries | int | 否 | 最大重试次数，默认1 |
| retry_interval | int | 否 | 重试间隔(秒)，默认5 |

## 使用工具查询任务结果

### 方法1：命令行

```bash
python tools/check_task_result.py <access_token> <task_id>
```

### 方法2：导入使用

```python
from tools.check_task_result import query_task_result

result = query_task_result("your-access-token", "task_id")
print(result)
```

## 认证机制

### 登录签名流程

1. 按参数名排序：`appId`, `password`, `timestamp`, `username`
2. 拼接签名字符串：`appId=xxx&password=xxx&timestamp=xxx&username=xxx`
3. 使用 RSA 私钥对签名字符串进行 SHA-256 签名
4. Base64 编码签名结果

### 请求头认证

登录成功后，后续请求需携带：

```
Authorization: Bearer {access_token}
```

## 数据加密

响应数据使用 AES-256 ECB 模式加密：

- **密钥生成**：`SHA-256(user_id)` 的前 16 字节
- **解密流程**：Base64 解码 → AES 解密 → 去除 PKCS7 padding

解密在 `query_credit_task_result` 方法中自动完成。

## 配置说明

在 [config.py](config.py) 中配置：

| 配置项 | 说明 |
|--------|------|
| `base_url` | 目标 API 基础地址 |
| `app_id` | 应用ID |
| `username` | 用户名 |
| `password` | 密码 |
| `private_key` | Base64 编码的 RSA 私钥 |

## 会话管理

- 当前使用内存存储会话 (`Dict[str, FinancialPlatformAPI]`)
- 生产环境建议使用 Redis 持久化存储
- 服务关闭时自动清理所有会话

## 日志

使用 `loguru` 记录日志，默认输出到控制台，可配置输出到文件。

## License

内部使用
