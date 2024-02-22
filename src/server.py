import asyncio
from typing import Optional
import websockets


class WebSocketServer:
    def __init__(self):
        self.server: Optional[websockets.WebSocketServer] = None

    async def send_transcription(self, websocket: websockets.WebSocketServerProtocol, path: str,
                                 transcription: list) -> None:
        """
        Sends the transcription to the connected WebSocket client.

        Args:
            websocket: The WebSocket server protocol.
            path: The requested path.
            transcription: The list of transcriptions.
        """
        while True:
            try:
                try:
                    await websocket.send(transcription[-1])
                except:
                    pass
                await asyncio.sleep(0.0002)
            except websockets.exceptions.ConnectionClosed:  # type: ignore
                break

    async def websocket_handler(self, websocket: websockets.WebSocketServerProtocol, path: str,
                                transcription: list) -> None:
        """
        Handles incoming WebSocket connections and sends the transcription to the clients.

        Args:
            websocket: The WebSocket server protocol.
            path: The requested path.
            transcription: The list of transcriptions.
        """
        while True:
            try:
                await self.send_transcription(websocket, path, transcription)
            except websockets.exceptions.ConnectionClosed:  # type: ignore
                break

    async def start_websocket_server(self, transcription: list) -> None:
        """
        Starts the WebSocket server and waits for incoming connections.

        Args:
            transcription: The list of transcriptions.
        """
        self.server = await websockets.serve(
            lambda ws, path: self.websocket_handler(ws, path, transcription),
            'localhost',
            8765
        )

    async def run_server(self, transcription: list) -> None:
        """
        Runs the WebSocket server.

        Args:
            transcription: The list of transcriptions.
        """
        await self.start_websocket_server(transcription)
        await asyncio.Future()

    def start(self, transcription: list) -> None:
        """
        Starts the WebSocket server in a separate thread.

        Args:
            transcription: The list of transcriptions.
        """
        asyncio.run(self.run_server(transcription))
