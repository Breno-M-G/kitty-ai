"""FastAPI application with WebSocket support."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from mybot.core.context import SharedContext


def create_app(context: SharedContext) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="MyBot WebSocket Server",
        description="WebSocket server for real-time agent communication",
        version="0.1.0",
    )
    app.state.context = context

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time event streaming and chat."""
        await websocket.accept()

        if context.websocket_worker is None:
            await websocket.close(code=1013, reason="WebSocket not available")
            return

        await context.websocket_worker.handle_connection(websocket)

    return app
