import aiohttp
import asyncio
import os

async def upload_image(image_path: str, api_key: str):
    """上传图片到服务器"""
    if not os.path.exists(image_path):
        print(f"错误：找不到图片文件 {image_path}")
        return

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
            if response.status == 200:
                result = await response.json()
                print("上传成功:", result['message'])
            else:
                print(f"上传失败: HTTP {response.status}")
                print(await response.text())

async def download_image(save_path: str, server_url: str = "http://localhost:8000"):
    """从服务器下载图片"""
    async with aiohttp.ClientSession() as session:
        try:
            # 发送GET请求
            async with session.get(f"{server_url}/get_image") as response:
                if response.status == 200:
                    # 异步写入文件
                    with open(save_path, 'wb') as f:
                        while True:
                            chunk = await response.content.read(8192)  # 分块读取
                            if not chunk:
                                break
                            f.write(chunk)
                    print(f"下载成功，已保存到: {save_path}")
                else:
                    print(f"下载失败: HTTP {response.status}")
                    print(await response.text())
        except Exception as e:
            print(f"下载出错: {str(e)}")

async def main():
    # 上传示例
    await upload_image("test.png", "your-secret-api-key")  # 替换为你的图片路径和API密钥
    
    # 下载示例
    await download_image("downloaded.png")

if __name__ == "__main__":
    # 安装依赖：pip install aiohttp
    asyncio.run(main()) 