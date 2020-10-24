import logging
from pprint import pprint

from yufuquantsdk.clients import RESTAPIClient

# Enable log for debug
logger = logging.getLogger("yufuquantsdk")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

base_url = "http://127.0.0.1:8000/api/v1"
api_key = "DBLx26F6.aHUGVqxfqSSh10NkIW9rvMdsJbMM5Xd4"


async def main():
    http_client = RESTAPIClient(
        base_url="http://127.0.0.1:8000/api/v1",
        api_key=api_key,
    )

    result = await http_client.get_robot(robot_id=1)
    pprint(result)

    result = await http_client.ping_robot(robot_id=1)
    pprint(result)

    result = await http_client.update_robot_asset_record(
        robot_id=1, data={"total_balance": 10000}
    )
    pprint(result)

    result = await http_client.get_robot_credential_key(robot_id=1)
    pprint(result)

    result = await http_client.get_robot_strategy_parameters(robot_id=1)
    pprint(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
