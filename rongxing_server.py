import uvicorn
from api import app  # 假设上面的代码保存在api.py中

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=32461)