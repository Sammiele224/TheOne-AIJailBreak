import asyncio

from engine.evaluators.llm_judge import LLMJudge


def test_level3_judge_parses_json_flag():
    judge = LLMJudge(response={"content": '{"is_jailbroken": true}'})
    result = asyncio.run(judge.evaluate_async())

    assert result["passed"] is True
    assert "jailbroken" in result["reason"].lower()
