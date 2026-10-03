# P2P Chat App Discovery Server

A lightweight WebSocket server that helps P2P chat clients find one another. Clients register their name, IP address, and chat port, then request a list of registered peers.

This server handles discovery only. Peer-to-peer connections and chat messages are handled by the chat clients.

## Requirements

- Python 3.11 or newer
- Dependencies listed in `requirements.txt` (`websockets==17.1`)

## Setup

Run these commands from the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

## Run the server

```bash
python main.py
```

By default, the server listens on all IPv4 interfaces at port `22222`:

```text
Server listening on ws://0.0.0.0:22222
```

Connect to `ws://localhost:22222` from the same machine, or `ws://<server-ip>:22222` from another machine. Remote clients need network access to the server's TCP port `22222`.

To change the listening address or port, edit `HOST` and `PORT` in `main.py`.

## Discovery protocol

Send each request as a JSON object in a WebSocket message. Responses are JSON objects too.

### Register a client

Send:

```json
{
  "type": "join",
  "name": "Alice",
  "ip": "192.168.1.10",
  "port": 5000
}
```

The `ip` and `port` identify the client's peer-to-peer chat endpoint, which must be reachable by other peers. The server stores the supplied address; it does not infer it from the WebSocket connection.

Response:

```json
{"type": "joined"}
```

Keep this WebSocket connection open while the client should remain discoverable. Sending another `join` on the same connection replaces its registration. Leading and trailing whitespace is removed from the name.

### List registered clients

Send:

```json
{"type": "list"}
```

Example response:

```json
{
  "type": "list",
  "names": [
    {"name": "Alice", "port": 5000, "ip": "192.168.1.10"},
    {"name": "Bob", "port": 5001, "ip": "192.168.1.11"}
  ]
}
```

Despite the field name `names`, each entry contains the client's name, port, and IP address. The list includes the requesting client if it has registered. An empty registry returns `{"type": "list", "names": []}`. A connection can request the list without registering first.

### Unknown request type

A request with an unknown or missing `type` receives:

```json
{"type": "error", "message": "Unknown message type"}
```

### Disconnect

Close the WebSocket connection to leave. The server removes that connection's registration when its handler exits. There is no separate `leave` request.

## Current behavior and limitations

- Registrations are stored in memory and are cleared when the server restarts.
- Registrations belong to connections; names do not have to be unique.
- Client addresses are accepted as supplied. The server does not verify reachability, provide NAT traversal, or relay chat traffic.
- Requests are expected to be valid JSON objects, and `join` expects a string `name`. Malformed requests can terminate the connection rather than receive a structured error response.
- The server has no authentication and uses unencrypted `ws://` connections by default.
- Incoming messages are printed to the server console.
