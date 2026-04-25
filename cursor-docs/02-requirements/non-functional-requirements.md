# Non-Functional Requirements

## NFR-01 Explainability and traceability
- Recommendation-bearing outputs must include rationale, evidence, provenance, and confidence.
- Hidden reasoning artifacts are never exposed.

## NFR-02 Reliability and graceful degradation
- Categorize failures into retryable, degraded, and blocked outcomes.
- Ensure critical control failures produce blocked state.

## NFR-03 Security and simple role-based access
- Enforce least privilege for request submission, approval, memory correction, and release operations.
- Capture user and service identity for all sensitive actions.

## NFR-04 Observability
- Emit traces and node-level spans across LangGraph execution.
- Correlate metrics/logs with request/session/trace identifiers.

## NFR-05 Performance
- Define max end-to-end response budget for orchestration path.
- Define node-level timeouts and retry budgets.

## NFR-06 Contract stability
- All machine interfaces are schema-versioned.
- Breaking changes require explicit migrations and compatibility strategy.

## NFR-07 Personal safety posture
- Maintain practical auditability and retention controls.
- Support evidence export for safety review and incident debugging.
