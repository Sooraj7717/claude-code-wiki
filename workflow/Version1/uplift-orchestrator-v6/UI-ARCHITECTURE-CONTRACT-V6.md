# UI Architecture Contract — V6

## Principle

The UI is a human control and observability plane over the Orchestrator API. It is not a second workflow engine.

## Primary screens

### Dashboard
- active runs
- progress
- current task/attempt
- human gates
- recent failures
- recent activity

### Run Overview
- run status
- plan version
- progress
- current task/attempt
- gates
- recent events

### Plan
- immutable plan versions
- task DAG
- dependencies
- scopes
- verification requirements
- intentional overlaps

### Tasks
- task status
- dependencies
- attempts
- verification
- recovery history

### Attempt
- baseline
- execution status
- workspace delta
- scope result
- contract result
- deterministic checks
- verifier result
- failure/recovery history

### Diff & Contract
- added/modified/deleted/renamed files
- protected Java API changes
- REST request/response contract changes
- configuration contract changes
- persistence contract changes
- actual diff inspection

### Human Gate
- reason
- evidence
- affected task/attempt
- relevant diff
- allowed decisions
- durable decision history

### Events
- append-only workflow history
- filterable by run/task/attempt/event type

## UI state rules

The UI renders server-authoritative state. Optimistic UI must not imply a state transition before the Orchestrator confirms it.

The UI must clearly distinguish:
- current state
- pending command
- evidence
- agent narrative
- authoritative Orchestrator decision

## Live updates

Prefer SSE for run event/status updates in V6. Reconnect using the last known event sequence where supported. On reconnect, reload authoritative run state and reconcile missed events.

## No direct filesystem access

The browser must never read `.uplift/runs/**`, Git metadata, or the target workspace directly. All data comes through the API.

## No direct Claude access

The browser must never launch Claude Code, call agent prompts, or manage AgentRunner instances.
