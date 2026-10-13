# Research draft: opt-in source-atomic MCP evidence delivery

Stage of work: experimental implementation and negative-result reporting. Keep this local draft; it is not ready for a formal algorithm promotion PR.

The opt-in mdcg_recall adapter re-reads already-authorized selected nodes, preserves source text, native applicability and exclusions with provenance hashes, counts the full response envelope, and returns explicit INCOMPLETE instead of clipping required evidence. It keeps the legacy default and does not alter retrieval order, permissions or memory content. Unknown JSON retains its full outer source so an ordinary source_document key cannot discard exceptions.

New public-document trials: frozen D46/56 versus B35/56 (13 paired wins,2 losses). The frozen source-atomic S1 candidate reached31/56, largely because whole-bundle budget refusal removed usable evidence; frozen G33/56. Post-campaign S2 fixes schema ambiguity and has identical outputs on the32 frozen A inputs, but has no new model generalization score. Do not promote S/G or retune on this test set.

Validation:13 focused unit cases, latest329 runnable Memory modules,14 native signed-token/MCP engineering scenarios,3 actual isolatedDSH plugin profiles, and71 public-corpus parsing/roundtrip assertions.3 original private-corpus tests remain unavailable; TypeScript148 pass/1 environment probe skip. No production installation, automatic PR submission or model-approved deployment.

Review blockers: substantial task-level regression, incomplete original private-corpus acceptance, limited public-document task families, and source-completeness not guaranteeing evidential sufficiency. Reversible default-off implementation is retained as research material only.
