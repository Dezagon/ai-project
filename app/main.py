from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fastapi_mcp import FastApiMCP

from app.routers import ai, auth

app = FastAPI(title="Trackagon Backend")
# mcp = FastApiMCP(app)

origins = [
    "http://localhost:0000/login",
    "http://localhost:0000/signup",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

# Mount MCP server directly to FastAPI app
# mcp.mount()