import os
import re

# Source Paths
sd_dir = "/Users/kcp/Documents/work/my-interview-vault/scratch/System Design"
notion_mirror_dir = '/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/scratch/notion_mirror'
docs_dir = "/Users/kcp/Documents/work/my-interview-vault/docs/system-design"
scenarios_dir = os.path.join(docs_dir, "scenarios")

# Ensure target directories exist
os.makedirs(docs_dir, exist_ok=True)
os.makedirs(scenarios_dir, exist_ok=True)

def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def sanitize_mdx(text):
    if not text:
        return ""
    # 1. Escape < not followed by details, summary, b, br, code, p, pre, span, div, img, h1, h2, h3, h4, h5, h6, a
    text = re.sub(r"<(?!/?(?:details|summary|b|br|code|p|pre|span|div|img|h1|h2|h3|h4|h5|h6|a)(?:\s|>|/))", "&lt;", text, flags=re.IGNORECASE)
    
    # 2. Escape { and } in non-code blocks
    parts = text.split("```")
    for i in range(len(parts)):
        if i % 2 == 0:  # Non-code block
            parts[i] = parts[i].replace("{", "\\{").replace("}", "\\}")
    return "```".join(parts)

def clean_names(text):
    if not text:
        return ""
    # Remove lines containing Instructor, Session by, Session with, etc.
    text = re.sub(r"(?im)^.*(?:Instructor|Session\s*by|Session\s*with).*?$", "", text)
    text = re.sub(r"Shelby Cohen's\s*", "", text, flags=re.IGNORECASE)
    return text

def extract_url(text):
    text = text.strip()
    # Extract url from markdown link like [some text](http://...)
    m = re.search(r"\[.*?\]\((https?://\S+?)\)", text)
    if m:
        return m.group(1)
    # Strip brackets, parentheses, and bullet characters
    text = text.strip("[]()↳► ")
    return text

# ==========================================
# 1. COMPILE FUNDAMENTALS PAGE (fundamentals.mdx)
# ==========================================
print("Compiling fundamentals.mdx...")
fundamentals_content = """---
title: System Design Fundamentals
sidebar_position: 1
---

# System Design Fundamentals

System design interviews reward structured thinking and deep tradeoff analysis more than memorized architecture diagrams.

## The Interview Workflow

1. **Clarify Requirements**: Functional requirements, user volume, read/write ratios, geographic distribution.
2. **Estimate Scale (Back-of-the-Envelope)**: Compute storage, memory bandwidth, network throughput, and QPS.
3. **Define APIs and Data Models**: Specify endpoints (REST/GraphQL parameters) and schema definitions.
4. **Sketch High-Level Architecture**: Draw stateless gateways, load balancers, application tiers, caches, and storage clusters.
5. **Identify Bottlenecks & Scale**: Evaluate what fails if traffic increases 10x, and introduce sharding, replication, or queues.
6. **Discuss Tradeoffs (CAP vs PACELC)**: Decide where to favor consistency over availability or latency.

## Core System Architectures

- **Load Balancing**: L4 vs L7 load balancers, DNS routing, and reverse proxies.
- **Caching**: Cache-aside, write-through, write-behind, eviction policies (LRU, LFU), and cache stampedes.
- **Queues and Async Processing**: Decoupling write-heavy paths with brokers (Kafka, RabbitMQ) and handling failures with DLQs.
- **Databases**: Indexing (B-Trees, LSM-Trees), SQL vs NoSQL, sharding architectures, replication slots, and CDC.

---

## Stanford LLM & Transformers Playlist

For advanced machine learning system designs and modern NLP model pipelines:
- [Stanford CME295 Transformers & LLMs - Lecture 1 (Transformer)](https://www.youtube.com/watch?v=Ub3GoFaUcds)
- [Stanford CME295 Transformers & LLMs - Lecture 2 (Transformer-Based Models & Tricks)](https://www.youtube.com/watch?v=yT84Y5zCnaA)

---

## Core Bookmarked Resources & Reads

### System Design Handbooks
- [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
- [binhnguyennus/awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)

### Tradeoff Analyses (Consistency vs Latency)
- [Balancing Strong and Eventual Consistency with Datastore (Google Cloud)](https://cloud.google.com/datastore/docs/articles/balancing-strong-and-eventual-consistency-with-google-cloud-datastore)
- [Why you should pick strong consistency, whenever possible (Google Cloud)](https://cloud.google.com/blog/products/databases/why-you-should-pick-strong-consistency-whenever-possible)
- [10 Common Software Architectural Patterns in a nutshell](https://towardsdatascience.com/10-common-software-architectural-patterns-in-a-nutshell-a0b47a1e9013)
- [Centralized vs Decentralized vs Distributed](https://medium.com/@bbc4468/centralized-vs-decentralized-vs-distributed-41d92d463868)
"""
write_file(os.path.join(docs_dir, "fundamentals.mdx"), fundamentals_content)

