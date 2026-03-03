"""
MindBridge Database Agent — Claude-powered agent core.

This module runs the agentic loop:
1. User sends a natural language request
2. Claude decides which tool(s) to call
3. We execute the tool against PostgreSQL
4. Claude synthesizes the result into a response
5. Loop continues until Claude stops calling tools
"""
import json
import os
from typing import Any

import anthropic
# NOTE: Your project has app/ai/claude_client.py — if it exports an AsyncAnthropic
# client instance, you can import and reuse it here instead of creating a new one.
import asyncpg

from app.ai.database_agent.tool_schemas import TOOL_SCHEMAS
from app.ai.database_agent.tools import check_blocking, query_database, create_view, run_cleanup
from app.ai.database_agent.audit import ensure_audit_table

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
MODEL = "claude-opus-4-5"
MAX_TOKENS = 4096
MAX_ITERATIONS = 10  # Prevent infinite loops

SYSTEM_PROMPT = """You are the MindBridge Database Agent — a specialized AI assistant for 
clinical database operations at a mental health platform.

You have access to 4 tools:
- check_blocking: Monitor PostgreSQL for slow or blocked queries
- query_database: Run safe SELECT queries against patient data  
- create_view: Create reusable clinical query views
- run_cleanup: Safely delete records with audit logging

Guidelines:
- Patient safety first: always confirm before destructive operations
- For run_cleanup, ALWAYS do a dry_run first, then ask for confirmation
- For query_database, always use parameterized queries ($1, $2...) for user values
- When creating views, use descriptive names that reflect the clinical purpose
- Summarize results clearly — clinicians need actionable information, not raw SQL dumps
- If a request seems ambiguous, ask a clarifying question before running queries

You are connected to a PostgreSQL database with 10 test patients in the MindBridge development environment."""


# ─────────────────────────────────────────────
# Tool dispatcher
# ─────────────────────────────────────────────
async def dispatch_tool(
    tool_name: str,
    tool_input: dict[str, Any],
    conn: asyncpg.Connection,
) -> dict[str, Any]:
    """Route tool calls to their implementations."""
    if tool_name == "check_blocking":
        return await check_blocking(conn, **tool_input)

    elif tool_name == "query_database":
        return await query_database(conn, **tool_input)

    elif tool_name == "create_view":
        return await create_view(conn, **tool_input)

    elif tool_name == "run_cleanup":
        return await run_cleanup(conn, **tool_input)

    else:
        return {"error": f"Unknown tool: {tool_name}"}


# ─────────────────────────────────────────────
# Agent loop
# ─────────────────────────────────────────────
async def run_agent(
    user_message: str,
    pool: asyncpg.Pool,
    conversation_history: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Run the MindBridge Database Agent for a single turn.

    Args:
        user_message: Natural language request from the user
        pool: asyncpg connection pool
        conversation_history: Prior messages for multi-turn context

    Returns:
        {
            "response": str,           # Claude's final natural language response
            "tools_called": list,      # Tools that were invoked
            "iterations": int,         # Number of tool-call rounds
            "conversation": list,      # Updated message history
        }
    """
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # Build message history
    messages = list(conversation_history or [])
    messages.append({"role": "user", "content": user_message})

    tools_called = []
    iterations = 0
    final_response = ""

    async with pool.acquire() as conn:
        # Ensure audit table exists
        await ensure_audit_table(conn)

        while iterations < MAX_ITERATIONS:
            iterations += 1

            # Call Claude
            response = await client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )

            # Collect assistant message
            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            # Check stop condition
            if response.stop_reason == "end_turn":
                # Extract final text response
                for block in assistant_content:
                    if hasattr(block, "text"):
                        final_response = block.text
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []

                for block in assistant_content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        # Execute the tool
                        try:
                            result = await dispatch_tool(tool_name, tool_input, conn)
                        except Exception as e:
                            result = {"error": f"Tool execution error: {str(e)}"}

                        tools_called.append({
                            "tool": tool_name,
                            "input": tool_input,
                            "result_preview": str(result)[:200],
                        })

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(result),
                        })

                # Feed results back to Claude
                messages.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                break

    return {
        "response": final_response,
        "tools_called": tools_called,
        "iterations": iterations,
        "conversation": messages,
    }
