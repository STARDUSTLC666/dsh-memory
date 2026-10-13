# Windows 解压与完整性复核

归档包含 DSH 原始会话目录，部分路径较长。第一次在过长目标目录解压触发 Windows MAX_PATH；原始 ZIP 未改写，已在新的 E 盘短目录使用长路径支持完整解压并通过全部离线复核。

可使用随交付提供的辅助工具，目标必须为尚不存在的新目录：

```powershell
python -B -X utf8 extract_and_replay.py memory-delivery-round8-complete-20261013.zip E:\r8-evidence-check
```

工具核对每个文件的 SHA256/长度和 ZIP CRC，拒绝越界路径与覆盖旧目录，然后重新评分 144 次主实验及 3 次开发实验。不会发起模型 API 调用。附带评估依赖面向 Windows CPython 3.12；其他环境请按固定依赖配置。

归档 SHA256：81ea623316eeeab987f5c8cfec4a655ed4f6cf3eb72aa3d42bc54419b4cf8b13。
共 11,921 项清单条目、178 份原始 DSH 尝试日志；178 不等于 178 个独立模型实验。原始解压失败堆栈另附，未删失败记录。
