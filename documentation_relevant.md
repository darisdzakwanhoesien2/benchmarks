# Role-Relevant Infrastructure Documentation

## Purpose

This document defines the software infrastructure scope and delivery expectations for a candidate responsible for three product surfaces:

1. **Annotator’s view**: website + app for data collection and annotation  
2. **Researcher’s view**: dashboard for aggregation and monitoring  
3. **Backend**: fast, robust, safe database and APIs with flexible ontologies

---

## 1) Annotator’s View (Web + App)

### Objective
Enable annotators to capture, review, and submit high-quality structured annotations efficiently across desktop and mobile.

### Core capabilities
- Secure sign-in and role-based workspace access
- Task queue with assignment rules (priority, language/domain, SLA)
- Annotation editor supporting text, label sets, hierarchical labels, and free-form notes
- Ontology-guided suggestions and validation (required fields, disallowed combinations)
- Save draft, autosave, resume session, submit/finalize
- Inter-annotator review workflow (primary vs secondary annotator)
- Conflict resolution + adjudication state
- Offline-first mobile support with sync + conflict handling
- Full history and change tracking per annotation

### Quality controls
- Mandatory schema checks before submit
- Confidence scoring per annotation
- Duplicate/near-duplicate detection
- Gold-standard hidden benchmark tasks for annotator calibration
- Reviewer feedback loop and correction audit trail

### Key UX modules
- `Task Inbox`
- `Annotation Workspace`
- `Ontology Picker`
- `Draft & Version History`
- `Review / Adjudication Panel`
- `Personal Metrics` (throughput, agreement, pending tasks)

### Acceptance criteria (MVP)
- Annotator can complete end-to-end task lifecycle without admin intervention
- Draft recovery works after refresh/app restart
- Validation prevents invalid ontology combinations
- Submission latency < 300ms (p95) on normal payload size

---

## 2) Researcher’s View (Dashboard)

### Objective
Give researchers operational and scientific visibility into annotation progress, quality, and ontology usage.

### Core capabilities
- Dataset and project-level progress tracking
- Throughput by annotator/team/time window
- Quality monitoring:
  - inter-annotator agreement (IAA, Cohen’s kappa/F1 where relevant)
  - adjudication rates
  - error categories
- Ontology coverage:
  - most/least used nodes
  - out-of-ontology labels
  - ontology drift over time
- Filtering by cohort, language, source, annotator, model version, date
- Export views to CSV/JSON for downstream research
- Alerting for bottlenecks (low agreement, high rejection, backlog growth)

### Key dashboard pages
- `Operations Overview`
- `Quality & Agreement`
- `Ontology Coverage`
- `Annotator Performance`
- `Data Exports / Monitoring Logs`

### Acceptance criteria (MVP)
- Dashboard reflects new annotations within near-real-time SLA (<= 1 minute)
- Researchers can reproduce filtered aggregates across sessions
- Exported data matches on-screen aggregates

---

## 3) Backend (Fast, Robust, Safe + Flexible Ontologies)

### Objective
Provide reliable APIs, storage, and ontology services supporting annotation and analytics at scale.

### High-level architecture
- API Gateway (authn/authz, rate limits, request tracing)
- Annotation Service (tasking, draft, submit, review, adjudication)
- Ontology Service (versioning, lookup, validation, compatibility checks)
- Analytics Service (pre-aggregations + researcher dashboard queries)
- Event Bus/Queue for async jobs (indexing, exports, alerts)
- Cache layer for hot reads
- Primary database + backup/replica strategy

### Database design principles
- **Transactional core + flexible schema edges**:
  - relational integrity for users/tasks/states
  - JSONB/document fields for extensible metadata
- **Versioned ontology model**:
  - ontology namespace, version, node, edge, deprecation status
  - mapping table for old->new node migration
- **Auditability**:
  - immutable event log for every create/update/submit/adjudicate action
- **Performance**:
  - indexed task/status/date columns
  - materialized views for dashboard-heavy aggregates
  - pagination-safe query design

### Security & safety requirements
- RBAC at project, dataset, and action level
- Encryption in transit (TLS) and at rest
- PII boundary controls and field-level masking where required
- Signed backups + tested restore procedures
- Tamper-evident audit logs
- Secrets managed outside source code (vault/secret manager)

### Reliability requirements
- API uptime target: 99.9% (or agreed SLA)
- Idempotent write APIs for retries
- Background job retry + dead-letter queue
- Observability: logs, metrics, distributed tracing, alerting
- Disaster recovery runbook with defined RPO/RTO

### Suggested backend entities
- `users`, `roles`, `permissions`
- `projects`, `datasets`, `items`
- `annotation_tasks`, `annotation_assignments`
- `annotation_records`, `annotation_versions`
- `reviews`, `adjudications`
- `ontologies`, `ontology_versions`, `ontology_nodes`, `ontology_edges`
- `ontology_mappings`
- `events_audit`, `exports`, `alerts`

---

## 4) Candidate Responsibilities (Role-Specific)

### Architecture & implementation
- Design and implement the 3-component system with clear API boundaries
- Build production-grade backend services and persistence layer
- Implement ontology versioning and validation engine
- Deliver web/mobile-ready annotator flows and researcher dashboard data paths

### Engineering quality
- Define coding standards, API contracts, and migration strategy
- Add automated testing: unit, integration, and contract tests
- Add CI/CD pipelines with rollback support
- Establish monitoring, alerting, and incident response workflow

### Data governance
- Ensure traceability from annotation input to dashboard metric
- Implement auditability and compliance-ready access controls
- Define data retention, deletion, and export policies

### Collaboration
- Work with research stakeholders to evolve ontology definitions
- Translate annotation policy into enforceable backend validation rules
- Provide technical documentation and handover artifacts

---

## 5) Non-Functional Requirements Summary

- **Performance**: low-latency annotation writes and fast aggregate reads  
- **Scalability**: support growth in annotators, tasks, and ontology complexity  
- **Robustness**: resilient workflows under partial failures  
- **Safety**: secure data handling, audit trails, controlled access  
- **Flexibility**: ontology updates without breaking historical annotations  

---

## 6) Recommended Delivery Plan

### Phase 1 (MVP)
- Auth + RBAC
- Annotation task lifecycle
- Basic ontology lookup/validation
- Core dashboard KPIs
- Audit log + backup baseline

### Phase 2
- Mobile offline sync
- Adjudication and reviewer workflows
- Advanced ontology version migration tools
- Alerting and quality anomaly detection

### Phase 3
- Deeper analytics, model-assist suggestions
- Multi-tenant isolation hardening
- Self-serve ontology administration

---

## 7) Definition of Done

System is considered production-ready when:
- Annotator and researcher workflows are complete and stable
- Backend SLAs and security controls are validated
- Ontology versioning and historical reproducibility are proven
- Monitoring, backup/restore, and incident runbooks are in place
- Documentation and handover are complete

