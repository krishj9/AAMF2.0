from typing import Protocol


class ModelAdapter(Protocol):
    async def summarize(self, prompt: str, evidence: list[dict[str, str]]) -> str:
        """Generate a user-facing summary from evidence."""


class LocalModelAdapter:
    async def summarize(self, prompt: str, evidence: list[dict[str, str]]) -> str:
        evidence_summary = "; ".join(item.get("summary", "") for item in evidence)
        return f"{prompt}: {evidence_summary}".strip()
