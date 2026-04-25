from app.contracts.analysis import AgentStageResult, AgentStatus


def completed_stage(
    agent_name: str,
    summary: str,
    protocol: str = "LOCAL",
    execution_location: str = "in_process",
) -> AgentStageResult:
    return AgentStageResult(
        agent_name=agent_name,
        status=AgentStatus.COMPLETED,
        summary=summary,
        protocol=protocol,
        execution_location=execution_location,
    )


def blocked_stage(
    agent_name: str,
    summary: str,
    protocol: str = "LOCAL",
    execution_location: str = "in_process",
) -> AgentStageResult:
    return AgentStageResult(
        agent_name=agent_name,
        status=AgentStatus.BLOCKED,
        summary=summary,
        protocol=protocol,
        execution_location=execution_location,
    )
