# SingleImageSavingAPI

一个简单的FastAPI应用，用于保存和获取单个图片。该API支持通过POST请求更新图片，通过GET请求获取图片，并使用Bearer Token进行认证。

## 功能特点

- 支持单个图片的保存和获取
- 使用Bearer Token进行API认证
- 异步处理请求
- 并发安全
- 支持Docker部署
- 当无图片时返回默认提示图片

## 快速开始

### 使用Docker

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/SingleImageSavingAPI.git
cd SingleImageSavingAPI
```

2. 使用Docker Compose启动服务：

```bash
docker-compose up -d
```

### 本地开发

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行服务：

```bash
uvicorn main:app --reload
```

## API 使用说明

### 更新图片

```http
POST /update_image
Authorization: Bearer your-api-key
Content-Type: multipart/form-data
```

请求示例：
```bash
curl -X POST \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@test.png" \
  http://localhost:8000/update_image
```

### 获取图片

```http
GET /get_image
```

请求示例：
```bash
curl http://localhost:8000/get_image --output image.png
```

## 配置

### 环境变量

- `API_KEY`: API认证密钥（可选，默认值：development-insecure-key）

## 项目结构

```
SingleImageSavingAPI/
├── main.py              # 主应用代码
├── requirements.txt     # Python依赖
├── Dockerfile          # Docker配置文件
├── docker-compose.yml  # Docker Compose配置
├── test_main.http     # HTTP请求测试文件
└── README.md          # 项目文档
```

## 开发

### 测试API

使用提供的 `test_main.http` 文件（需要VS Code的REST Client扩展）或者使用curl命令进行测试。

### Python客户端示例

```python
import aiohttp
import asyncio

async def upload_image(image_path: str, api_key: str):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {api_key}"}
        data = aiohttp.FormData()
        data.add_field('file',
                      open(image_path, 'rb'),
                      filename='test.png',
                      content_type='image/png')
        
        async with session.post(
            "http://localhost:8000/update_image",
            headers=headers,
            data=data
        ) as response:
            return await response.json()

async def download_image(save_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/get_image") as response:
            with open(save_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
```

## 注意事项

- 在生产环境中请务必设置安全的API密钥
- 服务重启后图片不会保持
- 仅支持保存一张图片，新上传的图片会覆盖旧图片