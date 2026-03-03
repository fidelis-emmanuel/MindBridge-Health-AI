"""
FastAPI router for the MindBridge Database Agent.
Mounts at /agent in the main FastAPI app.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import asyncpg

from app.ai.database_agent import run_agent

router = APIRouter(prefix="/agent", tags=["Database Agent"])


# ─────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────
class AgentRequest(BaseModel):
    message: str
    conversation_history: list[dict] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Show me all patients admitted in the last 30 days",
                "conversation_history": None,
            }
        }


class ToolCall(BaseModel):
    tool: str
    input: dict
    result_preview: str


class AgentResponse(BaseModel):
    response: str
    tools_called: list[ToolCall]
    iterations: int
    conversation: list[dict]


# ─────────────────────────────────────────────
# Dependency: get DB pool
# ─────────────────────────────────────────────
async def get_pool(request: Request) -> asyncpg.Pool:
    """Retrieve the asyncpg pool stored on app state."""
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(status_code=503, detail="Database pool not initialized")
    return pool


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────
@router.post("/query", response_model=AgentResponse)
async def agent_query(body: AgentRequest, request: Request, pool: asyncpg.Pool = Depends(get_pool)):
    """
    Send a natural language request to the MindBridge Database Agent.
    The agent will use its 4 tools (check_blocking, query_database,
    create_view, run_cleanup) as needed to fulfill the request.
    """
    result = await run_agent(
        user_message=body.message,
        pool=pool,
        conversation_history=body.conversation_history,
    )
    return AgentResponse(**result)


@router.get("/tools", summary="List available agent tools")
async def list_tools():
    """Return the schema of all tools available to the Database Agent."""
    from app.ai.database_agent.tool_schemas import TOOL_SCHEMAS
    return {
        "tools": [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": list(t["input_schema"]["properties"].keys()),
                "required": t["input_schema"].get("required", []),
            }
            for t in TOOL_SCHEMAS
        ]
    }


@router.get("/health")
async def agent_health(request: Request, pool: asyncpg.Pool = Depends(get_pool)):
    """Quick check that agent can reach the database."""
    try:
        async with pool.acquire() as conn:
            result = await conn.fetchval("SELECT COUNT(*) FROM patients")
        return {
            "status": "healthy",
            "patient_count": result,
            "tools_available": 4,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {e}")

