# ADR 0005: Defer the Security Data Pipeline to Phase 2

- Status: Accepted
- Date: 2026-07-20

## Context

Ingestion, immutable raw retention, normalization, streaming detection, and alert generation introduce durability, volume, replay, schema, and isolation concerns. Implementing them before the control-plane security foundation would prevent a bounded Phase 1.

## Decision

Phase 1 contains no event ingestion, canonical-event persistence, brokers, object storage, ClickHouse, detection execution, alerts, or incidents. It defines only necessary extension points. Phase 2 will select and benchmark the durable ingestion/outbox or broker design, raw-event retention, canonical schema implementation, search storage, and worker topology through additional ADRs.

## Consequences

Phase 1 makes no event-throughput, durable-before-ack, detection-latency, or SOC-workflow implementation claim. Product pages for deferred resources must not ship as fake or disconnected UI.

