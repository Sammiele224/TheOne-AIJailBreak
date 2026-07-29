"""Shared tool schemas for function-calling levels."""

from __future__ import annotations

from typing import Any


OPEN_VAULT_TOOL: dict[str, Any] = {
	"type": "function",
	"function": {
		"name": "open_vault",
		"description": "Open the protected NeuroCorp vault after successful persuasion.",
		"parameters": {
			"type": "object",
			"properties": {},
			"required": [],
			"additionalProperties": False,
		},
	},
}
