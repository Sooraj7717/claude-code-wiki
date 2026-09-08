# Uplift Orchestrator V6 — Stage 1

This package is the implementation milestone specification for **M1: First Runnable Java/Spring Vertical Slice**.

Pass the contents of `V6-STAGE-1-IMPLEMENTATION-SPEC.md` to Claude Code together with the existing V6 specification package.

## Intended sequence

1. Give Claude Code the V6 specification package.
2. Give Claude Code this Stage 1 specification.
3. Ask Claude Code to implement only M1.
4. Require the M1 Definition of Done to pass before beginning Stage 2.

## Domain constraint

The uplift workflow is specifically for Java/Spring applications.

Do not add TypeScript, Node.js, Python, Go, Rust, or other-language migration rules to the uplift engine.
The frontend may independently use an appropriate web technology; that does not change the uplift domain.
