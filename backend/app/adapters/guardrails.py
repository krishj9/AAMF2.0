from dataclasses import dataclass, field


@dataclass(frozen=True)
class GuardrailCheckResult:
    status: str
    blocked: bool = False
    violations: list[str] = field(default_factory=list)


class LocalGuardrailAdapter:
    async def check_output(self, text: str) -> GuardrailCheckResult:
        denied_phrases = ["guaranteed return", "risk-free profit"]
        violations = [phrase for phrase in denied_phrases if phrase in text.lower()]
        return GuardrailCheckResult(
            status="BLOCKED" if violations else "PASSED",
            blocked=bool(violations),
            violations=violations,
        )