# ==========================================
# 2. COMPILE CONCEPTS PAGE (concepts.mdx) (Merged with PACELC & DNS Lookup)
# ==========================================
print("Compiling concepts.mdx...")
concepts_1_raw = read_file(os.path.join(sd_dir, "Concepts And System Designs-1.md"))
concepts_2_raw = read_file(os.path.join(sd_dir, "Concepts And System Designs-2.md"))
git_repos_raw = read_file(os.path.join(sd_dir, "Git Repos.md"))

# Parse Git Repos
git_repos = []
git_lines = [l.strip() for l in git_repos_raw.split('\n') if l.strip()]
i = 0
while i < len(git_lines):
    if git_lines[i].startswith('#'):
        i += 1
        continue
    match = re.match(r"^\d+\s+(.*)", git_lines[i])
    if match:
        name = match.group(1).strip()
        link = extract_url(git_lines[i+1]) if i+1 < len(git_lines) else ""
        git_repos.append((name, link))
        i += 2
    else:
        i += 1

git_repos_md = "\n".join([f"- [{name}]({link})" for name, link in git_repos])

# Parse curated concepts list (34 links) from Concepts-2
curated_concepts = []
list_match = re.search(r"Here’s the curated list that helped me and will help you too 👇\n\n(.*?)(?=\n\nLearn about|$)", concepts_2_raw, re.DOTALL)
if list_match:
    list_text = list_match.group(1).strip()
    for line in list_text.split('\n'):
        line = line.strip()
        m = re.match(r"^\d+\.\s*(.*?):\s*(https?://\S+)(.*)", line)
        if m:
            concept_name = m.group(1).strip()
            concept_link = extract_url(m.group(2).strip())
            extra = m.group(3).strip()
            curated_concepts.append((concept_name, concept_link, extra))

concepts_table = "| Concept / Tech Topic | Curated Resource Link | Notes |\n| :--- | :--- | :--- |\n"
for name, link, extra in curated_concepts:
    notes = extra if extra else "-"
    concepts_table += f"| **{sanitize_mdx(name)}** | [Learning Resource Link]({link}) | {sanitize_mdx(notes)} |\n"

# Parse 20 Brain foods/articles from Concepts-1
brain_foods = []
bf_blocks = re.split(r"\n\d+\.\s*", concepts_1_raw)
for block in bf_blocks:
    block = block.strip()
    if '►' in block:
        parts = block.split('►')
        title = parts[0].strip().rstrip(':').replace('\n', ' ').strip()
        link = extract_url(parts[1])
        brain_foods.append((title, link))

brain_foods_md = "\n".join([f"- [{title}]({link})" for title, link in brain_foods])

# Parse 14 Topic Illustrations from Concepts-1 (with ↳)
illustrations = []
concepts_1_lines = concepts_1_raw.split('\n')
for idx, line in enumerate(concepts_1_lines):
    line = line.strip()
    if '↳' in line:
        title_line = concepts_1_lines[idx-1].strip() if idx > 0 else ""
        title = re.sub(r"^\d+\s+", "", title_line).strip()
        link = extract_url(line)
        if title and not title.startswith('#') and not title.startswith('↳'):
            illustrations.append((title, link))

illustrations_table = "| Deep-Dive Illustration Topic | Illustrated Resource Link |\n| :--- | :--- |\n"
for title, link in illustrations:
    illustrations_table += f"| **{sanitize_mdx(title)}** | [Visual/Article Link]({link}) |\n"

