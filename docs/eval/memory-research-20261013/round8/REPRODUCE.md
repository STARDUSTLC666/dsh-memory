# 复核与重跑

默认离线复核，不访问 API、不修改生产目录。解压本轮 ZIP 后，在新目录运行：

```powershell
python -B -X utf8 research/offline_replay.py research
```

复核 144 次主实验和 3 次开发实验的冻结真值、外部执行评分、API usage、请求/工具预算、可见引用、27 次真实 DSH 历史写入，并显式保留 1 次成功但违反 INCOMPLETE 的结果。原始 ZIP 有逐文件 SHA256 清单与 CRC 复核。附带 evaluator runtime 面向 Windows CPython 3.12；其他环境按 evaluator-dependencies.json 安装固定版本依赖，不能声称直接跨平台可执行。

候选检出后的项目检查（先安装仓库既有开发依赖并配置 Python，所有测试根目录独立）：

```powershell
python -B -X utf8 -m md_cg.test_evidence_delivery_invariants
python -B -X utf8 -m md_cg.test_issue75_source_newlines
python -B -X utf8 -m md_cg.test_issue75_neural_failure --mutate A
cargo build --release --offline --manifest-path rust/Cargo.toml
python -B -X utf8 scripts/run_tests.py --jobs 8
node node_modules/typescript/bin/tsc -p tsconfig.json
node --import tsx --test "test/*.test.ts"
```

本轮完整乱序并发复核使用归档中的 run_stability.py，为每个测试分配 E 盘唯一状态/缓存/租户/临时目录并保留完整输出。公共 run_tests.py 的模块数与归档脚本的 Memory-only 口径应区分。

原付费实验的 scripts/common.py、run_dsh.mjs 包含当时明确冻结的本机研究路径。换机器需在新运行版本中改根路径、确认独立 profile/最小凭据并重新冻结，不能直接指向生产配置。原始配置展示在每个试验的 profile.patch.json、actual-native-arguments.json 与 request-configs.json；模型只见任务和允许 A 证据，不见 private-truth。发布后的真值可供审计，但该数据从此不能再作为未见过的留出集。

如需复跑模型，deepseek-official/deepseek-flash、reasoning=off、8 requests、14 model tools、每请求 2048 output、120 秒、retries=0。服务端无可用采样 seed，不能保证逐答案复现。不得自动重跑失败并挑最好结果。A 历史写入为确定性真实 DSH 工具调用，0 API；每次 B 使用新的 DSH 会话及同一源图副本。完整归档保留所有尝试。
