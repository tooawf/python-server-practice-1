from __future__ import annotations

import threading
import time

from .model import DataModel
from .rpc import RPCClient, RPCServer


def main() -> None:
    server = RPCServer(DataModel())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.1)
    client = RPCClient()
    now = int(time.time())

    print("create_actor:", client.create_actor(1, now, "192.168.1.10", "Mozilla/5.0"))
    print("create_instruction:", client.create_instruction(1, now, "GET /index", 1, "new"))
    print("create_response:", client.create_response(1, now, "OK", "200", "", 1))
    print("actors:", client.get_all_actors())
    print("instructions:", client.get_all_instructions())
    print("responses:", client.get_all_responses())
    print("recent:", client.select_recent_instructions(now))
    print("update_actor:", client.update_actor(1, now, "10.0.0.1", "Mozilla/5.0 Chrome"))
    print("update_instruction:", client.update_instruction(1, now, "POST /login", 1, "done"))
    print("update_response:", client.update_response(1, now, "Accepted", "201", "", 1))
    print("delete_response:", client.delete_response(1))
    print("delete_instruction:", client.delete_instruction(1))
    print("delete_actor:", client.delete_actor(1))

    try:
        client.delete_actor(999)
    except RuntimeError as exc:
        print("error demonstration:", exc)
    finally:
        server.stop()


if __name__ == "__main__":
    main()
