# Cursor Steering Guide (New Baseline)

## Architecture steering
- Use LangGraph as the only orchestration framework.
- Run orchestration in AWS Lambda.
- Do not implement Bedrock native supervisor/collaborator orchestration for personal paths.

## AWS AI platform steering
- Use Bedrock for model inference and guardrails.
- Use AgentCore memory capabilities for long-term personalization.
- Implement tracing through a provider abstraction that supports both AgentCore and LangSmith.
- Keep CloudWatch as the common metrics/logging plane regardless of tracing backend.
- Keep interfaces portable and schema-first.

## Engineering steering
- Keep deterministic policy logic separate from LLM summarization.
- Treat approval as a hard control boundary.
- Require structured errors for machine-consumable failures.
- Preserve correlation metadata across every component boundary.
- Build and maintain the frontend using Angular conventions and tooling.

## Safety and safety and controls steering
- Never expose raw chain-of-thought.
- Apply policy checks before any recommendation is returned.
- Log all approval, override, memory correction, and policy events.

## Development workflow steering
- Build in this order: contracts -> orchestration -> nodes -> persistence -> evals -> deployment.
- For any change to prompts, policies, schemas, or orchestrator flow, run impacted eval suites before merge.
