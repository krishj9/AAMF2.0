from app.contracts.analysis import AgentStageResult, AgentStatus


def completed_stage(agent_name: str, summary: str) -> AgentStageResult:
    return AgentStageResult(agent_name=agent_name, status=AgentStatus.COMPLETED, summary=summary)


def blocked_stage(agent_name: str, summary: str) -> AgentStageResult:
    return AgentStageResult(agent_name=agent_name, status=AgentStatus.BLOCKED, summary=summary)
