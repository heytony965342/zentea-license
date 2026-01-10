FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

# 1. 替换 Debian 系统源为阿里云镜像（加速 apt-get）
# 使用 sed 命令将默认源替换为 mirrors.aliyun.com
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. 升级 pip 并预装基础构建工具
# 已经通过 ENV 设置了全局 PIP_INDEX_URL，无需在命令中重复指定 -i
RUN pip install --upgrade pip setuptools wheel

# 3. 安装项目依赖
# 这一步单独出来是为了充分利用 Docker 的层缓存
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. 复制应用代码
COPY . .

EXPOSE 8001

CMD ["python", "run.py"]