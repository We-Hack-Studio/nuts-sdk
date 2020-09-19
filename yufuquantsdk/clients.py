import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Set

import httpx
import websockets
from websockets import exceptions

logger = logging.getLogger("yufuquantsdk")


class WebsocketAPIClient:
    def __init__(self, uri: str, ws: websockets.WebSocketClientProtocol = None) -> None:
        self._uri: str = uri
        self._ws: websockets.WebSocketClientProtocol = ws
        self._authed: bool = False
        self._auth_token = ""
        self._sub_topics: Set[str] = set()
        self._inputs: asyncio.Queue[str] = asyncio.Queue()
        self._outputs: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        self._run_task: asyncio.Task[Any] = asyncio.get_event_loop().create_task(
            self._run()
        )

    async def auth(self, auth_token: str):
        message = {
            "cmd": "auth",
            "token": auth_token,
        }
        await self._deliver(json.dumps(message))
        self._authed = True
        self._auth_token = auth_token

    async def sub(self, topics: Iterable[str]):
        # Remove duplicated topics
        if not isinstance(topics, set):
            topics = set(topics)

        message = {
            "cmd": "sub",
            "topics": list(topics),  # Object of type set is not JSON serializable
        }
        await self._deliver(json.dumps(message))
        self._sub_topics = topics

    async def unsub(self, topics: Iterable[str]):
        # Remove duplicated topics
        if not isinstance(topics, set):
            topics = set(topics)

        message = {
            "cmd": "unsub",
            "topics": list(topics),
        }
        await self._deliver(json.dumps(message))
        self._sub_topics = self._sub_topics - topics

    async def robot_ping(self):
        data = {"timestamp": datetime.now().timestamp()}
        message = {"category": "robotPing", "data": data}
        await self._broadcast(message)

    async def robot_log(self, text: str, level: str = "info"):
        data = {
            "text": text,
            "level": level,
            "timestamp": int(datetime.now().timestamp()) * 1000,
        }
        message = {"category": "robotLog", "data": data}
        await self._broadcast(message)

    async def _connect(self, **kwargs):
        # disable ping
        kwargs["ping_interval"] = None
        try:
            self._ws = await websockets.connect(self._uri, **kwargs)
        except Exception as exc:
            logger.exception("Failed to connect to %s: %s.", self._uri, exc)
            raise
        logger.info("Connected to %s.", self._uri)

    async def _reconnect(self):
        await self._connect()

        if self._authed:
            await self.auth(self._auth_token)

        if len(self._sub_topics) > 0:
            await self.sub(self._sub_topics)

        logger.info("Reconnected to %s.", self._uri)

    async def _deliver(self, s: str):
        await self._inputs.put(s)

    async def _send(self, s: str):
        assert self._ws is not None, "No connection!"
        try:
            await self._ws.send(s)
            logger.debug(">>> %s", s)
        except websockets.ConnectionClosed as exc:
            logger.exception(exc)
            await self._reconnect()

    async def _broadcast(self, message: Dict):
        data = {"cmd": "broadcast", "message": message}
        await self._deliver(json.dumps(data))

    # todo: handle stop signal
    async def _run(self):
        await self._connect()
        try:
            while True:
                incoming: asyncio.Task[Any] = asyncio.create_task(self._ws.recv())
                outgoing: asyncio.Task[Any] = asyncio.create_task(self._inputs.get())

                done: Set[asyncio.Future[Any]]
                pending: Set[asyncio.Future[Any]]
                done, pending = await asyncio.wait(
                    [incoming, outgoing], return_when=asyncio.FIRST_COMPLETED
                )

                # Cancel pending tasks to avoid leaking them.
                if incoming in pending:
                    incoming.cancel()
                if outgoing in pending:
                    outgoing.cancel()

                if incoming in done:
                    try:
                        message = incoming.result()
                        logger.debug("<<< %s", message)
                    except websockets.ConnectionClosed:
                        break
                    else:
                        try:
                            self._outputs.put_nowait(message)
                        except asyncio.QueueFull:
                            logger.warning("The outputs queue is full.")

                if outgoing in done:
                    message = outgoing.result()
                    await self._send(message)
        finally:
            await self.close()

    async def close(self):
        await self._ws.close()
        close_status = exceptions.format_close(
            self._ws.close_code, self._ws.close_reason
        )
        logger.info(f"Connection closed: {close_status}.")


ROBOT_REQ_PATH = "/robots/{robot_id}/"
ROBOT_CONFIG_REQ_PATH = "/robots/{robot_id}/config/"
ROBOT_PING_REQ_PATH = "/robots/{robot_id}/ping/"
ROBOT_ASSET_RECORD_REQ_PATH = "/robots/{robot_id}/assetRecord/"


class RESTAPIClient:
    def __init__(self, base_url: str, auth_token: str):
        self._base_url: str = base_url.rstrip("/")
        self._auth_token: str = auth_token

    async def get_robot_config(self, robot_id: int):
        req_path = ROBOT_CONFIG_REQ_PATH.format(robot_id=robot_id)
        return await self._request("GET", req_path)

    async def patch_robot_asset_record(self, robot_id: int, data: Dict[str, Any]):
        req_path = ROBOT_ASSET_RECORD_REQ_PATH.format(robot_id=robot_id)
        d = {"data": {"type": "robots", "id": robot_id, "attributes": data}}
        return await self._request("PATCH", req_path, data=d)

    async def post_robot_ping(self, robot_id: int):
        req_path = ROBOT_PING_REQ_PATH.format(robot_id=robot_id)
        return await self._request("POST", req_path)

    async def _request(
        self,
        method: str,
        req_path: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict] = None,
        auth: bool = True,
    ):
        req_headers = {"Content-Type": "application/vnd.api+json"}
        if auth:
            req_headers["Authorization"] = f"Token {self._auth_token}"
        if headers is not None:
            req_headers.update(headers)

        url = self._base_url + req_path
        async with httpx.AsyncClient() as client:
            logger.debug(
                "%s %s, Request<headers=%s params=%s data=%s>",
                method,
                url,
                req_headers,
                params,
                data,
            )
            res = await client.request(
                method,
                url,
                headers=req_headers,
                params=params,
                json=data,
                timeout=5,
            )
            http_text = res.text
            logger.debug(
                "%s %s, Response<status_code=%s headers=%s http_text=%s>",
                method,
                url,
                res.status_code,
                req_headers,
                http_text,
            )
        res.raise_for_status()
        if res.status_code == "204":
            return None
        return res.json()
