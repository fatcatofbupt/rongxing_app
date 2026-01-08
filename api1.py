from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import uuid
from typing import Dict, List
import time
import json
import config
from typing import Dict, List, Optional  # 添加Optional
# 导入您提供的 FinancialPlatformAPI 类
from main import FinancialPlatformAPI

app = FastAPI(title="金融平台API代理服务")

# 会话存储 (生产环境应使用Redis等持久化存储)
_sessions: Dict[str, FinancialPlatformAPI] = {}

# 配置模型
class ReqPasswordModel(BaseModel):
    # base_url: str
    # app_id: str
    # private_key: str
    # username: str
    password: str

# 任务参数模型
class TaskParam(BaseModel):
    # idType: str
    # exid: str
    phone_number: str
# 信用指标任务参数模型
class CreditTaskParam(BaseModel):
    """信用指标任务参数模型，对应文档1.5接口"""
    originalJson: Optional[str] = None
    name: str
    idCard: str
    phone: str

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

# @app.post("/create_task/{session_id}", response_model=dict)
# async def create_task(
#     tasks: List[TaskParam], 
#     api: FinancialPlatformAPI = Depends(get_api_instance)
# ):
#     """批量创建任务"""
#     '''
#      # idType: str
#     # exid: str
#     phone_number: str
#     '''
#     task_params = [dict(idType="010105", exid=task.phone_number) for task in tasks]
#     task_id,msg = api.batch_create_task(task_params)
#     if task_id:
#         return {"status": "success", "task_id": task_id}
#     return {"status": "error", "message": msg}

# @app.get("/query_task/{session_id}", response_model=dict)
# async def query_task(
#     task_id: str,
#     max_retries: int = 1,
#     retry_interval: int = 5,
#     api: FinancialPlatformAPI = Depends(get_api_instance)
# ):
#     """查询任务结果"""
#     result, msg = api.query_task_result(task_id, max_retries, retry_interval)
#     if result:
#         return {"status": "success", "result": result }
#     return {"status": "error", "message": msg}
@app.post("/create_credit_task/{session_id}", response_model=dict)
async def create_credit_task(
    tasks: List[CreditTaskParam], 
    api: FinancialPlatformAPI = Depends(get_api_instance)
):
    """批量创建信用指标任务（对应文档1.5）"""
    task_params = [{
        "originalJson": task.originalJson,
        "name": task.name,
        "idCard": task.idCard,
        "phone": task.phone
    } for task in tasks]
    
    return  api.batch_create_credit_task(task_params)
 
@app.get("/query_credit_task/{session_id}", response_model=dict)
async def query_credit_task(
    task_id: str,
    max_retries: int = 1,
    retry_interval: int = 5,
    api: FinancialPlatformAPI = Depends(get_api_instance)
):
    """查询信用指标任务结果（对应文档1.6）"""
    return  api.query_credit_task_result(task_id, max_retries, retry_interval)
@app.on_event("shutdown")
async def shutdown_event():
    """清理会话"""
    for api in _sessions.values():
        if api.access_token:
            api.logout()