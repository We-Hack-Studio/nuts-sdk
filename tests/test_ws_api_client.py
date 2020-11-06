import logging
import random

from yufuquantsdk.clients import WebsocketAPIClient

# Enable log for debug
logger = logging.getLogger("yufuquantsdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

uri = "ws://127.0.0.1:8000/ws/v1/streams/"
api_key = "DBLx26F6.aHUGVqxfqSSh10NkIW9rvMdsJbMM5Xd4"


async def main():
    ws_api_client = WebsocketAPIClient(uri=uri)

    await ws_api_client.auth(api_key)
    await ws_api_client.sub(topics=["robot#9.log", "robot#9.store"])
    while True:
        await ws_api_client.robot_ping()
        await ws_api_client.robot_log("Test robot log...", level="INFO")
        await ws_api_client.robot_position_store(
            positions=[
                {
                    "qty": random.randint(1, 3),
                    "side": -1,
                    "liqPrice": 100,
                    "avgPrice": 355,
                    "unrealizedPnl": 0.1,
                }
            ]
        )
        await ws_api_client.robot_order_store(
            orders=[
                {
                    "qty": random.randint(1, 3),
                    "side": -1,
                    "price": 355,
                    "type": "limit",
                    "id": "123456",
                }
            ]
        )
        await ws_api_client.robot_strategy_store(
            data={
                "parametersExt": [
                    {
                        "code": "maxPosQty",
                        "name": "最大持仓数量",
                        "type": "float",
                        "value": random.randint(100, 150),
                        "description": "",
                        "editable": False,
                        "group": "头寸管理",
                    },
                    {
                        "code": "openPosQty",
                        "name": "单次开仓数量",
                        "type": "float",
                        "value": 100,
                        "description": "单次开仓（即单笔挂单）数量。",
                        "editable": False,
                        "group": "头寸管理",
                    },
                ]
            }
        )
        await asyncio.sleep(5)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
