# Mar 2026

3/1/2026 - Ari's sticky-session headache: scale WebSockets globally without slowing users
Ari is the backend architect for a social app with millions of daily active users. The system has WebSocket connections for real-time updates plus a REST API. Traffic is global and peaks produce large numbers of concurrent connections. Ari needs a load balancing strategy that minimizes end-user latency, keeps the system highly available during region failures, and avoids complex cross-region coordination for session state. The current implementation uses per-node in-memory sessions and an L7 global load balancer with sticky cookies; failures and autoscaling cause dropped connections and uneven load. Which architectural approach should Ari choose to best balance scalability, availability, latency, consistency, observability, and operational simplicity?

Ans:

Refactor services to be effectively stateless: move session/connection metadata to regional, highly available stores (short-lived tokens or regional Redis/DB), prefer regional routing to nearest cluster, and use simple L4/anycast or regional LBs. For WebSockets, accept local affinity at the region level and fail over by re-establishing connections with state fetched from the regional store.

**DETAILED EXPLANATION:**

Option B is the best balance for Ari's constraints. Making services effectively stateless and moving session/connection metadata into regional, highly available stores (or using signed short-lived tokens) enables low latency by keeping reads/writes local to a region, simplifies autoscaling and replacement of backend nodes, and improves availability because a region can continue serving users even if individual nodes fail. For WebSockets, regional affinity is usually sufficient: keep long-lived TCP/WebSocket connections to a local node, but persist minimal session state to a regional store so clients can reconnect to a different node in the same region without losing important context. Use health checks and connection draining to minimize dropped connections during maintenance, and rely on regional load balancers or anycast to route traffic to the nearest healthy cluster. Instrumentation (metrics/traces/logs) remains straightforward because session state is in a known store and requests are mostly stateless at the app layer.

Why the others are less suitable:

- Option A: L7 sticky sessions via cookies plus DNS weight routing ties clients to node-level state, causing uneven load and fragile failover. DNS routing is coarse-grained, and sticky cookies across regions break during failovers or autoscaling. Connection draining helps but doesn't solve the fundamental state coupling and adds operational complexity.
- Option C: Client-side load balancing with consistent hashing can reduce pressure on central LBs, but it forces complex client logic or sidecars and makes routing/observability harder. Asynchronous replication of session state across nodes leads to eventual consistency problems and race conditions for real-time updates, and adds a lot of operational overhead to keep replication correct under churn.
- Option D: A single strongly consistent global session store simplifies consistency but dramatically increases latency for many global users, creates a critical single point of failure or complex multi-master setups, and scales poorly under huge concurrent connection counts. Routing everything through a primary region defeats the goal of low latency and high availability for global users.

Trade-offs covered: B optimizes for latency and availability by favoring locality and statelessness; it accepts that some operations (cross-region failover) will require reconnection and short-lived state transfer rather than synchronous global consistency. This leads to simpler operations, better autoscaling, and clearer observability because session state is stored in predictable places.

---

3/2/2026 - **Jasper must stop dashboards from dragging down production DB; what's the plan?**

Jasper is a backend engineer on a payments platform. Every morning, a set of heavy SQL reports for business dashboards runs against the primary transactional database. Recently these reports started causing high CPU, long tail latency for user-facing requests, and occasional replica lag. Jasper can use EXPLAIN to optimize individual queries, but the team needs an architectural decision that solves the systemic problem long-term while balancing cost, latency, consistency, and observability. Which approach should Jasper pick?

Ans:

Move reporting to a separate analytics path: create periodic ETL/CDC pipelines that populate pre-aggregated tables or materialized views in a dedicated analytics cluster (columnar store or OLAP DB). Run dashboards against that store and set an appropriate refresh frequency for business needs.

**DETAILED EXPLANATION:**

