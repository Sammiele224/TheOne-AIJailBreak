from engine.evaluators.tool_verifier import ToolVerifier


def test_tool_verifier_detects_open_vault_call():
    response = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "open_vault"}}
                    ]
                }
            }
        ]
    }

    result = ToolVerifier(response=response).evaluate()

    assert result["passed"] is True
    assert "tool call" in result["reason"].lower()
