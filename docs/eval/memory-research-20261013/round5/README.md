# dsh-memory 第五轮证据包

这是阶段性实验与探索。首先阅读 `第五轮_完整实验报告.md`，其次看逐案例报告和反馈故障说明。有效主结果只来自 `comparison-v4-feedback`，原始受损版本不混入主分数。

完整 ZIP 内：

- `round5-data/`：真实 DSH 原始 JSONL、工具回执、最终代码、行为评分、A 来源图、固定任务和真值、版本与冻结清单、全部分析脚本。
- `frozen-product/`：对应冻结的公开仓库源码，含研究开始前已有的 30 个改动文件；不含 `.git`、运行时或正式记忆。
- `archive-manifest.json`：逐文件 SHA256、导出边界、私钥排除记录。ZIP 本身的 SHA256 在旁边的 `archive-receipt.json`。

没有导出 API 凭据、正式记忆或实验签名私钥。源码与数据原件保留在工作区。隔离 tokenizer 二进制也不打包；官方 JSON、许可证和来源哈希均保留。

在本机已有实验环境中重分析，命令见任务集说明。解压后可用 Python 3.12+ 离线复核行为分数，例如：

```powershell
python -B -X utf8 'E:\r5-evidence\round5-data\offline_reproduce.py' --data 'E:\r5-evidence\round5-data' --out 'E:\r5-offline-replay'
```

默认核对一题的六组两次成绩，加 `--all` 重放 144 次最终实现。输出目录必须是新目录；不覆盖原评分，不需要 API、Memory DB 或原始绝对路径。

模型实验不能保证逐次输出完全重现：provider 默认温度、远端权重和缓存状态未固定。该包提供固定输入、预算、评分、原始输出和来源证据，可复算结果并单独重复新实验，不把新成绩混入旧成绩。

本轮基线是特定实验适配器，不是正式插件完整工具面的最佳基线；部分留出任务曾在缺反馈版本中暴露。相关限制在报告中明确列出。反思继续关闭，不据此自动上线或进入预测式 RSI。
