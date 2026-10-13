# Opt-in evidence-preserving MCP delivery (D1)

The legacy recall packet can contain only a prefix of an already-authorized memory.
D1 re-reads the **same selected IDs** through `MdCGSecure.get`, then reuses the
existing D query-window renderer. Native applicability, exclusions, provenance,
effective dates, observation windows, versions and verification basis remain in
the rendered metadata. Arbitrary JSON memory bodies are never projected into a
guessed `source_document` field. Source hashes and character spans identify the
exact stored text; memory content, retrieval order and permission checks do not change.

`mdcg_recall(delivery_mode="evidence_preserving", evidence_budget_tokens=1200)`
enables D1 explicitly. Default `delivery_mode="original"` returns the old packet.
The budget counts the **whole serialized result using the project estimator**;
it is not a claim about billed model tokens. Truncated or omitted selected sources
are `INCOMPLETE`; no source is `INSUFFICIENT`. `COMPLETE_SELECTED_SOURCES` means
the selected sources fit, not that retrieval is exhaustive or their claims true.
Callers must DEFER on incomplete or insufficient evidence and may retrieve again
with a deliberate larger budget. Recent-event delivery is unsupported in D1 and
fails explicitly as INCOMPLETE; use the original path for that feature.

D0's historical 46/56 result used a research trace projection and a different
response adapter. **It is not a score for D1.** D1 fixes metadata and partiality
invariants and requires its own frozen independent evaluation. Neither the G
budget optimizer nor source-atomic S, reflection or RSI controllers are included.

To roll back, unset the opt-in or use `delivery_mode="original"` and restart only
the isolated test MCP process. No database migration or second authority is added.
Keep the original private-corpus acceptance gaps and any D1 regressions explicit;
local tests cannot authorize production rollout or remote PR submission.
