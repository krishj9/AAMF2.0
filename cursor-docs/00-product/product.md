# Product Overview

## Product
Autonomous Portfolio Construction and Rebalancing Platform

## Purpose
A personal-project financial decision-support platform that uses multiple specialist agents to generate explainable, evidence-backed rebalance recommendations and approval artifacts.

## Key architecture decision
- The orchestrator is **LangGraph**, not Bedrock native supervisor mode.
- LangGraph execution runs on **AWS Lambda**.
- Bedrock/AgentCore services remain first-class for model access, guardrails, memory, evals, and observability.
- The frontend is a web application built with **Angular**.

## Target users
- Personal investor
- Solo operator
- Safety reviewer (you)
- Power user
- Project maintainer

## Core outcomes
- Faster rebalance recommendation cycles
- Better traceability and safer decision support
- Strong policy checks and manual control before any execution handoff

## Product boundaries
- The platform produces recommendations and approval-ready artifacts.
- The platform does not autonomously execute trades in production.
- Manual approval is required for progression to any execution pathway.
