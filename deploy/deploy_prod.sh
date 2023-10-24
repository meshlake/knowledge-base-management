#!/bin/bash

cd ../Server

# 构建Docker镜像
docker build -t harbor.dev.meshlake.com:8443/meshlake/knowledge-base-server:0.0.1 .

# 推送Docker镜像
docker push harbor.dev.meshlake.com:8443/meshlake/knowledge-base-server:0.0.1

cd ../Frontend

# 安装依赖
pnpm i

# 打包
pnpm run build

# 打包镜像,注意tag的版本号
docker build -t harbor.dev.meshlake.com:8443/meshlake/knowledge-base-web:0.0.1 .

# 推送镜像
docker push harbor.dev.meshlake.com:8443/meshlake/knowledge-base-web:0.0.1

cd ../deploy

# 部署
kubectl replace --force -f server.yaml
kubectl replace --force -f web.yaml
