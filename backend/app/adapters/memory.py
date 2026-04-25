from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryItem:
    memory_id: str
    category: str
    summary: str
    confidence: float


class LocalMemoryAdapter:
    async def retrieve(self, client_id: str) -> list[MemoryItem]:
        return [
            MemoryItem(
                memory_id=f"mem_{client_id}_preference",
                category="derived_preference",
                summary="Synthetic default preference: keep recommendations advisory-only.",
                confidence=0.8,
            )
        ]
