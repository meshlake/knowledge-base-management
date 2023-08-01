# 开发

## Prerequisites

- [Python](https://www.python.org/) (>=3.10)

## 前置知识

1. [FastAPI文档](https://fastapi.tiangolo.com/zh/)

## 本地开发环境

1. 创建虚拟环境

```shell
python3 -m venv venv
```

2. 激活虚拟环境

```shell
source venv/bin/activate
```

3. 安装依赖

```shell
pip3 install -r requirements.txt
```

4. Start Database

```shell
kubectl port-forward svc/mysql 4306:3306 -n infra
```

5. 运行

```shell
uvicorn app.main:app --reload --port 7001
```

6. 访问

[Swagger UI](http://localhost:7001/docs)

[Open API](http://localhost:7001/redoc)

## 如果更新了依赖记得更新requirements.txt

```shell
pip3 freeze > requirements.txt
```
