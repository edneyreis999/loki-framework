# Selective Retrieval and Ranking v2

Read this reference for catalog lookup. Retrieval is deliberately index-first:
it must not read all inference records to discover whether they are relevant.

## Required query evidence

Normalize only observed query data:

- confirmed technology/domain IDs and aliases, with confidence;
- versions and affected surfaces;
- objectives and observable signals;
- available evidence;
- an optional opaque retrieval cursor and the active policy's
  `catalog_retrieval_page_size`. Page size is transport capacity, never a total
  result ceiling.

Do not turn an uncertain technology into a confirmed one. If no technology has
sufficient evidence, return `partial` or `insufficient` with the uncertainty.

## Two-stage lookup

1. Resolve only indices whose `technology` or `aliases` match confirmed query
   evidence. An absent or empty index is a valid `insufficient` result.
2. From index metadata, reject entries with incompatible status, version,
   surface, objective, explicit exclusion, or unavailable required evidence.
3. Order candidate summaries deterministically by exact technology, surface,
   objective, signal, compatible version, freshness, then `inference_id`.
   Matching booleans are descending and `inference_id` is the final ascending
   tie-breaker. Cost and impact are not retrieval ranking inputs.
4. Load only the records that survive deterministic filtering. Validate every
   loaded record and require index/record identity, revision, status, and
   locator parity.
5. Rerank the loaded set semantically only for relation to the demand,
   investigability, observable provenance support, validity/compatibility, and
   evidence able to confirm or reject it. Record a short observable reason for
   each ordinal rank.
6. Return eligible records in deterministic pages of at most
   `catalog_retrieval_page_size`. Preserve the next cursor and continue until
   the eligible sequence is exhausted. Reject irrelevant, invalid,
   incompatible, unverifiable, and exact-duplicate records. Defer only
   unresolved essential evidence, compatibility, or context. A page boundary
   never rejects or defers an eligible record and never means total exhaustion.

## Output

Return:

- confirmed technologies and confidence;
- indices read and record locators loaded;
- selected records labeled `catalogued` with revisions;
- deterministic filter facts and semantic reranking reasons;
- rejected entries and typed reasons;
- stale, incompatible, broken-locator, or uncertain items;
- page size, pages read, exhaustion state, next cursor, eligible count,
  selected count, and terminal state;
- policy ID and approved-candidate digest when policy limits are used.

The caller must distinguish these reused records from newly generated
inferences. Catalog results are heuristic starting points; the caller remains
free to generate contextual candidates beyond the catalog.

## Failure and stop rules

- Broken, escaping, or mismatched locators are `blocked`, not silently skipped.
- Unknown status, unsupported schema, invalid policy, or duplicate identity is
  `blocked`.
- No adequate record is `insufficient` or `partial`, not padded success.
- Cost and impact do not participate in pre-investigation retrieval,
  disposition, or the preparation candidate schema.
- Exact duplicates may be identified deterministically. Near-duplicates are
  reported for judgment and never merged automatically.
- Retrieval performs no catalog write and grants no promotion,
  reorganization, merge, or purge authority.