Option C is the best long-term architectural choice for this scenario. Separating transactional and analytical workloads gives predictable performance, reduces risk to user-facing requests, and lets you pick a system optimized for heavy scans and aggregations (columnar storage, compression, vectorized execution). Using ETL or CDC to populate pre-aggregated tables or materialized views lets you control freshness (minutes, hourly, daily) according to business needs, and makes query plans simple and stable. It also improves observability: you can monitor pipeline lag, materialized view refresh times, and query latency in the analytics cluster independently from the primary DB. Fault isolation is stronger; heavy analytic load can't consume primary DB resources; and cost is more predictable since you size the analytics cluster separately.

Why the others are less suitable:

- Option A (tune on primary): Good short-term and low-complexity. EXPLAIN-driven tuning and throttling can reduce impact, but it doesn't address the fundamental mismatch: OLTP engines are not optimized for repeated full-table scans and wide aggregations. As data and query volume grow, you’ll keep fighting index/plan churn. Scheduling reports off-peak helps but doesn't eliminate risk to latency and availability, and throttling reduces business value of near-real-time dashboards.
- Option B (synchronous read replicas): Synchronous replicas add operational and latency cost to writes and do not eliminate load on primary if replicas are synchronous (they can increase write latency or reduce write availability). If replicas are asynchronous to avoid write impact, you get replica lag and therefore weaker read freshness, which can be unacceptable for business dashboards. Replicas scale read throughput but are still an OLTP engine and suffer the same inefficiencies for analytical patterns (many random I/O, insufficient columnar compression). Also debugging cross-replica query performance can be harder and replicas add complexity in failover.
- Option D (federated engine): A federated engine gives flexibility and avoids upfront ETL, and predicate pushdown reduces data movement for some queries. But federated queries that join across systems or scan large tables still move data across the network and create unpredictable latency. The query planner’s cost model might not accurately reflect multiple heterogeneous systems, making EXPLAIN output harder to interpret across sources. Federated setups can be useful for ad hoc exploration but typically don’t provide the predictable, low-latency performance and isolation that dashboards need at scale.

When to pick alternatives: If the dashboard needs strictly real-time data within milliseconds, you might need a streaming/CDC pipeline with near-real-time sync and tuned materialized views (still Option C but with higher refresh rate). If the workload is low-volume and you want minimal operational overhead, start with option A while monitoring capacity and query plans. Federated engines are useful for ad hoc analytics across many sources before committing to ETL. Read replicas can be an intermediate step when read freshness tolerates lag and analytic queries are modest.

Operational tips for Option C: use CDC to minimize full-table refreshes, design incremental/partitioned materialized views, choose partitioning and compression suited to your access patterns, add observability on ETL lag and refresh failures, and continue using EXPLAIN on the analytics cluster to tune long-running aggregation queries.

---

3/3/2026 - **When to Strangle the Legacy: safe migration choices**

Mateo is a senior backend engineer at an online marketplace that has a large, monolithic order service (the legacy). The team wants to migrate order handling to a new microservice using the Strangler Fig pattern so they can iterate faster and scale parts independently. The legacy handles ~5k writes/sec and low-latency reads, and the business requires near-zero data loss, predictable read-after-write behavior for most operations, strong observability, and the ability to rollback quickly if problems appear. Mateo must choose an approach that minimizes customer-visible errors, supports incremental cutover by customer segment, and avoids long periods of hard-to-debug dual-write bugs or data drift. Which architectural approach should he pick?

Ans:

Incremental strangling with traffic mirroring + transactional outbox: add an API gateway with feature flags and canaries, mirror (shadow) production traffic to the new service for testing, and adopt an outbox pattern in the legacy writes so the new service consumes a reliable event stream. Gradually switch segments to the new service, keep strong observability, and rely on the outbox to avoid dual-write inconsistencies and allow easy rollback.

**DETAILED EXPLANATION:**

