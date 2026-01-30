# AI News Daily 实现方案

## 概述

定时获取 4 个平台的 AI 资讯，汇总并翻译成中文，推送给用户。

## 数据源

| 平台 | 类型 | 获取方式 | 筛选逻辑 |
|------|------|----------|----------|
| Hacker News | 新闻聚合 | RSS | 关键词过滤：AI, ML, LLM, OpenAI, GPT, Anthropic |
| ArXiv | 学术论文 | API | 分类：cs.AI, cs.LG，按时间排序 |
| Twitter/X | 社交媒体 | RSS | 订阅 AI 研究者/公司账号 |
| 稀土掘金 | 中文社区 | RSS | AI 标签下的文章 |

## 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      定时触发器                              │
│                  （每天早上 9:00）                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     News Fetcher                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ HN RSS   │ │ ArXiv API│ │ Twitter  │ │ 稀土掘金 │       │
│  └──────────┘ └──────────┘ │  RSS     │ │  RSS     │       │
│                            └──────────┘ └──────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Processor                            │
│  • 解析 XML/JSON                                             │
│  • 去重（标题相似度判断）                                     │
│  • 关键词过滤                                                │
│  • 时间过滤（近 24 小时）                                    │
│  • 重要性排序                                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   LLM Processor                             │
│  • 翻译标题/摘要为中文                                       │
│  • 生成简洁摘要（2-3 句话）                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Output                                  │
│  格式：Markdown / 飞书消息 / 微信                            │
└─────────────────────────────────────────────────────────────┘
```

## 各平台实现细节

### 1. Hacker News

```python
# 配置
RSS_URL = "https://news.ycombinator.com/rss"

# 关键词列表
HN_KEYWORDS = [
    "AI", "ML", "machine learning", "LLM", "large language model",
    "OpenAI", "GPT", "Anthropic", "Claude", "DeepMind",
    "neural network", "transformer", "generative AI"
]

# 获取逻辑
def fetch_hn_news():
    response = requests.get(RSS_URL)
    items = parse_xml(response.text)
    filtered = [item for item in items
                if any(kw.lower() in item.title.lower() for kw in HN_KEYWORDS)]
    return filtered[:10]
```

### 2. ArXiv

```python
# 配置
API_URL = "http://export.arxiv.org/api/query"

# 查询参数
QUERY_PARAMS = {
    "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.NE",
    "start": 0,
    "max_results": 20,
    "sortBy": "submittedDate",
    "sortOrder": "descending"
}

# 获取逻辑
def fetch_arxiv_papers():
    response = requests.get(API_URL, params=QUERY_PARAMS)
    feed = parse_atom(response.text)
    papers = []
    for entry in feed.entries:
        papers.append({
            "title": entry.title,
            "summary": entry.summary,
            "authors": [a.name for a in entry.authors],
            "pdf_url": entry.id.replace("abs", "pdf") + ".pdf",
            "published": entry.published
        })
    return papers
```

### 3. Twitter/X

```python
# 方案：使用 RSSHub 或 Nitter
RSSHUB_URL = "https://rsshub.app/twitter/following"

# 关注的 AI 账号列表
TWITTER_ACCOUNTS = [
    "@OpenAI",
    "@anthropic",
    "@ylecun",
    "@JeffDean",
    "@AndrewYNg",
    "@ylecun",
    "@hardmaru"
]

# 获取逻辑
def fetch_twitter_news():
    # 方式1：RSSHub 订阅列表
    url = f"{RSSHUB_URL}?limit=20"
    response = requests.get(url)
    items = parse_rss(response.text)
    return items
```

### 4. 稀土掘金

```python
# 配置
RSS_URL = "https://juejin.cn/rss/posts/6814622904592242719"  # AI 标签

# 获取逻辑
def fetch_juejin_news():
    response = requests.get(RSS_URL)
    items = parse_xml(response.text)
    return items[:10]
```

## 数据处理

### 去重策略

```python
from difflib import SequenceMatcher

def is_duplicate(title1, title2, threshold=0.8):
    """判断两个标题是否重复"""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() > threshold

def deduplicate(news_list):
    """去重"""
    unique_news = []
    for news in news_list:
        is_dup = False
        for existing in unique_news:
            if is_duplicate(news["title"], existing["title"]):
                # 保留内容更丰富的那条
                if len(news.get("summary", "")) > len(existing.get("summary", "")):
                    unique_news.remove(existing)
                    unique_news.append(news)
                is_dup = True
                break
        if not is_dup:
            unique_news.append(news)
    return unique_news
```

### 重要性排序

```python
def calculate_importance(news):
    """计算新闻重要性分数"""
    score = 0

    # 标题包含重要关键词
    important_keywords = ["release", "announce", "new", "GPT-4", "Claude 3", "GPT-5"]
    if any(kw in news["title"] for kw in important_keywords):
        score += 5

    # 来源权重
    source_weights = {
        "OpenAI": 10,
        "Anthropic": 10,
        "Google DeepMind": 8,
        "Meta AI": 6,
        "ArXiv": 4,
        "Hacker News": 3
    }
    score += source_weights.get(news.get("source", ""), 1)

    return score
```

## 输出格式

```markdown
# 📰 今日 AI 要闻

> 汇总时间：2024-01-30 09:00

## 1. [OpenAI 发布 GPT-4.5](https://...)
   **摘要**：OpenAI 正式推出 GPT-4.5，在推理能力和成本效率上有显著提升...
   **来源**：OpenAI Blog
   **标签**：产品发布

## 2. [Meta 发布 Llama 3](https://...)
   **摘要**：Meta 宣布开源 Llama 3 模型，性能接近 GPT-4...
   **来源**：Twitter @MetaAI
   **标签**：开源模型

---

💡 共 5 条新闻 | 来源：HN(2) + ArXiv(1) + Twitter(1) + 稀土掘金(1)
```

## 定时任务配置

### Cron 表达式

```bash
# 每天早上 9:00 运行
0 9 * * * /usr/bin/python3 /path/to/ai_news_daily.py
```

### GitHub Actions（可选）

```yaml
name: Daily AI News
on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:

jobs:
  fetch-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run AI News Fetcher
        run: python3 ai_news_daily.py
```

## 待办

- [ ] 实现 HN RSS 解析模块
- [ ] 实现 ArXiv API 解析模块
- [ ] 实现 Twitter RSS 解析模块
- [ ] 实现稀土掘金 RSS 解析模块
- [ ] 实现数据去重和排序逻辑
- [ ] 集成 LLM 翻译和摘要生成
- [ ] 配置定时任务
- [ ] 对接飞书/微信推送

## 参考资料

- [Hacker News RSS](https://news.ycombinator.com/rss)
- [ArXiv API](http://export.arxiv.org/api_help)
- [RSSHub](https://docs.rsshub.app/)
- [稀土掘金 RSS](https://juejin.cn/rss)
