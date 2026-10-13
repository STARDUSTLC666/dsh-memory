# Draft: isolate verifier process checks and aggregation clocks in tests

Stage of work: experimental stabilization and evidence collection. This is a local review draft only; no PR has been created or updated.

The verifier timeout regression used a machine-wide python.exe count, so unrelated concurrent tests could trip its cleanup assertion. Track exactly the launched processes and their actual Windows venv worker handles, require zero owned survivors, and preserve a deliberate real-worker leak negative control. The verifier implementation and timeout limits are unchanged.

The mode parity test also hashed an aggregation body containing a wall-clock minute. Inject a fixed test stamp through the existing API, preserving exact tombstone and mutation assertions.

Validation: latest full randomized parallel Memory suite 329/329 runnable modules; 3 original private-corpus modules unavailable. Focused actual-worker checks 144/144 across concurrency1/2/4/8 and3 shuffle seeds. Both mutation suites passed. Full logs and failed/incomplete historical batches are preserved in the research archive.

Scope: only md_cg/test_issue91_verifier_timeout.py and md_cg/test_mode_parity.py. No production plugin/configuration, identity permissions or reflection changes. Experimental source-atomic delivery is a separate patch and is not proposed for promotion.