# Parse and clean DNS Lookup
dns_raw = read_file(os.path.join(sd_dir, "Concepts-DNS Lookup/DNS Lookup 2a7074943dc3809d809bf9f04ea5fc50.md"))
dns_clean = dns_raw.replace("# DNS Lookup", "").strip()
dns_clean = re.sub(r"!\[image\.png\].*$", "![DNS Lookup Diagram](/img/system-design/dns-lookup.png)", dns_clean, flags=re.MULTILINE)

# Parse and clean CAP vs PACELC
cap_raw = read_file(os.path.join(notion_mirror_dir, 'CAP - PACELC.md'))
if not cap_raw:
    # Read from existing doc if old Notion mirror file is not available
    cap_raw = read_file(os.path.join(docs_dir, 'cap-pacelc.mdx'))
# Clean headers
cap_clean = cap_raw.replace("# CAP - PACELC", "").strip()
# Remove frontmatter if present
cap_clean = re.sub(r"^---.*?---", "", cap_clean, flags=re.DOTALL).strip()

concepts_content = f"""---
title: Concepts & Building Blocks
sidebar_position: 2
---

# Concepts & Building Blocks

Understanding core architectural primitives is essential to navigating trade-offs under scale, network partitions, and latency requirements.

---

## CAP vs PACELC Theorem

In a distributed data store, trade-offs between consistency, availability, and latency are fundamental and dictated by network physical constraints.

{cap_clean}

---

## DNS Lookup Walkthrough

Resolving a human-readable domain name into an IP address involves traversing several routing and caching layers across the global internet.

{dns_clean}

---

## Curated Systems Design Resource Directory

| Concept / Tech Topic | Curated Resource Link | Notes |
| :--- | :--- | :--- |
{concepts_table}

---

## Deep-Dive Illustrations

| Topic / Illustrated Pattern | Reference Link |
| :--- | :--- |
{illustrations_table}

---

## Brain Foods & Articles for Engineers

High-signal articles and case studies on scaling engineering careers and modern infrastructure:
{brain_foods_md}

---

## Useful GitHub Repositories & Guides

{git_repos_md}

---

## Distributed Systems Glossary Topics

- **Covering Indexes**: Database indexes that contain all fields requested in a query, allowing the database engine to return results purely from the index structure without fetching from the heap table.
- **Transactional Outbox**: An architectural pattern that ensures reliable message publishing in microservices by writing events to an `outbox` table in the same database transaction as the business operation, and tailing the database WAL/log to push events to message brokers asynchronously.
"""
write_file(os.path.join(docs_dir, "concepts.mdx"), concepts_content)

# Delete standalone pages merged into concepts
for path in [
    os.path.join(docs_dir, "cap-pacelc.mdx"),
    os.path.join(docs_dir, "dns-lookup.mdx")
]:
    if os.path.exists(path):
        os.remove(path)
        print(f"Removed merged file: {path}")

# ==========================================
# 3. COMPILE Distributed Systems Whitepapers (whitepapers.mdx)
# ==========================================
print("Compiling whitepapers.mdx...")
whitepapers_raw = read_file(os.path.join(sd_dir, "White Papers.md"))
papers = []
wp_lines = [l.strip() for l in whitepapers_raw.split('\n') if l.strip()]
i = 0
while i < len(wp_lines):
    if wp_lines[i].startswith('#'):
        i += 1
        continue
    match = re.match(r"^\d+\s+(.*)", wp_lines[i])
    if match:
        name = match.group(1).strip()
        desc = wp_lines[i+1].strip() if i+1 < len(wp_lines) else ""
        link_url = extract_url(wp_lines[i+2]) if i+2 < len(wp_lines) else ""
        papers.append((name, desc, link_url))
        i += 3
    else:
        i += 1

papers_table = "| System / Concept | Focus / Description | Original Whitepaper |\n| :--- | :--- | :--- |\n"
for name, desc, url in papers:
    papers_table += f"| **{sanitize_mdx(name)}** | {sanitize_mdx(desc)} | [Read Research Paper]({url}) |\n"

