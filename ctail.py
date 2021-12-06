import asyncio
import subprocess
from fastapi import (FastAPI,
    Request,WebSocket, WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedError
import os


app = FastAPI()
origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    command = ["tail", "-f", "nohup.out"]
    try:
        with subprocess.Popen(command,
                              stdout=subprocess.PIPE,
                              bufsize=1,
                              universal_newlines=True) as proc:

            await asyncio.sleep(0.1)
            for line in proc.stdout:
                line = line.rstrip()
                c1 = ws.application_state == WebSocketState.CONNECTED
                c2 = ws.client_state == WebSocketState.CONNECTED
                if not c1 or not c2:
                    proc.terminate()
                    await ws.close()
                    break
                cont = await ws.receive_text()

                if cont == "close":
                    proc.terminate()
                    await ws.close()
                    break

                await ws.send_text(line)

    except ConnectionClosedError:
        await ws.close()
    except WebSocketDisconnect:
        await ws.close()
