# Canonical Event Schema

## Contract

The canonical event is an immutable, versioned envelope. JSON is the external representation; internal serialization may differ if round-trip semantics are preserved. Unknown fields go only under namespaced `extensions`; core fields cannot be shadowed.

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | Semantic contract version, initially `1.0.0` |
| `event_id` | UUID/string | Unique ID within tenant |
| `tenant_id` | UUID/string | Trusted server-derived tenant |
| `source_id` | UUID/string | Authenticated data source |
| `event_type` | string | Controlled category, e.g. `authentication.login` |
| `event_time` | RFC 3339 | Time the observation occurred |
| `ingested_at` | RFC 3339 | Platform acceptance time |
| `observed_at` | RFC 3339/null | Collector observation time |
| `severity` | enum | `unknown`, `informational`, `low`, `medium`, `high`, `critical` |
| `outcome` | enum | `unknown`, `success`, `failure`, `partial` |
| `message` | string/null | Bounded human-readable summary |
| `actor`, `target`, `network`, `device`, `cloud` | object/null | Normalized context |
| `labels` | object | Bounded scalar tags; reserved keys prohibited |
| `extensions` | object | Namespaced source-specific data |
| `provenance` | object | Source schema, mapper, receipt, integrity metadata |

Representative fields include `actor.id/type/user/ip`, `target.id/type/resource`, network addresses/ports/protocol, device ID/hostname/OS, cloud provider/account/region/resource, and provenance receipt/source IDs, mapper version, payload hash, and warnings.

## Validation

- Maximum serialized size is initially 256 KiB; strings, arrays, nesting, labels, and extensions have explicit bounds.
- Addresses, ports, timestamps, and identifiers are parsed strictly and normalized.
- Excess event-time skew creates a warning; time is not silently rewritten.
- `tenant_id` and receipt/integrity metadata are server-owned.
- Known credential fields are redacted or rejected before persistence.
- Duplicate identity is `(tenant_id, event_id)`; conflicting duplicates are quarantined and alerted.

## Compatibility

Patch versions clarify constraints; minor versions add optional fields/enums; major versions may break consumers. Producers declare a version, provenance retains mapper version, and readers support current and previous majors during migration. Schema fixtures and compatibility tests gate promotion.

## Example

```json
{
  "schema_version": "1.0.0",
  "event_id": "018f-example",
  "tenant_id": "tenant-example",
  "source_id": "source-example",
  "event_type": "authentication.login",
  "event_time": "2026-07-20T10:00:00Z",
  "ingested_at": "2026-07-20T10:00:02Z",
  "observed_at": null,
  "severity": "informational",
  "outcome": "success",
  "message": "Interactive login succeeded",
  "actor": {"id": "user-42", "type": "user", "ip": "192.0.2.10"},
  "target": {"id": "console", "type": "application"},
  "network": null, "device": null, "cloud": null,
  "labels": {"environment": "production"},
  "extensions": {"vendor.example": {"method": "password"}},
  "provenance": {"receipt_id": "receipt-example", "source_event_id": "abc", "source_schema": "vendor-v2", "mapper_version": "1.0.0", "payload_hash": "sha256:example", "normalization_warnings": []}
}
```
