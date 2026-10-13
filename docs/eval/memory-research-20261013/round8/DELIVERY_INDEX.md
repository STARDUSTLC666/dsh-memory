# 阶段性 Memory 研究交付索引

本次提交的是持续研究的阶段性实验和工程探索，允许负结果，尚不构成生产发布批准。

| 内容 | 文件 |
|---|---|
| 第八轮结论、成本与边界 | ROUND8_REPORT.md |
| 第七轮 13 胜 2 负及全部 D0 失败 | ROUND7_CASE_ANALYSIS.md |
| 新任务逐案例归因 | ROUND8_CASE_ANALYSIS.md / case-attribution.json |
| 配对明细与机读统计 | paired-task-results.csv / results-summary.json |
| 回归、并发、权限、环境与私有缺口 | REGRESSION_REPORT.md |
| 离线复核与实验命令 | REPRODUCE.md / offline_replay.py |
| 最小审查草稿 | D1_PR_DRAFT.md |
| 发布阻塞 | RELEASE_BLOCKERS.md |
| 原始记录与冻结版本 | memory-delivery-round8-complete-20261013.zip |
| 原始包完整性 | evidence-file-manifest.json / archive-receipt.json |
| 第七轮原始结果 | 自有研究分支中的 round7 完整归档 |

研究分支存报告、完整原始归档与实验工具；审查分支从最新上游单独建立，只包含 D1 必需代码、测试和文档。历史轮次资料保留在研究分支已有 docs/eval 下，不把它们合并为独立新样本。新旧原始评分均不修改。完整实验归档含冻结评分真值，公开后不得再次声称该任务集是未见留出集。

反思继续默认关闭，G 暂不推广，无预测控制器/JEPA/自动算法演化。生产 Memory 与 DSH 正式插件没有更新。上游 PR、合并、发布仍未授权执行。
