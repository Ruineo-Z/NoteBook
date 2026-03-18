# TCM Hierarchical Clustering Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个可直接读取中医证候 Excel 数据并输出层次聚类结果、指标表和树状图的 Python 脚本。

**Architecture:** 采用单文件脚本加一个单元测试文件的方式实现。脚本内部拆分为数据读取与清洗、特征筛选、层次聚类评估、结果汇总导出四个模块化函数；测试优先覆盖不依赖 Excel 文件的核心计算逻辑，最后再用真实数据跑通全流程。

**Tech Stack:** Python 3.14、pytest、pandas、numpy、scipy、scikit-learn、matplotlib、openpyxl

---

### Task 1: 建立项目骨架与依赖

**Files:**
- Modify: `/Users/ruinow/Develop/git-repo/NoteBook/.gitignore`
- Create: `/Users/ruinow/Develop/git-repo/NoteBook/requirements-clustering.txt`
- Create: `/Users/ruinow/Develop/git-repo/NoteBook/scripts/tcm_hierarchical_clustering.py`
- Create: `/Users/ruinow/Develop/git-repo/NoteBook/tests/test_tcm_hierarchical_clustering.py`

**Step 1: 写失败测试**

为以下行为各写一个最小测试：
- 低频症状能按 `<5%` 阈值被剔除
- `K` 候选指标中能正确选出最优值
- 聚类剖面表能计算频数、频率和提升度

**Step 2: 运行测试确认失败**

Run: `pytest tests/test_tcm_hierarchical_clustering.py -q`

Expected: 因模块或函数不存在而失败。

**Step 3: 写最小实现**

在脚本中先实现纯函数：
- `normalize_binary_series`
- `filter_low_frequency_features`
- `select_best_k`
- `build_cluster_profiles`

**Step 4: 运行测试确认通过**

Run: `.venv/bin/pytest tests/test_tcm_hierarchical_clustering.py -q`

Expected: 上述单元测试全部通过。

### Task 2: 接入 Excel 读取、聚类计算与导出

**Files:**
- Modify: `/Users/ruinow/Develop/git-repo/NoteBook/scripts/tcm_hierarchical_clustering.py`
- Modify: `/Users/ruinow/Develop/git-repo/NoteBook/tests/test_tcm_hierarchical_clustering.py`

**Step 1: 写失败测试**

补一个端到端最小测试，使用临时 DataFrame 或临时 Excel 文件验证：
- 能生成患者聚类标签
- 能返回 `K=4~7` 的指标表
- 能构造输出目录下的结果文件路径

**Step 2: 运行测试确认失败**

Run: `.venv/bin/pytest tests/test_tcm_hierarchical_clustering.py -q`

Expected: 因分析管线尚未实现而失败。

**Step 3: 写最小实现**

补充：
- Excel 读取与基础列排除
- 缺失值填补
- Ward 层次聚类与 `fcluster` 切类
- 评估指标计算
- Excel 与树状图输出
- CLI 参数解析

**Step 4: 运行测试确认通过**

Run: `.venv/bin/pytest tests/test_tcm_hierarchical_clustering.py -q`

Expected: 测试全部通过。

### Task 3: 真实数据验证

**Files:**
- Verify only: `/Users/ruinow/Documents/中医数据_结合西医特征调优版（ai层次聚类法）.xlsx`

**Step 1: 安装依赖**

Run: `python3 -m venv .venv && .venv/bin/pip install -r requirements-clustering.txt`

Expected: 依赖安装完成。

**Step 2: 运行真实分析**

Run: `.venv/bin/python scripts/tcm_hierarchical_clustering.py --input "/Users/ruinow/Documents/中医数据_结合西医特征调优版（ai层次聚类法）.xlsx"`

Expected: 生成输出目录、`cluster_summary.xlsx` 与 `dendrogram.png`。

**Step 3: 核查关键结果**

检查：
- 最优 `K` 是否成功从 `4~7` 中选出
- 每类患者数量之和是否等于样本总数
- 结果文件是否可打开

**Step 4: 汇报结果**

向用户说明脚本路径、运行命令、输出路径与本次真实数据的关键结果。
