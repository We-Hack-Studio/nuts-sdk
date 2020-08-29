# yufuquant SDK

yufuquant SDK 封装了用于和 yufuquant 后端进行交互的常用方法。

yufuquant SDK 目前只支持 Python，由于大多数 API 都是基于 asyncio 的异步 API，因此要求 Python 的最低版本为 Python 3.7，推荐使用 Python 3.8。

## 安装

```bash
$ pip install yufuquantsdk
```

## REST API 客户端

REST API 客户端用于和 yufuquant 后端的 RESTful API 进行交互。

```python
from yufuquantsdk.clients import RESTAPIClient

base_url="https://yufuquant.cc/api/v1" # 系统后端接口地址
auth_token="xxxxx" # 认证令牌
robot_id = 1 # 机器人 id
rest_api_client = RESTAPIClient(base_url=base_url, auth_token=auth_token)

# 获取机器人配置
await rest_api_client.get_robot_config(robot_id)

# 更新机器人的资产信息
data = {
  "total_balance": 5.8
}
await rest_api_client.patch_robot_asset_record(robot_id, data)

# 发送 ping
await rest_api_client.post_robot_ping(robot_id)
```

以下是一个完整的示例：

```python
import logging
from pprint import pprint
from yufuquantsdk.clients import RESTAPIClient


# 开启日志
logger = logging.getLogger("yufuquantsdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

async def main():
    http_client = RESTAPIClient(
        base_url="https://yufuquant.cc/api/v1",
        auth_token="8g2e470579ba14ea69000859eba6c421b69ff95d",
    )
    
    result = await http_client.get_robot_config(robot_id=1)
    pprint(result)
    
    result = await http_client.post_robot_ping(robot_id=1)
    pprint(result)
    
    result = await http_client.patch_robot_asset_record(
      robot_id=1, data={"total_balance": 10000}
    )
    pprint(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Websocket API 客户端

Websocket API 客户端用于和 yufuquant 后端的 Websocket API 进行交互。

```python
from yufuquantsdk.clients import WebsocketAPIClient

uri="wss://yufuquant.cc/ws/v1/streams/" # 系统后端接口地址
auth_token="xxxxx" # 认证令牌
topics = ["robot#1.ping", "robot#1.log"] # 订阅的话题
ws_api_client = WebsocketAPIClient(uri=uri)

# 认证
await ws_api_client.auth(auth_token)

# 订阅话题
await ws_api_client.sub(topics)

# 取消话题订阅
await ws_api_client.unsub(topics)

# 发送机器人 ping
await ws_api_client.robot_ping()

# 发送机器人日志
await ws_api_client.robot_log()
```

以下是一个完整的示例：

```python
import logging
from yufuquantsdk.clients import WebsocketAPIClient

# 开启日志
logger = logging.getLogger("yufuquantsdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

async def main():
    ws_api_client = WebsocketAPIClient(uri="wss://yufuquant.cc/ws/v1/streams/")
    
    await ws_api_client.auth("8d2e470575ba04ea69000859eba6c421a69ff95c")
    await ws_api_client.sub(topics=["robot#1.log"])
    while True:
        await ws_api_client.robot_ping()
        await ws_api_client.robot_log("Test robot log...", level="INFO")
        await asyncio.sleep(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

