import pytest
from unittest.mock import AsyncMock, patch


def test_ai_chat_auth_required(client):
    """
    Ensure the chat endpoint requires authorization.
    """
    response = client.post(
        "/api/v1/ai/chat",
        json={"message": "Hello", "conversation_id": "test_conv"}
    )
    assert response.status_code == 401


@patch("backend.ai.agent.LLMService.generate_response", new_callable=AsyncMock)
def test_ai_chat_agent_flow_with_tool_calling(mock_generate_response, client):
    """
    Test the complete agent orchestration loop, including tool execution and history updates.
    """
    # 1. Register and login user
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "student@example.com", "password": "password123", "name": "Active Student"}
    )
    assert signup_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "student@example.com", "password": "password123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mock the LLM service responses:
    # First turn: requests tool execution 'current_user_info'
    # Second turn: returns final text answer
    mock_generate_response.side_effect = [
        (None, [{"id": "call_info_1", "name": "current_user_info", "arguments": {}}]),
        ("Welcome! You are logged in as Active Student (student@example.com).", [])
    ]

    # 2. Call the AI Chat endpoint
    response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Who am I?",
            "conversation_id": "session_123"
        },
        headers=headers
    )

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    
    assert data["response"] == "Welcome! You are logged in as Active Student (student@example.com)."
    assert len(data["actions"]) == 1
    assert data["actions"][0]["tool"] == "current_user_info"
    assert data["actions"][0]["output"]["name"] == "Active Student"
    assert data["actions"][0]["output"]["email"] == "student@example.com"
    assert "sources" in data


@patch("backend.ai.agent.LLMService.generate_response", new_callable=AsyncMock)
def test_ai_chat_agent_flow_syllabus_and_plan_generation(mock_generate_response, client):
    """
    Test agent flow creating a syllabus, study plan, and verifying tool state side-effects.
    """
    # 1. Register and login user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "student@example.com", "password": "password123", "name": "Active Student"}
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "student@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest a syllabus manually to have database records
    raw_syllabus = "Unit 1: Python basics\n- Variables"
    syllabus_resp = client.post(
        "/api/v1/syllabi/",
        json={"raw_text": raw_syllabus},
        headers=headers
    )
    syllabus_id = syllabus_resp.json()["id"]

    # Mock the LLM service responses:
    # First turn: LLM wants to generate a plan for syllabus_id = 1
    # Second turn: LLM explains the generated plan details
    mock_generate_response.side_effect = [
        (
            None, 
            [{
                "id": "call_plan_1",
                "name": "generate_plan",
                "arguments": {
                    "syllabus_id": syllabus_id,
                    "start_date": "2026-07-20",
                    "end_date": "2026-07-22"
                }
            }]
        ),
        ("I have generated a new 3-day study plan starting tomorrow.", [])
    ]

    response = client.post(
        "/api/v1/ai/chat",
        json={
            "message": "Create a study plan for my latest syllabus from tomorrow for 3 days.",
            "conversation_id": "session_456"
        },
        headers=headers
    )

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert "study plan starting tomorrow" in data["response"]
    assert len(data["actions"]) == 1
    assert data["actions"][0]["tool"] == "generate_plan"
    assert data["actions"][0]["output"]["status"] == "active"
    assert len(data["actions"][0]["output"]["schedule"]) == 3
    assert f"Syllabus #{syllabus_id}" in data["sources"]