D is the best fit because it supports an incremental Strangler Fig migration while minimizing data-loss risk and avoiding the brittle, hard-to-debug dual-write problem. The outbox pattern turns legacy writes into a reliable, ordered event stream that the new service can consume; this gives a single source of truth (the legacy DB) for writes while enabling near-real-time replication without needing distributed transactions. Traffic mirroring and canary/feature-flag-driven cutovers let the team validate behavior and rollback quickly if issues appear. Strong observability (metrics, tracing, error budgets) can be implemented on mirrored traffic before cutting over real users.

Why not the others?

- A (big-bang) is high risk at this scale: long maintenance windows, data-migration time, and limited rollback capability make it unsuitable for 5k writes/sec and strict uptime/availability needs.
- B (synchronous dual-write with distributed transactions) seems to give strong consistency but is operationally complex, brittle, and often causes latency spikes or partial failures. Two-phase commit across heterogeneous systems increases coupling and recovery complexity; it also makes rollbacks and gradual rollout harder.
- C (pure async CDC/event-driven) is closer but incomplete: treating the legacy as source-of-truth and asynchronously replicating is good, but if you rely purely on eventual consistency without an outbox/CDC or without safe mirroring and careful cutover controls, you risk long windows of data drift and user-visible read-after-write anomalies. C can be acceptable when strict immediate consistency isn't required, but it lacks the safer deployment controls and guaranteed delivery the outbox + mirrored traffic approach provides.

Overall, approach D gives the best balance of safety, incremental rollout, observability, and avoidance of dual-write inconsistency while supporting rollback and production testing before full cutover.

---

3/4/2026 - **Rohan's Dilemma: How to Mock Dependencies Without Breaking Production**

Rohan is a backend engineer working on a high-throughput microservice that handles order processing. The service talks to an internal Auth service (HTTP), a third-party payment gateway (HTTP), and publishes events to a Kafka cluster. The team needs a testing strategy and DI approach that keeps unit tests fast, catches integration regressions early, and preserves confidence in non-functional behavior (latency, retries, and eventual consistency). Rohan must pick an approach for using dependency injection and mocks across the test pyramid that balances developer velocity, CI reliability, and production safety. Which architectural approach should he choose?

Ans:

Hybrid: use DI to inject lightweight, behaviorally accurate test doubles for unit tests; enforce consumer-driven contract tests (e.g., Pact) for service-to-service APIs; and run periodic ephemeral CI integration tests using real-like infra (testcontainers or ephemeral clusters) that validate non-functional behaviors and failure modes.

**DETAILED EXPLANATION:**

Option D is the best balance for distributed systems. Using DI to inject lightweight, behaviorally accurate doubles keeps unit tests fast and focused while preserving the ability to simulate error paths (timeouts, retries, transient errors). Consumer-driven contract tests lock in the interaction surface between services so changes are detected by consumers before deployments; they are much cheaper and less brittle than relying only on full integration runs. Running periodic ephemeral integration tests (via testcontainers, ephemeral clusters, or CI-provisioned environments) validates non-functional properties; latency, backpressure, eventual consistency, and failure modes; in a controlled, reproducible way.

Why the others are less suitable:

- A (centralized service virtualization): A shared mock server can speed tests, but it centralizes a single canned view of behavior that often drifts from reality. It tends to hide latency, partial failures, and subtle contract mismatches, and becomes a single source of brittle coupling that hurts availability and observability when behaviour diverges from real systems.
- B (integration-first): Running everything against real services in CI gives high fidelity but is slow, expensive, and brittle. Shared staging environments introduce flakiness (environment contention) and make the pipeline less scalable. They also slow developer feedback loops and can mask consumer-specific contract expectations if not paired with consumer-driven checks.
- C (unit stubs only): Simple in-process stubs are great for unit correctness but usually don’t model important non-functional behavior (network latency, retries, eventual consistency, message ordering). Relying on ad-hoc smoke tests pushes discovery of integration bugs later, increasing blast radius and reducing system availability.

Trade-offs addressed by D:

