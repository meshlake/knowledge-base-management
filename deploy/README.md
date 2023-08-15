# deploy

## 前置知识
1. [如何在本地开发环境使用集群应用服务（例如mysql, postgresql）？](https://meshlake.feishu.cn/wiki/wikcnCkkiubD37UVuFP5xZHIWtc)

## 查看当前集群的命名空间状态
```shell
kubectl get all -n knowledge-base
```

## 部署
```shell
//部署到测试环境
./deploy_test.sh

//查看部署状态
kubectl get all -n knowledge-base
```

## QA
1. 如何配置namespace的secret docker-registry
```shell
kubectl -n knowledge-base create secret docker-registry meshlake-harbor-auth \
    --docker-server=harbor.dev.meshlake.com:8443 \
    --docker-username=robot\$cicd \
    --docker-password=xcYhv0uWaVPSXcJPPEB0KxaZMqgwIVAE \
    --docker-email=devops@meshlake.com
```