whitepapers_content = f"""---
title: Distributed Systems Whitepapers
sidebar_position: 3
---

# Distributed Systems Whitepapers

Reading original architectural research papers is the best way to build deep intuition around consistency models, storage layout, and cluster orchestration.

{papers_table}
"""
write_file(os.path.join(docs_dir, "whitepapers.mdx"), whitepapers_content)

# ==========================================
# 4. COMPILE Corporate Case Studies (case-studies.mdx)
# ==========================================
print("Compiling case-studies.mdx...")
case_studies_raw = read_file(os.path.join(sd_dir, "Case Studies.md"))
cases = []
cs_lines = [l.strip() for l in case_studies_raw.split('\n') if l.strip()]
i = 0
while i < len(cs_lines):
    if cs_lines[i].startswith('#'):
        i += 1
        continue
    match = re.match(r"^\d+\s+(.*)", cs_lines[i])
    if match:
        name = match.group(1).strip()
        link_url = extract_url(cs_lines[i+1]) if i+1 < len(cs_lines) else ""
        cases.append((name, link_url))
        i += 2
    else:
        i += 1

cases_table = "| Corporate Case Study | Source Link |\n| :--- | :--- |\n"
for name, url in cases:
    cases_table += f"| **{sanitize_mdx(name)}** | [Case Study Link]({url}) |\n"

case_studies_content = f"""---
title: Corporate Case Studies
sidebar_position: 4
---

# Corporate Case Studies

Real-world architectures showing how major software platforms balance scale, availability, latency, and operational complexity.

{cases_table}
"""
write_file(os.path.join(docs_dir, "case-studies.mdx"), case_studies_content)

# ==========================================
# 5. COMPILE Interview Questions (interview-questions.mdx)
# ==========================================
print("Compiling interview-questions.mdx...")
questions_raw = read_file(os.path.join(sd_dir, "25 System Design Interview Questions.md"))

q_content = questions_raw.replace("# 25 System Design Interview Questions", "").strip()
q_content = re.sub(r"^𝗧(\d)\s*·\s*(.*)", r"### Tier \1: \2", q_content, flags=re.MULTILINE)
q_content = re.sub(r"^(Foundational|The must-know|Where 2026|Senior\+|For staff)(.*)", r"* \1\2", q_content, flags=re.MULTILINE)

interview_questions_content = f"""---
title: Interview Questions
sidebar_position: 5
---

# Top 25 System Design Interview Questions

This curated list represents high-frequency architectural challenges asked during technical interviews, categorized by difficulty level.

{q_content}
"""
write_file(os.path.join(docs_dir, "interview-questions.mdx"), interview_questions_content)

# ==========================================
# 6. PARSE AND CATEGORIZE REAL-WORLD SCENARIOS
# ==========================================
print("Parsing scenarios from logs...")
eng_files = ["Eng-1.md", "Eng-2.md", "Eng-3.md", "Eng-4.md"]
date_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{4})(.*)")
all_scenarios = []

