# Orchestrator API Contract — V6

## Purpose

Expose the Orchestrator as a stable control-plane API for the UI and future clients. API handlers delegate to the workflow engine; they do not contain workflow policy.

Base path: `/api/v1`

## Resources

- Run
- Plan
- Task
- Attempt
- Human Gate
- Artifact
- Verification
- Event
- Workspace Diff

## Core endpoints

```text
GET    /runs
POST   /runs
GET    /runs/{runId}
POST   /runs/{runId}/start
POST   /runs/{runId}/pause
POST   /runs/{runId}/resume

GET    /runs/{runId}/plan
GET    /runs/{runId}/tasks
GET    /runs/{runId}/attempts
GET    /runs/{runId}/gates
GET    /runs/{runId}/artifacts
GET    /runs/{runId}/verification
GET    /runs/{runId}/diff
GET    /runs/{runId}/events
GET    /runs/{runId}/events/stream

GET    /runs/{runId}/gates/{gateId}
POST   /runs/{runId}/gates/{gateId}/decision

POST   /runs/{runId}/replan
POST   /runs/{runId}/verify
```

Exact request/response schemas are to be implemented as Java DTOs and documented with OpenAPI. Do not expose internal persistence classes directly.

## Command semantics

Commands are idempotency-aware and must include or derive a command/invocation identity where repeated delivery could otherwise duplicate work.

A successful HTTP response means the command was accepted by the Orchestrator, not that an agent has completed the requested work unless the command is explicitly synchronous and documented as such.

Recommended statuses:
- `200` successful read/command completion
- `201` resource created
- `202` asynchronous command accepted
- `400` invalid request
- `404` unknown resource
- `409` invalid state transition/conflict
- `422` policy/validation failure
- `423` human-gated/locked operation where applicable
- `500` unexpected server error

## Error model

Errors should include a stable machine-readable code, message, resource identifiers, and current state when useful.

Example codes:
- `INVALID_STATE_TRANSITION`
- `HUMAN_GATE_REQUIRED`
- `PLAN_NOT_ACCEPTED`
- `SCOPE_VIOLATION`
- `CONTRACT_VIOLATION`
- `WORKSPACE_DIRTY`
- `CONFLICT`
- `POLICY_DENIED`

## Event stream

SSE events should carry event type, run ID, sequence/order information, timestamp, and a compact payload. The append-only event log remains authoritative; SSE is a delivery mechanism.
