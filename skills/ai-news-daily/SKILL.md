---
name: ai-news-daily
description: Fetch and summarize daily AI news from HN, ArXiv, Twitter, and Juejin. This skill should be used when users ask for "AI news", "今日AI资讯", "AI updates", "AI动态" or similar requests.
---

# AI News Daily Skill

Fetch and summarize AI news from 4 sources: Hacker News, ArXiv, Twitter/X, and Juejin.

## When to Use

Use this skill when user asks for:
- "AI news today" / "今日AI资讯" / "AI动态"
- "有什么AI新闻" / "AI圈有什么新消息"
- "Get AI updates" / "汇总AI新闻"
- Any request for AI news, LLM updates, machine learning research

## Workflow

### Step 1: Fetch Data from 4 Sources (Parallel)

#### Source 1: Hacker News (RSS)

```python
import requests

RSS_URL = "https://news.ycombinator.com/rss"
HN_KEYWORDS = [
    "AI", "ML", "machine learning", "LLM", "large language model",
    "OpenAI", "GPT", "Anthropic", "Claude", "DeepMind",
    "neural network", "transformer", "generative AI",
    "人工智能", "大模型", "GPT"
]

def fetch_hn_news():
    response = requests.get(RSS_URL, timeout=10)
    # Parse XML, extract items with <item> elements
    items = parse_xml_items(response.text)
    
    # Filter by keywords
    filtered = []
    for item in items:
        title = item.get("title", "")
        if any(kw.lower() in title.lower() for kw in HN_KEYWORDS):
            filtered.append({
                "title": title,
                "url": item.get("link", ""),
                "summary": item.get("description", "")[:200],
                "source": "Hacker News",
                "published": item.get("pubDate", "")
            })
    
    return filtered[:10]  # Top 10
```

#### Source 2: ArXiv (API)

```python
API_URL = "http://export.arxiv.org/api/query"

def fetch_arxiv_papers():
    params = {
        "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL OR cat:cs.NE",
        "start": 0,
        "max_results": 15,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    response = requests.get(API_URL, params=params, timeout=10)
    # Parse Atom response
    entries = parse_atom_entries(response.text)
    
    papers = []
    for entry in entries:
        papers.append({
            "title": entry.get("title", "").replace("\n", " "),
            "summary": entry.get("summary", "")[:300],
            "url": entry.get("id", ""),
            "pdf_url": entry.get("id", "").replace("abs", "pdf") + ".pdf",
            "source": "ArXiv",
            "authors": [a.get("name", "") for a in entry.get("authors", [])],
            "published": entry.get("published", "")
        })
    
    return papers
```

#### Source 3: Twitter/X (RSS via RSSHub)

```python
# RSSHub public instance or self-hosted
RSSHUB_URL = "https://rsshub.app/twitter/following"

# AI accounts to follow
AI_ACCOUNTS = [
    "OpenAI", "anthropic", "ylecun", "JeffDean", 
    "AndrewYNg", "hardmaru", " StabilityAI"
]

def fetch_twitter_news():
    url = f"{RSSHUB_URL}?limit=20"
    response = requests.get(url, timeout=10)
    items = parse_rss_items(response.text)
    
    tweets = []
    for item in items:
        tweets.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "summary": item.get("description", "")[:200],
            "source": "Twitter",
            "published": item.get("pubDate", "")
        })
    
    return tweets[:10]
```

#### Source 4: 稀土掘金 (RSS)

```python
RSS_URL = "https://juejin.cn/rss/posts/6814622904592242719"  # AI tag

def fetch_juejin_news():
    response = requests.get(RSS_URL, timeout=10)
    items = parse_xml_items(response.text)
    
    articles = []
    for item in items:
        articles.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "summary": item.get("description", "")[:200],
            "source": "稀土掘金",
            "published": item.get("pubDate", "")
        })
    
    return articles[:10]
```

### Step 2: Process and Deduplicate

```python
from difflib import SequenceMatcher
from datetime import datetime, timedelta

def is_duplicate(title1, title2, threshold=0.85):
    """Check if two titles are duplicates"""
    return SequenceMatcher(None, title1.lower(), title2.lower()).ratio() > threshold

def filter_recent(news_list, hours=24):
    """Keep only news from past N hours"""
    cutoff = datetime.now() - timedelta(hours=hours)
    filtered = []
    for news in news_list:
        try:
            published = parse_date(news.get("published", ""))
            if published and published > cutoff:
                filtered.append(news)
        except:
            # If can't parse date, include anyway
            filtered.append(news)
    return filtered

def deduplicate(news_list):
    """Remove duplicate news"""
    unique = []
    for news in news_list:
        is_dup = False
        for existing in unique:
            if is_duplicate(news["title"], existing["title"]):
                is_dup = True
                break
        if not is_dup:
            unique.append(news)
    return unique

def prioritize(news_list):
    """Sort by importance"""
    def score(news):
        s = 0
        title = news.get("title", "").lower()
        
        # Recent releases
        if any(kw in title for kw in ["release", "announce", "new", "launch"]):
            s += 3
        
        # Major sources
        if news.get("source") == "Twitter":
            s += 2
        
        return s
    
    return sorted(news_list, key=score, reverse=True)
```

### Step 3: Summarize with LLM

```markdown
Given these AI news items, create Chinese summaries:

Original: [title]
Summary: [2-3 sentence Chinese summary]

Output format:
1. [Original Title]
   摘要：[Chinese summary]
   链接：[URL]
   来源：[Source]
```

### Step 4: Output Format

```
📰 今日 AI 要闻

1. [新闻标题 - 保留原文]
   摘要：2-3句话的中文摘要
   链接：https://...
   来源：Hacker News

2. [新闻标题]
   摘要：...
   链接：...
   来源：ArXiv

...

---
💡 共 [N] 条新闻 | 来源：HN([X]) + ArXiv([Y]) + Twitter([Z]) + 稀土掘金([W])
```

## Data Sources Summary

| Source | URL | Method | What to Fetch |
|--------|-----|--------|---------------|
| Hacker News | https://news.ycombinator.com/rss | RSS | Top AI-related stories |
| ArXiv | http://export.arxiv.org/api/query | API | Latest AI/ML papers |
| Twitter/X | https://rsshub.app/twitter/following | RSS | AI researchers/companies tweets |
| 稀土掘金 | https://juejin.cn/rss/posts/6814622904592242719 | RSS | Chinese AI articles |

## Quick Reference

```python
# All-in-one fetching function
def fetch_all_ai_news():
    """Fetch news from all 4 sources in parallel"""
    import concurrent.futures
    
    sources = [
        ("Hacker News", fetch_hn_news),
        ("ArXiv", fetch_arxiv_papers),
        ("Twitter", fetch_twitter_news),
        ("稀土掘金", fetch_juejin_news)
    ]
    
    all_news = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda s: s[1](), sources)
        for source_name, news in zip([s[0] for s in sources], results):
            for item in news:
                item["source"] = source_name
            all_news.extend(news)
    
    # Process
    all_news = filter_recent(all_news, hours=48)
    all_news = deduplicate(all_news)
    all_news = prioritize(all_news)
    
    return all_news[:20]  # Return top 20
```

## Notes

- Set reasonable timeouts (10s) for each request
- Handle network errors gracefully - if one source fails, continue with others
- Use concurrent.futures for parallel fetching
- Translate summaries to Chinese using LLM
- Keep original English titles, only translate summaries
- Always include source links