for file_name in eng_files:
    path = os.path.join(sd_dir, file_name)
    if not os.path.exists(path):
        continue
    content = read_file(path)
    lines = content.split('\n')
    
    current_date_block = None
    date_blocks = []
    
    for line in lines:
        line_stripped = line.strip()
        match = date_pattern.match(line_stripped)
        if match:
            if current_date_block:
                date_blocks.append(current_date_block)
            current_date_block = {
                "date": match.group(1),
                "title_raw": match.group(2).replace('-', '').strip(),
                "lines": []
            }
        else:
            if current_date_block is not None:
                current_date_block["lines"].append(line)
    if current_date_block:
        date_blocks.append(current_date_block)
        
    for db in date_blocks:
        db_content = "\n".join(db["lines"]).strip()
        raw_sub_blocks = db_content.split('\n---\n')
        if len(raw_sub_blocks) <= 1:
            raw_sub_blocks = db_content.split('---')
            
        sub_blocks = []
        for rsb in raw_sub_blocks:
            rsb = rsb.strip()
            if rsb:
                sub_blocks.append(rsb)
                
        # Merge logic for broken Notion splits
        merged_sub_blocks = []
        skip_next = False
        for idx in range(len(sub_blocks)):
            if skip_next:
                skip_next = False
                continue
            curr = sub_blocks[idx]
            if idx + 1 < len(sub_blocks):
                next_block = sub_blocks[idx + 1]
                is_curr_question_only = curr.strip().endswith("Ans:") or curr.strip().endswith("Ans") or "?" in curr[-50:]
                is_next_expl_only = (
                    next_block.startswith("Why A is best") or 
                    next_block.startswith("Why B is less suitable") or 
                    next_block.startswith("Why the others") or
                    next_block.startswith("Option A is") or
                    next_block.startswith("Option B is") or
                    next_block.startswith("Option C is") or
                    next_block.startswith("Option D is") or
                    next_block.startswith("Why ")
                )
                if is_curr_question_only and is_next_expl_only:
                    curr = curr + "\n\n" + next_block
                    skip_next = True
            merged_sub_blocks.append(curr)
            
        for s_idx, sb in enumerate(merged_sub_blocks):
            sb_lines = [l.strip() for l in sb.split('\n') if l.strip()]
            if not sb_lines:
                continue
            
            # Extract first line for title
            sub_title = ""
            if s_idx == 0 and db["title_raw"]:
                sub_title = db["title_raw"]
            else:
                first_line = sb_lines[0]
                if len(first_line) < 100:
                    sub_title = first_line
                else:
                    sub_title = first_line[:50] + "..."
            
            sub_title = re.sub(r"^#+\s*", "", sub_title).strip()
            sub_title = re.sub(r"^\d+/\d+/\d+\s*-\s*", "", sub_title)
            sub_title = sub_title.strip()
            
            q_match = re.search(r"^(.*?)(?=\nAns:|\nA:|\nCorrect answer:|\nWhy A is best:)", sb, re.DOTALL | re.IGNORECASE)
            question_text = q_match.group(1).strip() if q_match else sb[:300]
            
            ans_match = re.search(r"\n(Ans:|A:|Correct answer:)\s*(.*?)(?=\nDetailed Explanation:|\nExplanation|\nWhy A is best|\nWhy the other|$)", sb, re.DOTALL | re.IGNORECASE)
            expl_match = re.search(r"\n(Detailed Explanation:|Explanation|Why A is best:.*?|Reasoning:.*?|DETAILED EXPLANATION:.*?)\s*(.*?)$", sb, re.DOTALL | re.IGNORECASE)
            
            answer = ans_match.group(2).strip() if ans_match else ""
            explanation = expl_match.group(0).strip() if expl_match else ""
            
            # If no detailed explanation match, check if we had any trailing discussion text
            if not explanation:
                remaining_text = sb.replace(question_text, "").replace(answer, "").strip()
                # Clean up "Ans:" prefix or dates
                remaining_text = re.sub(r"^(Ans:|A:|Correct answer:)", "", remaining_text).strip()
                if len(remaining_text) > 20:
                    explanation = remaining_text
            
            # Skip empty/dash-only scenarios
            if len(sub_title) < 5 or sub_title == "---":
                continue
                
            all_scenarios.append({
                "date": db["date"],
                "title": clean_names(sanitize_mdx(sub_title)),
                "question": clean_names(sanitize_mdx(question_text)),
                "answer": clean_names(sanitize_mdx(answer)),
                "explanation": clean_names(sanitize_mdx(explanation))
            })

