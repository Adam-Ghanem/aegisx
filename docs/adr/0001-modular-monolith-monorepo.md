# ADR 0001: Modular Monolith in a Monorepo

- Status: Accepted
- Date: 2026-07-20

## Context

AegisX needs strong domain boundaries without the operational and consistency cost of premature microservices.

## Decision

Use one monorepo and a modular monolith. Domain, application, and infrastructure concerns expose explicit ports; FastAPI entry points compose them. A worker entry point may share packages but cannot bypass application policies. Modules do not import another module's persistence internals.

## Consequences

Transactions, migrations, local development, and policy testing remain simple. Independent deployment and scaling are deferred until measured load or failure isolation justifies extraction. Contract tests must preserve module boundaries.

