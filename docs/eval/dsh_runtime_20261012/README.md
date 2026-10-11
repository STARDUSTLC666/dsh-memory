# 两项记忆优化在真实 DSH 宿主中的集成验收

意图声明：核验检索文本投影缓存与 recall 摘录预算修复能一起通过 DSH 的实际插件安装、工具执行、Python/MCP 桥接和提示组装流程。

预期结果：隔离安装后注册六个工具；写入可读、审核前更新不生效、审核后新内容可检索且旧精确命中消失；80 token 摘录保留证据；重启宿主和 Python 进程后仍可读取持久化结果；自动记忆块保留 untrusted 标记。

可信边界：Windows、Node 24.16.0、Python 3.12.10、DSH 0.2.0-rc.1 / Cordis 4.0.4。测试使用新建 profile、合成 Markdown、独立凭据和临时目录。调用真实 `ctx.tools.execute` 和 `ctx.systemPrompt.assemble`，没有替换生产工具、检索函数或提示服务。没有调用远程 LLM、发送聊天消息或进行网页点击验收；也没有测并发、吞吐或生产数据。功能调用耗时只作原始记录，不作为性能对照。

## 实测结果

| 阶段 | 通过检查 | 实际 DSH 工具调用 | 结果 |
|---|---:|---:|---|
| 新 profile 功能链路 | 25 | 19 | PASS |
| 重启后读取及提示组装 | 15 | 10 | PASS |
| 合计 | 40 | 29 | 失败 0，跳过 0 |

- 通过 `dsh plugin --profile memory-lab add <tgz> --ignore-scripts` 安装本地构建包，通过 DSH CLI 启动实际宿主。
- `cg(info)`、`stg(timeline)`、`mdcg_remember`、`mdcg_recall`、`mdcg_search`、`mdcg_get` 均经真实宿主工具服务执行。
- 英文记忆的 `evidenceKEEP42` 位于旧算法过早截断的位置。`recall` 和 `cg(read)` 的 80 token 摘录均保留它，完整摘录含省略号仍为 80 估算 token，资格仍为 `unverified / BLINDSPOT`。零预算返回空包。
- 对中文 CCG 记录重复检索三次，id、score、state、content 一致。更新先进入 `review_queue`，审核前原文不变；调用既有审核入口接受这条合成更新后，新关键词返回新正文，旧关键词不再命中该节点。
- 缺少 CCG 六要素的写入仍被拒绝，缺失节点返回结构化 `not_found`。
- 内部共享记忆按项目现有语义可跨查询 session 声明读取；timeline 的 session 视图过滤也验证通过。没有把查询 session 当成身份隔离权限。
- 自动记忆块实际进入 DSH 提示组装流程，并保留 `<untrusted-memory>` 标记；这里只核验注入与标记，不推断模型是否会服从其中的内容。
- 第二阶段只读已有数据，不重新写入。两阶段 Python PID 不同，三个生产文件 SHA256 一致。

[readings.json](readings.json) 保留全部调用参数、返回值、耗时、逐条断言、版本、文件指纹和两个进程的 PID。绝对本机目录替换成 `${LAB}`、`${HARNESS}`、`${PYTHON}`；本地启动日志及凭据不进入证据。CI 的依赖/私有语料跳过与这里的 40 项检查是不同范围。

## 源码身份

对应 [PR #116](https://github.com/FuRongJun-1999/dsh-memory/pull/116) 与 [PR #117](https://github.com/FuRongJun-1999/dsh-memory/pull/117)。本分支是两项改动的联合验收分支，不代表已经合入 upstream main。

安装包来自联合源码提交 `9ba178acaa7d07c9e6179ee412b318cd22342c4b`，包名仍为 `@furongjun1999/dsh-memory@0.8.1`，是本地构建包，未发布新 npm 版本。之后同步的测试和文档修正没有改变本次安装包中的生产文件。[source_identity.json](source_identity.json) 记录构建提交、两个独立 PR 的提交、DSH checkout 提交、实际运行入口及安装包/源码指纹。DSH 的 checkout HEAD 仅提供背景，运行入口哈希用于识别本次构建，不声称宿主构建已可独立复现。重建包因文档或构建产物不同可以有不同的归档哈希，应核对安装后生产文件指纹。

## 复跑

准备已构建的 DSH 0.2.0-rc.1 源码 checkout，其 CLI 入口为 `apps/cli/lib/bin.js`；准备 Node 22.19+ 和 Python 3.12。以下命令在本联合验收分支根目录执行。路径占位符需替换为实际路径；测试工作目录和端口由复核者选择。

```text
npm ci --ignore-scripts --no-audit --no-fund
node node_modules/typescript/bin/tsc -p tsconfig.json
npm pack --ignore-scripts --pack-destination <测试目录>
node docs/eval/dsh_runtime_20261012/run.mjs --cli <DSH源码根>/apps/cli/lib/bin.js --package <测试目录>/furongjun1999-dsh-memory-0.8.1.tgz --python <Python可执行文件> --workspace <测试目录> --output <新报告路径> --port 13088
```

实际 Python/MCP 测试路径使用标准库，不依赖 LLM 或向量模型。首次 DSH 插件安装可能需要从 npm 下载宿主依赖；超时/安装错误会失败，不能计成跳过。已验证的宿主版本和平台见上，其他版本/平台尚未核验。

`run.mjs` 每次创建新目录，清除继承的 `DSH_*` / `MDCG_*` 环境变量和 `DEEPSEEK_API_KEY`，强制使用隔离存储与默认确认闸；不会写入日常 DSH profile。两阶段结束后停止自己启动的宿主，保留合成数据及私有日志供排查。成功时退出 0，并输出：

```text
functional: 25 checks, 19 real DSH tool calls
restart: 15 checks, 10 real DSH tool calls
PASS; report=...
```

若断言失败、宿主提前退出或超时，则退出非 0；报告中的 `ok` 必须为 `true`，并且 `restart_uses_new_python_process` 为 `true`。没有自动忽略失败或 SKIP 分支。运行时刻见 `started_at` / `finished_at`；固定日期和记录名标识这份验收夹具。

联合分支另补跑了两项功能的运行守卫：`python -X utf8 -m md_cg.test_exact_text_cache`（12 tests）与 `python -X utf8 -m md_cg.test_excerpt_budget`（6 tests），均通过。各 PR 的冻结基线性能/预算对照及定点变异见上一层评测文档；这些读数与 DSH 的功能验收分开计算。