# Categorization Helper
def get_category(sc):
    text = (sc["title"] + " " + sc["question"]).lower()
    
    # 1. Methodology & Testing (checked first for precision)
    if any(k in text for k in ['test', 'pyramid', 'mock', 'strangle', 'legacy', 'migration', 'null', 'refactor', 'monolith', 'microservice', 'systems design']):
        return "methodology-testing"
        
    # 2. Transactions & Concurrency
    if any(k in text for k in ['lock', 'mutex', 'cas', 'concurrency', 'saga', '2pc', 'idempotency', 'idempotent', 'double-charge', 'double charge', 'outbox', 'deadlock', 'isolation', 'pessimistic', 'optimistic']):
        return "transactions-concurrency"
        
    # 3. APIs & Messaging
    if any(k in text for k in ['api', 'rest', 'graphql', 'grpc', 'trpc', 'websocket', 'rate limit', 'rate-limiter', 'queue', 'kafka', 'message', 'stream', 'backpressure', 'webhook', 'pub-sub', 'pub/sub']):
        return "apis-messaging"
        
    # 4. Database & Storage
    if any(k in text for k in ['database normalization', 'database sharding', 'postgres', 'mysql', 'sql', 'nosql', 'time-series', 'storage', 'partitioning', 'sharding', 'shard', 'cdc', 'debezium', 'wal', 'index', 'cqrs', 'query', 'aggregations', 'materialized', 'normalization', 'denormalization']):
        return "database-storage"
        
    return "operations-scale"

# Grouping
scenarios_by_category = {
    "database-storage": [],
    "apis-messaging": [],
    "transactions-concurrency": [],
    "operations-scale": [],
    "methodology-testing": []
}

for sc in all_scenarios:
    cat = get_category(sc)
    scenarios_by_category[cat].append(sc)

print(f"Total valid scenarios parsed: {len(all_scenarios)}")

# Helper to write scenarios MDX file
def write_scenarios_mdx(cat_key, cat_title, position, description):
    items = scenarios_by_category[cat_key]
    
    md_content = f"""---
title: {cat_title}
sidebar_position: {position}
---

# {cat_title} Playbook

{description}

---
"""
    for idx, sc in enumerate(items):
        ans_text = sc['answer'].strip()
        expl_text = sc['explanation'].strip()
        
        # Clean placeholders if there is no explanation
        if ans_text == "See detailed explanation below." and not expl_text:
            ans_text = ""
            
        detail_content = ""
        if ans_text:
            detail_content += f"### Recommended Solution:\n**{ans_text}**\n\n"
        if expl_text:
            detail_content += f"### Detailed Analysis & Trade-offs:\n{expl_text}\n"
            
        # Omit details block entirely if empty, otherwise present it
        details_panel = ""
        if detail_content.strip():
            details_panel = f"""
<details>
<summary><b>Click to expand recommended architecture & tradeoffs</b></summary>

{detail_content}
</details>
"""
        # Date is removed from headers as requested
        md_content += f"""
## Scenario {idx+1}: {sc['title']}

**Dilemma Statement:**
> {sc['question']}
{details_panel}
---
"""
    write_file(os.path.join(scenarios_dir, f"{cat_key}.mdx"), md_content)

# Write scenario categories
write_scenarios_mdx(
    "database-storage",
    "Database & Storage",
    1,
    "Structured design decisions around logical normalization, sharding keys, indexing, CDC pipelines, and time-series architectures."
)
write_scenarios_mdx(
    "apis-messaging",
    "APIs, Protocols & Messaging",
    2,
    "Scenarios evaluating HTTP REST vs GraphQL, real-time WebSockets, distributed rate limiting, and message brokers vs event streams."
)
write_scenarios_mdx(
    "transactions-concurrency",
    "Transactions & Concurrency",
    3,
    "Real-world dilemmas involving multi-service Sagas, distributed locks, optimistic/pessimistic concurrency, and idempotency guarantees."
)
write_scenarios_mdx(
    "operations-scale",
    "Operations & Scaling",
    4,
    "Case studies on global load balancing, multi-region failover, caching topologies, CDN cache invalidations, and leader elections."
)
write_scenarios_mdx(
    "methodology-testing",
    "Methodology & Testing",
    5,
    "Best practices for monolith-to-microservice refactorings, zero-downtime database cutovers, testing pyramids, and mock strategies."
)

# Write scenarios _category_.json
scenarios_category = """{
  "label": "Real-World Scenarios Playbook",
  "position": 6,
  "link": {
    "type": "generated-index",
    "description": "70+ scenario-based Q&A logs evaluating distributed design decisions under latency, availability, and consistency constraints."
  }
}
"""
write_file(os.path.join(scenarios_dir, "_category_.json"), scenarios_category)

print("Successfully compiled all System Design pages!")
