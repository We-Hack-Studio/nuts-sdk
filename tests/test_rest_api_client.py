import logging
from pprint import pprint

from yufuquantsdk.clients import RESTAPIClient

# Enable log for debug
logger = logging.getLogger("yufuquantsdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

base_url = "http://127.0.0.1:8000/api/v1"
api_key = "DBLx26F6.aHUGVqxfqSSh10NkIW9rvMdsJbMM5Xd4"
robot_id = 8


async def main():
    http_client = RESTAPIClient(
        base_url="http://127.0.0.1:8000/api/v1",
        api_key=api_key,
    )

    result = await http_client.get_robot(robot_id)
    pprint(result)

    result = await http_client.ping_robot(robot_id)
    pprint(result)

    result = await http_client.update_robot_asset_record(
        robot_id=robot_id, data={"total_balance": 10000}
    )
    pprint(result)

    result = await http_client.update_robot_strategy_store(
        robot_id=robot_id,
        data={
            "parametersExt": [
                {
                    "code": "maxPosQty",
                    "name": "最大持仓数量",
                    "type": "float",
                    "value": 100,
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
        },
    )
    pprint(result)

    result = await http_client.update_robot_order_store(
        robot_id=robot_id,
        data=[
            {
                "id": "1234567",
                "qty": 1,
                "side": -1,
                "price": 355,
                "type": "limit",
            }
        ],
    )
    pprint(result)

    result = await http_client.update_robot_position_store(
        robot_id=robot_id,
        data=[
            {
                "qty": 1,
                "side": -1,
                "liqPrice": 100,
                "avgPrice": 355,
                "unrealizedPnl": 0.1,
            }
        ],
    )
    pprint(result)

    result = await http_client.get_robot_credential_key(robot_id)
    pprint(result)

    result = await http_client.get_robot_strategy_parameters(robot_id)
    pprint(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
