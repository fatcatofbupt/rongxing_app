import requests
import json
import time
import pyrootutils
root = pyrootutils.setup_root(__file__, pythonpath=True)
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import config

class FinancialPlatformAPI:
    def __init__(self, base_url, app_id, private_key, username, password):
        """
        初始化API客户端
        :param base_url: 接口基础地址
        :param app_id: 应用ID
        :param private_key: 私钥字符串
        :param username: 用户名
        :param password: 密码
        """
        self.base_url = base_url.rstrip('/')
        self.app_id = app_id
        self.private_key = private_key
        self.username = username
        self.password = password
        self.access_token = None
        self.user_id = None
    
    def generate_signature(self, timestamp):
        """
        生成签名（严格遵循文档规则）
        :param timestamp: 毫秒级时间戳（有效期5分钟）
        :return: Base64编码的签名字符串
        """
        # 按字典序排序参数
        params = {
            'appId': self.app_id,    # 严格使用文档示例中的参数名
            'password': self.password,
            'timestamp': str(timestamp),
            'username': self.username
        }
        
        # 按字典序排序键并拼接
        sorted_keys = sorted(params.keys())
        sign_string = '&'.join([f'{key}={params[key]}' for key in sorted_keys])
        print(f"Sign String: {sign_string}")
        try:
            # 1. 对私钥进行Base64解码（关键修改）
            key_bytes = base64.b64decode(self.private_key.strip())
            # 2. 导入PKCS8格式私钥
            rsa_key = RSA.import_key(key_bytes)
            # 3. 计算SHA256哈希
            hash_obj = SHA256.new(sign_string.encode('utf-8'))
            # 4. 执行PKCS#1 v1.5签名
            signature = pkcs1_15.new(rsa_key).sign(hash_obj)
            # 5. 返回Base64编码结果
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            raise Exception(f"签名生成失败: {str(e)}")
    def login(self):
        """
        1.1 使用账号密码登录，获取token（严格遵循接口文档）
        """
        url = f"{self.base_url}/app-api/system/third/login"
        timestamp = int(time.time() * 1000)  # 毫秒级时间戳（有效期5分钟）
        
        # 确保密码为字符串类型（文档要求string类型）
        password_str = str(self.password) if self.password is not None else ""
        
        # 按文档参数顺序组织请求数据
        data = {
            "username": self.username,
            "password": password_str,      # 严格转为字符串
            "timestamp": timestamp,
            "appId": self.app_id,
            "sign": self.generate_signature(timestamp)
        }
        
        # 添加调试信息输出
        print(f"【登录请求】URL: {url}")
        print(f"【签名字符串】{self.generate_signature.__doc__.split('Sign String: ')[-1].strip()}")
        print(f"【请求数据】{json.dumps(data, indent=2)}")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            
            # 处理非200状态码（文档要求）
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    if 'msg' in error_detail:
                        error_msg += f": {error_detail['msg']}"
                except:
                    error_msg += f": {response.text[:200]}"
                print(f"【登录失败】{error_msg}")
                return False
            
            # 解析响应
            result = response.json()
            
            # 严格检查响应结构（文档要求）
            if 'code' not in result or 'msg' not in result or 'data' not in result:
                print("【响应格式错误】缺少必要字段(code/msg/data)")
                print(f"【实际响应】{json.dumps(result, indent=2)}")
                return False
            print(f"login result: {result}")
            # 处理业务错误（文档要求code=0表示成功）
            if result.get('code') != 200:
                print(f"【业务错误】{result.get('msg', '未知错误')} (code={result.get('code')})")
                return False
            
            # 处理成功响应
            self.access_token = result['data'].get('accessToken')
            self.user_id = str(result['data'].get('userId', ''))
            
            # 严格验证必要字段
            if not self.access_token or not self.user_id:
                print("【响应数据不完整】缺少accessToken或userId")
                return False
            
            print("【登录成功】")
            print(f"User ID: {self.user_id}")
            print(f"Access Token: {self.access_token[:10]}...{self.access_token[-10:]}")  # 部分显示
            return True
            
        except Exception as e:
            print(f"【请求异常】{str(e)}")
            import traceback
            print(f"【异常堆栈】{traceback.format_exc()}")
            return False
    def logout(self):
        """
        1.2 登出系统
        """
        if not self.access_token:
            print("未登录，无法登出")
            return False
            
        url = f"{self.base_url}/app-api/system/third/logout"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.post(url, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                print("登出成功！")
                self.access_token = None
                self.user_id = None
                return True
            else:
                print(f"登出失败: {result.get('msg', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"登出请求异常: {str(e)}")
            return False
    
    def batch_create_task(self, task_params):
        """
        1.3 批量下APP指标任务
        :param task_params: 任务参数列表
        :return: 任务ID
        """
        if not self.access_token:
            print("请先登录")
            return None
            
        url = f"{self.base_url}/app-api/system/third/checkAppTaskBatch"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = requests.post(url, json=task_params, headers=headers)
            result = response.json()
            print(f"【任务创建结果】:{result}")
            if response.status_code == 200 and result.get('code') == 200:
                task_id = result['data']
                print(f"任务创建成功！任务ID: {task_id}")
                return task_id
            else:
                print(f"任务创建失败: {result.get('msg', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"任务创建请求异常: {str(e)}")
            return None
    
    def decrypt_data(self, cipher_text):
        """
        解密数据
        :param cipher_text: 加密的文本
        :return: 解密后的JSON字符串
        """
        try:
            # 生成 AES key, 取 SHA-256 的前16字节
            sha256 = hashlib.sha256(self.user_id.encode('utf-8')).hexdigest()
            key = sha256[:16].encode('utf-8')
            
            # AES ECB模式解密
            cipher = AES.new(key, AES.MODE_ECB)
            
            # 解密前需要base64解码
            encrypted_bytes = base64.b64decode(cipher_text)
            
            # 解密并去掉padding
            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"数据解密失败: {str(e)}")
    
    def query_task_result(self, task_id, max_retries=1, retry_interval=5):
        """
        1.4 查询APP指标任务结果
        :param task_id: 任务ID
        :param max_retries: 最大重试次数
        :param retry_interval: 重试间隔(秒)
        :return: 任务结果
        """
        if not self.access_token:
            print("请先登录")
            return None
            
        url = f"{self.base_url}/app-api/system/third/queryAppTaskResult"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        params = {
            "taskId": task_id  # 注意文档中是taskld，但应该是taskId
        }
        
        for retry in range(max_retries):
            try:
                response = requests.get(url, params=params, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"【任务查询结果】:{result}")
                    if result.get('code') == 200:
                        encrypted_data = result['data']
                        # 解密数据
                        decrypted_data = self.decrypt_data(encrypted_data)
                        print("任务查询成功！")
                        return json.loads(decrypted_data)
                    else:
                        print(f"任务查询失败: {result.get('msg', '未知错误')}")
                        return None
                        
                elif response.status_code == 204:
                    print(f"任务进行中... ({retry + 1}/{max_retries})")
                    if retry < max_retries - 1:
                        time.sleep(retry_interval)
                    continue
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"任务查询请求异常: {str(e)}")
                return None
        
        print("任务查询超时")
        return None

# 使用示例
if __name__ == "__main__":
    # ==================== 配置信息 ====================
    # 请替换为您的实际信息
    BASE_URL = config.base_url
    APP_ID =config.appid
    PRIVATE_KEY = f"""
    -----BEGIN PRIVATE KEY-----
    {config.private_key}
    -----END PRIVATE KEY-----
    """
    PRIVATE_KEY = config.private_key
    USERNAME =config.username
    PASSWORD = config.password
    
    # ==================== 测试代码 ====================
    
    # 创建API客户端实例
    api = FinancialPlatformAPI(BASE_URL, APP_ID, PRIVATE_KEY, USERNAME, PASSWORD)
    
    # 1. 登录
    if api.login():
        # 2. 批量创建任务（示例：查询手机号）
        task_params = [
            {
                "idType": "010214",  # OAID（开放匿名设备标识符），Android 10+替代IMEI的标识
                "exid": "9b31d4b6-058c-4728-9c48-57a8b0c76330"  # 要查询的手机号
            }
            # {
            #     "idType": "010105",  # PHONE
            #     "exid": "15961798692"  # 要查询的手机号
            # }
            # 可以添加更多任务...
        ]
        
        # task_id = api.batch_create_task(task_params)
        # task_id = "2006183308746915841"
        task_id = "2006189742209466370"
        while True:
            print("等待任务完成...")
            
            result = api.query_task_result(task_id)
            if result:
                print("任务结果:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                break
            time.sleep(300)  # 等待一段时间再查询
        
        # 4. 登出
        api.logout()