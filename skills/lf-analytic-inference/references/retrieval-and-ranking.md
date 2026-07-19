# Selective Retrieval and Ranking v1

Read this reference for catalog lookup. Retrieval is deliberately index-first:
it must not read all inference records to discover whether they are relevant.

## Required query evidence

Normalize only observed query data:

- confirmed technology/domain IDs and aliases, with confidence;
- versions and affected surfaces;
- objectives and observable signals;
- available evidence;
- risk, investigation cost constraints, and requested relevant-result floor.

Do not turn an uncertain technology into a confirmed one. If no technology has
sufficient evidence, return `partial` or `insufficient` with the uncertainty.

## Two-stage lookup

1. Resolve only indices whose `technology` or `aliases` match confirmed query
   evidence. An absent or empty index is a valid `insufficient` result.
2. From index metadata, reject entries with incompatible status, version,
   surface, objective, explicit exclusion, or unavailable required evidence.
3. Order candidate summaries deterministically by exact technology, surface,
   objective, signal, compatible version, freshness, risk, cost, then
   `inference_id`. Booleans are descending; risk and cost use caller-declared
   safe preference; `inference_id` is the final ascending tie-breaker.
4. Load only the records that survive deterministic filtering. Validate every
   loaded record and require index/record identity, revision, status, and
   locator parity.
5. Rerank the loaded set semantically for relation to the demand, evidence able
   to confirm or reject it, material-finding potential, risk, and cost. Record a
   short observable reason for each score or ordinal rank.
6. Stop when the relevant floor is met and additional records cannot improve
   material coverage within the approved lookup budget. A floor is not a quota:
   never add an irrelevant record to satisfy it.

## Output

Return:

- confirmed technologies and confidence;
- indices read and record locators loaded;
- selected records labeled `catalogued` with revisions;
- deterministic filter facts and semantic reranking reasons;
- rejected entries and typed reasons;
- stale, incompatible, broken-locator, or uncertain items;
- requested floor, relevant count, and terminal state;
- policy ID and approved-candidate digest when policy limits are used.

The caller must distinguish these reused records from newly generated
inferences. Catalog results are heuristic starting points; the caller remains
free to generate contextual candidates beyond the catalog.

## Failure and stop rules

- Broken, escaping, or mismatched locators are `blocked`, not silently skipped.
- Unknown status, unsupported schema, invalid policy, or duplicate identity is
  `blocked`.
- No adequate record or too few relevant records is `insufficient` or
  `partial`, not padded success.
- Unknown cost remains unknown and cannot consume a fictitious zero budget.
- Exact duplicates may be identified deterministically. Near-duplicates are
  reported for judgment and never merged automatically.
- Retrieval performs no catalog write and grants no promotion,
  reorganization, merge, or purge authority.
