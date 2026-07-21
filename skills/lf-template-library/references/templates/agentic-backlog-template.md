---
title: "Agentic Run Backlog"
type: agentic-backlog
status: draft
schema_version: 1
---

# Agentic Run Backlog

## Run

- `run_id`: {{run_id}}
- `created_at`: {{created_at}}

## Post-Execution Items

| ID | Source | Type | Status | Description | Suggested Owner |
| --- | --- | --- | --- | --- | --- |
| {{item_id}} | {{source}} | {{type}} | open | {{description}} | {{suggested_owner}} |

## Blockers

| ID | Gate | Status | Required Decision |
| --- | --- | --- | --- |
| {{blocker_id}} | {{gate_type}} | open | {{required_decision}} |

## Non-Blocking Follow-Up

- {{follow_up}}

## Consultive Write Test Outcomes

These items never change the run, task, phase, validator, approval or gate
status. Readers must consume this current template version.

| ID | Checkpoint | Review Handoff | Agent Run | Evidence | Coverage | Risk | Status | Reason | Description | Suggested Owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {{review_backlog_id}} | {{review_checkpoint_id}} | {{review_handoff_id_or_null}} | {{review_agent_run_id_or_null}} | {{review_evidence_ref_or_null}} | {{review_coverage_digest}} | {{review_risk_ref}} | {{review_checkpoint_status}} | {{review_reason_or_null}} | {{review_outcome_summary}} | {{review_suggested_owner}} |
