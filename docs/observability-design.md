# Observability Design

## Objectives and signals

Observability must answer whether data is accepted and processed, detection is timely and correct, tenants are isolated and within quota, dependencies are healthy, and incidents can be reconstructed without exposing customer payloads.

- **Metrics:** requests, errors, latency, bytes/events accepted or rejected, queue lag/age, normalization outcomes, detection latency/matches/timeouts, delivery outcomes, query cost, job duration, quota use, storage saturation.
- **Logs:** structured timestamp, service, environment, severity, request/trace ID, operation, outcome/error code, and bounded tenant surrogate. Exclude payloads, tokens, secrets, and raw queries.
- **Traces:** linked edge-to-queue and consumer spans; sampling retains errors/high latency while limiting data leakage.
- **Audit:** separate append-only security records; operational logs are not an audit substitute.

## SLOs and alerts

SLIs measure customer-observable boundaries. Multi-window error-budget burn alerts cover availability and detection latency. Immediate paging covers acknowledged-data-loss risk, successful cross-tenant canaries, audit-pipeline failure, key/credential compromise signals, and unrecoverable queue/storage failure. Capacity/cost anomalies create tickets before saturation.

## Correlation, access, and retention

Correlate request, trace, ingestion receipt, event, rule version, alert, job, and delivery IDs. Tenant context is available to authorized investigation but omitted from uncontrolled metric labels. Error codes are stable.

Telemetry access is least privilege and environment-separated. Debug elevation is time-bound and audited. Central redaction occurs before export; tests inject canary secrets/PII and prove they never reach telemetry. Operational retention is documented and normally shorter than audit retention.

## Dashboards and runbooks

Initial dashboards cover ingest, processing lag, detection, API/query health, notifications, storage/capacity, quota pressure, and security/audit health. Every page links to an owned runbook with diagnosis, safe mitigation, escalation, and verification.
