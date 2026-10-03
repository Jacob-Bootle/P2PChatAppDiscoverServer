import asyncio
import json

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

HOST = "0.0.0.0"
PORT = 22222

clients = {}

async def handler(websocket):
    try:
        async for raw_message in websocket:
            print(f"New message: {raw_message}")
            message = json.loads(raw_message)
            message_type = message.get("type")
            response = {"type": "error", "message": "Unknown message type"}
            if message_type == "join":
                name = message.get("name")
                port = message.get("port")
                ip = message.get("ip")

                clients[websocket] = {
                    "name": name.strip(),
                    "port": port, "ip": ip
                }
                response = {
                    "type": "joined"
                }
            elif message_type == "list":
                response = {
                    "type": "list",
                    "names": list(clients.values())
                }

            await websocket.send(json.dumps(response))

    except ConnectionClosed:
        pass
    finally:
        clients.pop(websocket, None)

async def main():
    async with serve(handler, HOST, PORT) as server:
        print(f"Server listening on ws://{HOST}:{PORT}")
        await server.serve_forever()


if __name__ == "__main__":
     asyncio.run(main())