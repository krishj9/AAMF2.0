from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class TraceSpan:
    trace_id: str
    node_name: str
    status: str
    started_at: datetime
    ended_at: datetime


class LocalTraceAdapter:
    def span(self, trace_id: str, node_name: str, status: str = "OK") -> TraceSpan:
        now = datetime.now(UTC)
        return TraceSpan(
            trace_id=trace_id,
            node_name=node_name,
            status=status,
            started_at=now,
            ended_at=now,
        )
