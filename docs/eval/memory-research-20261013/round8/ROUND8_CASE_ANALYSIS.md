# 第八轮逐案例分析

48 个配对按任务、重复列入 `paired-task-results.csv`；以下覆盖全部非平局及 D1 失败。没有修改任何原始答案、成功标准或评分。

## r8-http-1 / repeat 1 — B=0 D1=1

分类：same_facts_different_metadata_presentation

Correct source body is visible in B and D1. Native B contains consistency/qualification fields; D1 presents a whitelist. Changed agent adoption is observed; attention or framing is an inference, not isolated causal proof.

B 候选 ['r8_http_1_0']；选中 ['r8_http_1_0']；截断 []。

D1 交付 ['r8_http_1_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-http-1/rep-1/D1`。

确定性判定：B checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-2 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_http_2_1', 'r8_http_2_0']；选中 ['r8_http_2_1', 'r8_http_2_0']；截断 ['r8_http_2_0']。

D1 交付 ['r8_http_2_1', 'r8_http_2_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-http-2/rep-2/D1`。

确定性判定：B checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-3 / repeat 1 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_http_3_0', 'r8_http_3_1']；选中 ['r8_http_3_0', 'r8_http_3_1']；截断 ['r8_http_3_1']。

D1 交付 ['r8_http_3_0', 'r8_http_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-http-3/rep-1/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-3 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_http_3_0', 'r8_http_3_1']；选中 ['r8_http_3_0', 'r8_http_3_1']；截断 ['r8_http_3_1']。

D1 交付 ['r8_http_3_0', 'r8_http_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-http-3/rep-2/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-4 / repeat 2 — B=1 D1=0

分类：agent_wrong_http_status, submitted_action_disagrees_with_reason

Full current rule and native exclusion are visible. Deterministic RFC-order scorer finds wrong status array; textual reason even includes the correct correction, but committed output does not.

B 候选 ['r8_http_4_0']；选中 ['r8_http_4_0']；截断 []。

D1 交付 ['r8_http_4_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-http-4/rep-2/D1`。

确定性判定：B checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': True}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-5 / repeat 2 — B=1 D1=0

分类：agent_uses_expired_evidence, submitted_action_disagrees_with_reason

D1 text retains the explicit expired-on-2026-09-30 statement; ANSWER is submitted anyway. The scorer correctly requires empty DEFER.

B 候选 ['r8_http_5_0']；选中 ['r8_http_5_0']；截断 []。

D1 交付 ['r8_http_5_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-http-5/rep-2/D1`。

确定性判定：B checks={'defer_empty': True}；D1 checks={'defer_empty': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-6 / repeat 1 — B=0 D1=0

分类：long_source_delivery_incomplete

Original A contains the needed policy; B truncates it; D1 exposes query windows but explicitly marks the source INCOMPLETE. DEFER is safe yet fails the fixed completion target.

B 候选 ['r8_http_6_0']；选中 ['r8_http_6_0']；截断 ['r8_http_6_0']。

D1 交付 ['r8_http_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-http-6/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-6 / repeat 2 — B=0 D1=0

分类：long_source_delivery_incomplete

Original A contains the needed policy; B truncates it; D1 exposes query windows but explicitly marks the source INCOMPLETE. DEFER is safe yet fails the fixed completion target.

B 候选 ['r8_http_6_0']；选中 ['r8_http_6_0']；截断 ['r8_http_6_0']。

D1 交付 ['r8_http_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-http-6/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-http-7 / repeat 1 — B=1 D1=0

分类：agent_wrong_http_status, submitted_action_disagrees_with_reason

Full current rule and native exclusion are visible. Deterministic RFC-order scorer finds wrong status array; textual reason even includes the correct correction, but committed output does not.

B 候选 ['r8_http_7_0']；选中 ['r8_http_7_0']；截断 []。

D1 交付 ['r8_http_7_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-http-7/rep-1/D1`。

确定性判定：B checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': True}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'status_semantics': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-1 / repeat 2 — B=0 D1=1

分类：same_facts_different_metadata_presentation

Correct source body is visible in B and D1. Native B contains consistency/qualification fields; D1 presents a whitelist. Changed agent adoption is observed; attention or framing is an inference, not isolated causal proof.

B 候选 ['r8_jsonschema_1_0']；选中 ['r8_jsonschema_1_0']；截断 []。

D1 交付 ['r8_jsonschema_1_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-jsonschema-1/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'schema_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-2 / repeat 1 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；选中 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；截断 ['r8_jsonschema_2_1']。

D1 交付 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-jsonschema-2/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'schema_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-2 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；选中 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；截断 ['r8_jsonschema_2_1']。

D1 交付 ['r8_jsonschema_2_0', 'r8_jsonschema_2_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-jsonschema-2/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'schema_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-3 / repeat 1 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；选中 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；截断 ['r8_jsonschema_3_1']。

D1 交付 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-jsonschema-3/rep-1/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-3 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；选中 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；截断 ['r8_jsonschema_3_1']。

D1 交付 ['r8_jsonschema_3_0', 'r8_jsonschema_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-jsonschema-3/rep-2/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-4 / repeat 1 — B=0 D1=1

分类：model_budget_or_submission_failure

B has no accepted answer; raw turn_end/model requests establish failure, not memory absence. D1 successful result does not establish a unique mechanism.

B 候选 ['r8_jsonschema_4_0']；选中 ['r8_jsonschema_4_0']；截断 []。

D1 交付 ['r8_jsonschema_4_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-jsonschema-4/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': False, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'schema_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-6 / repeat 1 — B=0 D1=0

分类：long_source_delivery_incomplete

Original A contains the needed policy; B truncates it; D1 exposes query windows but explicitly marks the source INCOMPLETE. DEFER is safe yet fails the fixed completion target.

B 候选 ['r8_jsonschema_6_0']；选中 ['r8_jsonschema_6_0']；截断 ['r8_jsonschema_6_0']。

D1 交付 ['r8_jsonschema_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-jsonschema-6/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-jsonschema-6 / repeat 2 — B=0 D1=1

分类：task_success_with_caller_safety_violation

D1 explicitly returned INCOMPLETE, but submit_answer committed ANSWER; original score remains passed.

B 候选 ['r8_jsonschema_6_0']；选中 ['r8_jsonschema_6_0']；截断 ['r8_jsonschema_6_0']。

D1 交付 ['r8_jsonschema_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-jsonschema-6/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'schema_semantics': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-1 / repeat 2 — B=0 D1=1

分类：same_facts_different_metadata_presentation

Correct source body is visible in B and D1. Native B contains consistency/qualification fields; D1 presents a whitelist. Changed agent adoption is observed; attention or framing is an inference, not isolated causal proof.

B 候选 ['r8_sqlite_1_0']；选中 ['r8_sqlite_1_0']；截断 []。

D1 交付 ['r8_sqlite_1_0']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 1/1；原始日志 `runs/prospective/r8-sqlite-1/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'executed_query_truth': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-2 / repeat 1 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；选中 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；截断 ['r8_sqlite_2_1']。

D1 交付 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-sqlite-2/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'executed_query_truth': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-2 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；选中 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；截断 ['r8_sqlite_2_1']。

D1 交付 ['r8_sqlite_2_0', 'r8_sqlite_2_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-sqlite-2/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': True, 'cited_past_source': True, 'executed_query_truth': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-3 / repeat 1 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；选中 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；截断 ['r8_sqlite_3_1']。

D1 交付 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-sqlite-3/rep-1/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-3 / repeat 2 — B=0 D1=1

分类：delivery_recovers_current_or_conflicting_source

B native recall marks selected source truncated; D1 re-reads the same selected IDs and returns whole sources; revision/retraction clause is present in saved D1 text.

B 候选 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；选中 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；截断 ['r8_sqlite_3_1']。

D1 交付 ['r8_sqlite_3_0', 'r8_sqlite_3_1']；状态 `COMPLETE_SELECTED_SOURCES`；全文可见 2/2；原始日志 `runs/prospective/r8-sqlite-3/rep-2/D1`。

确定性判定：B checks={'defer_empty': False}；D1 checks={'defer_empty': True}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-6 / repeat 1 — B=0 D1=0

分类：long_source_delivery_incomplete

Original A contains the needed policy; B truncates it; D1 exposes query windows but explicitly marks the source INCOMPLETE. DEFER is safe yet fails the fixed completion target.

B 候选 ['r8_sqlite_6_0']；选中 ['r8_sqlite_6_0']；截断 ['r8_sqlite_6_0']。

D1 交付 ['r8_sqlite_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-sqlite-6/rep-1/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。

## r8-sqlite-6 / repeat 2 — B=0 D1=0

分类：long_source_delivery_incomplete

Original A contains the needed policy; B truncates it; D1 exposes query windows but explicitly marks the source INCOMPLETE. DEFER is safe yet fails the fixed completion target.

B 候选 ['r8_sqlite_6_0']；选中 ['r8_sqlite_6_0']；截断 ['r8_sqlite_6_0']。

D1 交付 ['r8_sqlite_6_0']；状态 `INCOMPLETE`；全文可见 0/1；原始日志 `runs/prospective/r8-sqlite-6/rep-2/D1`。

确定性判定：B checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}；D1 checks={'answer_disposition': False, 'cited_past_source': True, 'external_execution_valid': False}。完整模型提交、参考范围与诊断 ID 见 `case-attribution.json`。
