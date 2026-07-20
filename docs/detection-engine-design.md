# Detection Engine Design

## Goals and limits

The engine evaluates safe, declarative, versioned detections over canonical events with deterministic evidence. It does not execute arbitrary tenant code. Streaming rules are the MVP; scheduled retrospective queries and richer correlation follow after correctness and isolation are proven.

## Rule model

A version contains identity, tenant/managed ownership, schema compatibility, expression AST, event selectors, grouping keys, event-time window, allowed lateness, severity, alert fingerprint, suppression policy, fixtures, cost estimate, and author/approval metadata.

## Evaluation

1. Compile a validated rule into a bounded plan.
2. Distribute a signed immutable ruleset scoped to tenant and schema version.
3. Route events by tenant and grouping key.
4. Evaluate predicates and bounded event-time window state.
5. Emit a finding with rule version, evidence IDs, interval, and stable fingerprint.
6. Deduplicate/correlate findings into alerts and apply explicit suppression.

## Safety and correctness

- No dynamic network, filesystem, reflection, or user-code access.
- Validate field allowlists, types, regex complexity, joins, cardinality, and windows.
- Enforce per-tenant CPU, memory, state, rule-count, and output quotas.
- Kill/quarantine pathological plans without affecting other tenants.
- Include tenant ID in snapshots and state keys; reject mixed-tenant state.
- Use event time and declared allowed lateness; mark late findings.
- Replay uses a replay ID and isolated result namespace; it never notifies production by default.
- Results are deterministic for the same events, rule, enrichment snapshot, and engine version.

## Lifecycle and measurement

Static validation checks types, schema, unsafe constructs, cost, and compatibility. Fixtures cover positive, negative, boundary, late, duplicate, and missing-field cases. Staging is shadow-only. Activation is atomic and rollback selects an immutable prior version. Managed updates never overwrite tenant forks/suppressions.

Metrics cover evaluation volume/latency, matches, alert yield, lag, state, timeouts, errors, lateness, suppression, and false-positive dispositions. Tenant IDs are not used as uncontrolled high-cardinality labels.
