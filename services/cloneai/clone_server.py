from __future__ import annotations

import os
from typing import Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from clone_agentAI import AIPersonaAgent, check_ollama_available, create_yamada_taro_persona


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field("default")
    reset: bool = Field(False)
    model_name: Optional[str] = Field(None, description="Override Ollama model (e.g. 'gemma3:1b')")


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model_name: str


app = FastAPI(title="cloneAI local chat server", version="0.1.0")

# Very small in-memory session store for PoC
_sessions: Dict[str, AIPersonaAgent] = {}


def _get_agent(session_id: str, model_name: Optional[str]) -> AIPersonaAgent:
    if session_id in _sessions:
        agent = _sessions[session_id]
        if model_name and getattr(agent.client, "model_name", None) != model_name:
            agent.client.model_name = model_name
        return agent

    persona = create_yamada_taro_persona()

    default_model = os.getenv("CLONEAI_OLLAMA_MODEL", "gemma3:1b")
    chosen_model = model_name or default_model

    # For PoC, automatically fall back to simulation if Ollama isn't reachable.
    simulation_mode = not check_ollama_available()
    agent = AIPersonaAgent(persona, model_name=chosen_model, simulation_mode=simulation_mode)
    _sessions[session_id] = agent
    return agent


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    agent = _get_agent(req.session_id, req.model_name)

    if req.reset:
        agent.reset_conversation()

    reply = agent.process_input(req.message)

    return ChatResponse(
        reply=reply,
        session_id=req.session_id,
        model_name=agent.client.model_name,
    )
