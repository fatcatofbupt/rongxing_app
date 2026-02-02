from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import uuid
from typing import Dict, List
import time
import json
import config
from typing import Dict, List, Optional
# 导入修改后的 FinancialPlatformAPI 类
from loguru import logger
from main import FinancialPlatformAPI

app = FastAPI(title="金融平台API代理服务")

# 会话存储 (生产环境应使用Redis等持久化存储)
_sessions: Dict[str, FinancialPlatformAPI] = {}

# 配置模型
class ReqPasswordModel(BaseModel):
    password: str

# 信用指标任务参数模型
class CreditTaskParam(BaseModel):
    """信用指标任务参数模型，对应文档1.7接口"""
    originalJson: Optional[str] = "{}"
    name: str
    idCard: str
    phone: str

# 设备信息任务参数模型 (1.3)
class DeviceTaskParam(BaseModel):
    """设备信息任务参数模型，对应文档1.3接口"""
    idType: str  # 010105=PHONE, 010207=IMEI, 010208=IMSI, 010209=MAC, 010213=IDFA, 010214=OAID
    exid: str    # 查询内容

# 会话ID依赖
def get_session_id(session_id: str):
    return session_id

# API实例依赖
def get_api_instance(session_id: str = Depends(get_session_id)):
    if session_id in _sessions:
        return _sessions[session_id]
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的会话ID"
    )

@app.post("/init", response_model=dict)
async def init_session(req: ReqPasswordModel):
    """初始化会话"""
    if req.password != "123456":
    # if req.password != config.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误"
        )
    try:
        api = FinancialPlatformAPI(
            config.base_url,
            config.app_id,
            config.private_key,
            config.username,
            config.password
        )
        session_id = str(uuid.uuid4())
        api.session_id = session_id  # 设置 session_id 用于日志关联
        _sessions[session_id] = api
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"初始化失败: {str(e)}"
        )

@app.post("/login/{session_id}", response_model=dict)
async def login(api: FinancialPlatformAPI = Depends(get_api_instance)):
    """执行登录操作"""
    if api.login():
        return {"status": "success", "message": "登录成功"}
    return {"status": "error", "message": "登录失败"}

@app.post("/logout/{session_id}", response_model=dict)
async def logout(api: FinancialPlatformAPI = Depends(get_api_instance)):
    """执行登出操作"""
    if api.logout():
        return {"status": "success", "message": "登出成功"}
    return {"status": "error", "message": "登出失败"}

@app.post("/create_credit_task/{session_id}", response_model=dict)
async def create_credit_task(
    tasks: List[CreditTaskParam],
    api: FinancialPlatformAPI = Depends(get_api_instance)
):
    """
    批量创建信用指标任务（对应文档1.7）
    创建后直接返回解密后的信用评分结果
    """
    task_params = [{
        "originalJson": task.originalJson,
        "name": task.name,
        "idCard": task.idCard,
        "phone": task.phone
    } for task in tasks]

    # 调用异步方法
    result = await api.batch_create_credit_task(task_params)
    return result

@app.post("/create_device_task/{session_id}", response_model=dict)
async def create_device_task(
    tasks: List[DeviceTaskParam],
    api: FinancialPlatformAPI = Depends(get_api_instance)
):
    """
    批量创建设备信息任务（对应文档1.3）
    idType: 010105=PHONE, 010207=IMEI, 010208=IMSI, 010209=MAC, 010213=IDFA, 010214=OAID
    """
    task_params = [{"idType": task.idType, "exid": task.exid} for task in tasks]
    result = await api.batch_create_device_task(task_params)
    return result

@app.get("/query_device_task/{session_id}", response_model=dict)
async def query_device_task(
    task_id: str,
    max_retries: int = 1,
    retry_interval: int = 5,
    api: FinancialPlatformAPI = Depends(get_api_instance)
):
    """
    查询APP任务结果（对应文档1.4）
    使用异步HTTP请求，直接转发原始响应
    """
    result = await api.query_device_task_result(task_id, max_retries, retry_interval)
    return result

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("FastAPI应用启动")

@app.on_event("shutdown")
async def shutdown_event():
    """清理会话和资源"""
    # 关闭所有 API 实例的会话
    for session_id, api in _sessions.items():
        if hasattr(api, 'close_session'):
            await api.close_session()
        if api.access_token:
            api.logout()  # 同步登出
    
    # 清空会话存储
    _sessions.clear()
    logger.info("已清理所有会话")