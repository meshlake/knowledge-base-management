#!/bin/bash

cd ../Server

# 构建Docker镜像
docker build -t harbor.dev.meshlake.com:8443/meshlake/knowledge-base-server:test .

# 推送Docker镜像
docker push harbor.dev.meshlake.com:8443/meshlake/knowledge-base-server:test

cd ../Frontend

# 安装依赖
pnpm i

# 打包
pnpm run build

# 打包镜像,注意tag的版本号
docker build -t harbor.dev.meshlake.com:8443/meshlake/knowledge-base-web:test .

# 推送镜像
docker push harbor.dev.meshlake.com:8443/meshlake/knowledge-base-web:test

cd ../deploy

# 部署
kubectl replace --force -f server-test.yaml
kubectl replace --force -f web-test.yaml
