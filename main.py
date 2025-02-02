import asyncio
import os
import warnings

import aiofiles
from PIL import Image, ImageDraw
from fastapi import FastAPI, UploadFile, HTTPException, Depends
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

app = FastAPI()

# 创建异步锁
image_lock = asyncio.Lock()
# 用于存储图片的文件路径
IMAGE_PATH = "stored_image.png"

# 创建安全认证方案
security = HTTPBearer()

# 从环境变量获取API密钥，如果未设置则使用默认值
DEFAULT_API_KEY = "development-insecure-key"
API_KEY = os.getenv("API_KEY", DEFAULT_API_KEY)

# 如果使用默认值，输出警告
if API_KEY == DEFAULT_API_KEY:
    warnings.warn(
        "警告: 使用默认的API密钥。在生产环境中，请通过环境变量设置安全的API密钥。",
        RuntimeWarning
    )


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证API密钥"""
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@app.post("/update_image")
async def upload_image(
        file: UploadFile,
        api_key: str = Depends(verify_api_key)  # 添加API密钥验证
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="文件必须是图片格式")

    # 使用异步锁确保同一时间只有一个写操作
    async with image_lock:
        try:
            # 异步读取上传的文件内容
            content = await file.read()
            # 异步写入文件
            async with aiofiles.open(IMAGE_PATH, 'wb') as f:
                await f.write(content)
            return {"message": "图片上传成功"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.get("/get_image")
async def get_image():
    # 使用异步锁确保在读取时文件不会被修改
    async with image_lock:
        try:
            # 检查文件是否存在
            if not os.path.exists(IMAGE_PATH):
                # 返回一个默认的"无图片"提示图片或者404错误
                default_image_path = "default_no_image.png"
                if os.path.exists(default_image_path):
                    async with aiofiles.open(default_image_path, 'rb') as f:
                        content = await f.read()
                        return Response(content=content, media_type="image/png")
                else:
                    raise HTTPException(
                        status_code=404,
                        detail="还没有上传任何图片，且默认图片不存在"
                    )

            # 异步读取文件
            async with aiofiles.open(IMAGE_PATH, 'rb') as f:
                content = await f.read()
                return Response(content=content, media_type="image/png")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"读取失败: {str(e)}")


@app.on_event("startup")
async def startup_event():
    # 确保启动时图片目录存在
    os.makedirs(os.path.dirname(IMAGE_PATH) if os.path.dirname(IMAGE_PATH) else '.', exist_ok=True)

    # 如果需要，创建默认的"无图片"提示图片
    default_image_path = "default_no_image.png"
    if not os.path.exists(default_image_path):
        try:
            img = Image.new('RGB', (200, 100), color='white')
            d = ImageDraw.Draw(img)
            d.text((100, 50), "404", fill='black')
            img.save(default_image_path)
        except Exception as e:
            print(f"创建默认图片失败: {str(e)}")