- Scalability & latency: Fast unit tests scale in CI; ephemeral integration tests run in isolated environments to measure latency implications without slowing every commit.
- Availability & fault tolerance: Contract tests plus targeted integration tests catch breaking changes and failure-mode regressions earlier, reducing production incidents.
- Consistency: Consumer-driven contracts make expectations explicit and help avoid mismatches that cause consistency failures.
- Observability: Contract failures and integration test metrics feed CI dashboards and alerts, giving clear signals about where to investigate.

Implementation tips: design DI abstractions that let test doubles simulate timeouts, throttling, and partial failures; automate publishing and verification of consumer contracts in CI; use ephemeral infra so integration tests are reproducible and isolated.

---

3/5/2026 - **Liam's NULL Problem: Fix at Source or Patch at Read?**

Liam is a backend engineer owning an event-driven Orders service used by dozens of microservices. Over time many older orders contain NULLs in fields like billing_country, customer_tier, and promo_code. Some downstream reports and materialized views use COALESCE(column, 'DEFAULT') in queries to avoid NULLs; other services apply their own defaults at read time. The system is high-throughput (thousands of writes/s), sharded Postgres for OLTP, Kafka for events, and Redis caches in front of several read-heavy APIs. Liam must choose an architecture to handle NULLs and defaults going forward; balancing latency, scalability, availability, consistency, observability, and operational effort. Which approach should he pick?

Ans: 

Make defaults first-class: add NOT NULL + DEFAULT constraints where appropriate, run a coordinated background backfill to fix historical rows, and enforce producer-side validation (schema registry + contract checks). Use COALESCE only temporarily during migration and compatibility windows.

**DETAILED EXPLANATION:**

Option C is the best long-term architecture for a high-throughput, distributed backend. Making defaults part of the schema and backfilling historical data produces a single source of truth, reduces per-read work, preserves index behavior, and makes behavior consistent across consumers. Benefits and rationale: - Consistency: NOT NULL + DEFAULT enforces a contract at storage level so every reader sees the same canonical value. - Performance & latency: removing COALESCE and read-time normalization reduces CPU per query and avoids potential plan regressions; queries become simpler and more cache-friendly. - Indexes & sargability: predicates and index usage are more predictable when columns are non-null and have stable values; wrapping columns in COALESCE inside WHERE clauses can prevent indexes from being used efficiently in some databases. - Observability & debugging: a single canonical model reduces surprising differences between consumers and eases alerting and monitoring. - Operational safety: with a careful, chunked background backfill and producer validation (schema registry, client-side checks), you can apply changes with minimal downtime and rollback capability. COALESCE remains useful as a temporary compatibility shim during migration windows. Why the others are less suitable: - Option A (COALESCE everywhere): Low friction initially but pushes normalization to runtime. That increases DB CPU, may hide data-quality bugs, risks inconsistent defaults across ad-hoc queries and reports, and can hurt query plans and index usage. It’s a maintenance burden on complex queries and materialized views. - Option B (API edge normalization): Centralizing normalization at the gateway reduces DB load but creates a new choke point and coupling. It also leaves the canonical stored data unchanged (so analytics, older consumers, and caches might still see NULLs), and it adds complexity and operational risk in the gateway. It also doesn’t help indexing or query patterns inside the DB. - Option D (per-service defaults + eventual repair): Minimizes upfront work but leads to inconsistent behavior across services, harder-to-reproduce bugs, and more complexity in reasoning about correctness. Eventual repairs also delay strong guarantees and make cross-service invariants fragile. Practical notes for implementing C safely: - Do chunked updates or backfill using batches to avoid long locks; test on replica first. - For Postgres versions that rewrite tables when adding DEFAULT, prefer an online-safe migration path (add column nullable, backfill in batches, then alter to NOT NULL). - Run producer-side validation (schema registry or middleware) to prevent reintroducing NULLs. - Use short-lived COALESCE in SELECTs or API responses only during the migration window. Overall, invest in schema-level fixes and producer contracts for long-term reliability, and use read-time normalization only as a compatibility bridge.