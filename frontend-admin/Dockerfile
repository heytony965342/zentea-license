# Stage 1: Build stage
FROM node:20-alpine AS builder

# 设置 npm 国内镜像源环境变量
ENV NODE_MIRROR=https://npmmirror.com/mirrors/node \
    NPM_CONFIG_REGISTRY=https://registry.npmmirror.com

WORKDIR /app

# 1. 优化依赖安装缓存
# 复制 package.json 和 lock 文件（如果有）
COPY package.json package-lock.json* ./

# 2. 安装依赖
# 使用 npmmirror 加速，并只安装生产环境依赖（如果 build 不需要 devDeps）
# 如果遇到需要编译的 C++ 库，建议在这一步前 apk add --no-cache python3 make g++
RUN npm install --frozen-lockfile

# 3. 复制源码并构建
COPY . .
RUN chmod -R +x node_modules/.bin/
RUN npm run build

# Stage 2: Production stage
FROM nginx:alpine

# 1. 修改系统时区 (可选，方便查看日志)
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 2. 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 3. 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# 使用 healthcheck 确保容器健康 (可选)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]