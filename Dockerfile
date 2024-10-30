# 使用官方的 Python 轻量镜像
FROM python:3.12-slim

# 设置容器内的工作目录
# 在容器中创建并设置工作目录为 /app。所有接下来的操作（复制文件、安装依赖等）都会在这个目录下进行
WORKDIR /app

# 复制 requirements.txt 并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Uvicorn
RUN pip install uvicorn

# 复制项目的所有文件到容器工作目录
# 将当前目录的所有内容复制到容器的 /app 目录中，包括你的 FastAPI 应用代码
COPY . .

# 暴露应用的端口
# 这个声明是为了告诉 Docker 让外界知道可以通过这个端口访问应用
EXPOSE 8000

# 启动 FastAPI 应用, 告诉系统用 Uvicorn 来运行应用
# main:app：指明要运行的应用对象。
# main 是 Python 文件的名称（即 main.py）。
# app 是在 main.py 中定义的 FastAPI 实例
# --host 0.0.0.0 / --port 8000
CMD ["uvicorn", "Main:app", "--host", "0.0.0.0", "--port", "8000"]