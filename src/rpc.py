"""TCP RPC server/client for practical assignment variant 1."""

from __future__ import annotations

import json
import logging
import socket
import struct
import threading
from typing import Any, Callable

from .model import DataModel

PROTOCOL_VERSION = 1
HEADER_FORMAT = ">BBI"  # version, operation, body size; big-endian
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

OPERATIONS = {
    1: "create_actor",
    2: "delete_actor",
    3: "get_all_actors",
    4: "update_actor",
    5: "create_instruction",
    6: "delete_instruction",
    7: "get_all_instructions",
    8: "update_instruction",
    9: "create_response",
    10: "delete_response",
    11: "get_all_responses",
    12: "update_response",
    13: "select_recent_instructions",
}

NAME_TO_OPERATION = {name: code for code, name in OPERATIONS.items()}

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger("rpc")


def _pack_message(operation: int, payload: dict[str, Any]) -> bytes:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return struct.pack(HEADER_FORMAT, PROTOCOL_VERSION, operation, len(body)) + body


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("Connection closed before the complete message was received")
        data.extend(chunk)
    return bytes(data)


def _recv_message(sock: socket.socket) -> tuple[int, dict[str, Any]]:
    header = _recv_exact(sock, HEADER_SIZE)
    version, operation, size = struct.unpack(HEADER_FORMAT, header)
    if version != PROTOCOL_VERSION:
        raise ValueError(f"Unsupported protocol version: {version}")
    if size > 10_000_000:
        raise ValueError("RPC body is too large")
    body = _recv_exact(sock, size)
    return operation, json.loads(body.decode("utf-8"))


class RPCServer:
    def __init__(self, model: DataModel, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.model = model
        self.host = host
        self.port = port
        self._server: socket.socket | None = None
        self._stop = threading.Event()

    def _dispatch(self, operation: int, payload: dict[str, Any]) -> Any:
        name = OPERATIONS.get(operation)
        if name is None:
            raise ValueError(f"Unknown operation: {operation}")
        function: Callable[..., Any] = getattr(self.model, name)
        return function(**payload)

    def _handle_client(self, conn: socket.socket) -> None:
        with conn:
            try:
                operation, payload = _recv_message(conn)
                LOGGER.info("RPC request: operation=%s payload=%s", operation, payload)
                result = self._dispatch(operation, payload)
                response = {"ok": True, "result": result}
            except Exception as exc:  # RPC must return errors instead of crashing the server.
                response = {"ok": False, "error": type(exc).__name__, "message": str(exc)}
            conn.sendall(_pack_message(operation if "operation" in locals() else 0, response))

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            self._server = server
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen()
            server.settimeout(0.5)
            LOGGER.info("RPC server listening on %s:%s", self.host, self.port)
            while not self._stop.is_set():
                try:
                    conn, _ = server.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()

    def stop(self) -> None:
        self._stop.set()
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass


class RPCClient:
    """Client method names intentionally match DataModel method names."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000, timeout: float = 3.0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def call(self, method: str, **payload: Any) -> Any:
        operation = NAME_TO_OPERATION[method]
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            sock.sendall(_pack_message(operation, payload))
            response_operation, response = _recv_message(sock)
        if response_operation != operation:
            raise ValueError("RPC response operation does not match request")
        if not response.get("ok"):
            raise RuntimeError(f"{response['error']}: {response['message']}")
        return response["result"]

    def create_actor(self, key: int, created: int, ip: str, user_agent: str) -> Any:
        return self.call("create_actor", key=key, created=created, ip=ip, user_agent=user_agent)

    def delete_actor(self, key: int) -> Any:
        return self.call("delete_actor", key=key)

    def get_all_actors(self) -> Any:
        return self.call("get_all_actors")

    def update_actor(self, key: int, created: int, ip: str, user_agent: str) -> Any:
        return self.call("update_actor", key=key, created=created, ip=ip, user_agent=user_agent)

    def create_instruction(self, key: int, created: int, content: str, actor: int, status: str) -> Any:
        return self.call("create_instruction", key=key, created=created, content=content, actor=actor, status=status)

    def delete_instruction(self, key: int) -> Any:
        return self.call("delete_instruction", key=key)

    def get_all_instructions(self) -> Any:
        return self.call("get_all_instructions")

    def update_instruction(self, key: int, created: int, content: str, actor: int, status: str) -> Any:
        return self.call("update_instruction", key=key, created=created, content=content, actor=actor, status=status)

    def create_response(self, key: int, created: int, output: str, status: str, failure: str, instruction: int) -> Any:
        return self.call("create_response", key=key, created=created, output=output, status=status, failure=failure, instruction=instruction)

    def delete_response(self, key: int) -> Any:
        return self.call("delete_response", key=key)

    def get_all_responses(self) -> Any:
        return self.call("get_all_responses")

    def update_response(self, key: int, created: int, output: str, status: str, failure: str, instruction: int) -> Any:
        return self.call("update_response", key=key, created=created, output=output, status=status, failure=failure, instruction=instruction)

    def select_recent_instructions(self, now: int | None = None) -> Any:
        payload = {} if now is None else {"now": now}
        return self.call("select_recent_instructions", **payload)
