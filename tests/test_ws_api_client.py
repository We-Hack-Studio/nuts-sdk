import logging

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
    await ws_api_client.sub(topics=["robot#5.log"])
    while True:
        await ws_api_client.robot_ping()
        await ws_api_client.robot_log("Test robot log...", level="INFO")
        await asyncio.sleep(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
