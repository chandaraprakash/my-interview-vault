import os
import re

# Paths
notion_mirror_dir = '/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/scratch/notion_mirror'
bookmarks_file = '/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/scratch/relevant_bookmarks.md'
docs_dir = '/Users/kcp/Documents/work/my-interview-vault/docs'

# Ensure directories exist
os.makedirs(os.path.join(docs_dir, 'coding'), exist_ok=True)
os.makedirs(os.path.join(docs_dir, 'system-design'), exist_ok=True)
os.makedirs(os.path.join(docs_dir, 'coaching'), exist_ok=True)
os.makedirs(os.path.join(docs_dir, 'strategy'), exist_ok=True)

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
        else:
            # Code block - leave it alone
            pass
    return "```".join(parts)

def clean_names(text):
    if not text:
        return ""
    # Remove lines containing Instructor:, Session by:, Session with:, etc.
    text = re.sub(r"(?im)^.*(?:Instructor|Session\s*by|Session\s*with).*?$", "", text)
    # Remove Shelby Cohen's name from headers
    text = re.sub(r"Shelby Cohen's\s*", "", text, flags=re.IGNORECASE)
    return text

# 1. Parse Bookmarks
bookmarks_text = read_file(bookmarks_file)

def get_bookmarks_under_header(subfolder_name):
    pattern = rf"## SubFolder ->.*{subfolder_name}.*?\n(.*?)(?=\n##|$)"
    match = re.search(pattern, bookmarks_text, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1).strip()
        links = re.findall(r"- \[(.*?)\]\((.*?)\)", content)
        return [{"title": sanitize_mdx(t), "url": u} for t, u in links]
    return []

conshash_bookmarks = get_bookmarks_under_header("ConsHash_Backtrack")
tuts_bookmarks = get_bookmarks_under_header("Tuts")

def bookmarks_to_md(bookmarks):
    if not bookmarks:
        return "*No links registered.*"
    return "\n".join([f"- [{b['title']}]({b['url']})" for b in bookmarks])

# 2. Parse monthly logs for Q&As
monthly_files = ['Dec 2025.md', 'Jan 2026.md', 'Feb 2026.md', 'Mar 2026.md']
scenarios = []

for file_name in monthly_files:
    path = os.path.join(notion_mirror_dir, file_name)
    if not os.path.exists(path):
        continue
    content = read_file(path)
    
    blocks = content.split('---')
    for idx, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        
        lines = block.split('\n')
        lines = [l.strip() for l in lines if l.strip()]
        if not lines:
            continue
        
        title = lines[0]
        title = re.sub(r"^#+\s*", "", title)
        
        block_text = "\n".join(lines)
        
        ans_match = re.search(r"\n(Ans:|A:|Correct answer:)\s*(.*?)(?=\nDetailed Explanation:|\nExplanation|\nWhy A is best|\nWhy the other|$)", block_text, re.DOTALL | re.IGNORECASE)
        expl_match = re.search(r"\n(Detailed Explanation:|Explanation|Why A is best:.*?|Reasoning:.*?|DETAILED EXPLANATION:.*?)\s*(.*?)$", block_text, re.DOTALL | re.IGNORECASE)
        q_match = re.search(r"Q:\s*(.*?)(?=\nAns:|\nA:|\nCorrect answer:|$)", block_text, re.DOTALL | re.IGNORECASE)
        
        if q_match:
            question = q_match.group(1).strip()
        else:
            before_ans_match = re.search(r"^.*?(?=\nAns:|\nA:|\nCorrect answer:)", block_text, re.DOTALL | re.IGNORECASE)
            if before_ans_match:
                question_text = before_ans_match.group(0).strip()
                q_lines = question_text.split('\n')
                if len(q_lines) > 1:
                    question = "\n".join(q_lines[1:]).strip()
                else:
                    question = question_text
            else:
                question = block_text
        
        if ans_match:
            answer = ans_match.group(2).strip()
        else:
            answer = "See explanation details below."
            
        if expl_match:
            explanation = expl_match.group(0).strip()
        else:
            explanation = ""
            
        cleaned_title = re.sub(r"^\d+/\d+/\d+\s*-\s*", "", title)
        cleaned_title = cleaned_title.strip()
        
        if len(question) < 20 and not explanation:
            continue
            
        scenarios.append({
            "file": file_name,
            "title": clean_names(sanitize_mdx(cleaned_title)),
            "question": clean_names(sanitize_mdx(question)),
            "answer": clean_names(sanitize_mdx(answer)),
            "explanation": clean_names(sanitize_mdx(explanation))
        })

print(f"Parsed {len(scenarios)} architectural scenarios.")

# ----------------- Write Coding & DSA files -----------------

# 1. platforms-and-topics.mdx (Enriched with Recursion Template)
lc_400_notes = read_file(os.path.join(notion_mirror_dir, 'LC 400.md'))
lc_notes = read_file(os.path.join(notion_mirror_dir, 'Leetcode Notes.md'))
recursion_notes = read_file(os.path.join(notion_mirror_dir, 'Recursion_aa3143e4.md'))

platforms_md = f"""---
title: Platforms and Topics
sidebar_position: 1
---

# Coding Practice: Platforms and Topics

To prepare effectively for coding interviews, focus on understanding fundamental data structures and algorithmic patterns rather than memorizing individual problems.

## Coding Platforms

- **LeetCode**: Excellent for algorithmic problem practice, tagging common interview patterns, and discussion solutions.
- **HackerRank / CodeSignal**: Frequently used by companies for initial technical assessments and online assessments (OAs).
- **InterviewKickstart**: Platform used for structural preparation and test review classes.

---

## Qualitative Study Strategy

{sanitize_mdx(lc_400_notes.replace('# LC 400', '').strip())}

---

## Recursion Implementation Template

Below is the standard backtracking and recursion workspace template for exploring permutations, combinations, and general search spaces:

{sanitize_mdx(recursion_notes.replace('# Recursion (ID: aa3143e4-ef11-413a-bbe8-71252b8c8073)', '').strip())}

---

## LeetCode Strategy & Mindset

{sanitize_mdx(lc_notes.replace('# Leetcode Notes', '').strip())}

---

## Core Algorithmic Checklist (Top 75 Categories)

We organize preparation around the high-signal patterns from the **Blind Curated List of Top 75 LeetCode Questions**:

1. **Arrays**: Two pointers, sliding window, prefix sums.
2. **Binary (Bit Manipulation)**: Bitwise operations, mask, XOR.
3. **Dynamic Programming**: Memoization, tabulation, recurrence relations.
4. **Graph**: BFS, DFS, Topological Sort, Union Find.
5. **Interval**: Merge intervals, meeting rooms.
6. **Linked List**: Fast and slow pointers, reversing, merging.
7. **Matrix**: Grid traversal, rotation, search.
8. **String**: Palindromes, anagrams, substring search.
9. **Tree**: DFS (top-down / bottom-up), BFS, tree construction.
10. **Heap**: Priority queue, K-way merges, top K elements.

---

## Custom Problem Set (ConsHash_Backtrack Window)

The following problem bookmarks, discussion solutions, and submissions are curated for deep-dives into backtracking, graphs, and system-level hash structures:

{bookmarks_to_md(conshash_bookmarks)}
"""
write_file(os.path.join(docs_dir, 'coding', 'platforms-and-topics.mdx'), platforms_md)


# 2. arrays-and-strings.mdx (Enriched)
arrays_problems_notion = read_file(os.path.join(notion_mirror_dir, 'Arrays - Problems.md'))
arrays_notes_notion = read_file(os.path.join(notion_mirror_dir, 'Arrays - Notes.md'))

arrays_md = f"""---
title: Arrays and Strings
sidebar_position: 2
---

# Arrays and Strings

Arrays and strings show up in many first-round interviews because they test indexing, invariants, and careful edge-case handling.

## Core Definitions

### Bitonic Array
{sanitize_mdx(arrays_notes_notion.replace('# Arrays - Notes', '').replace('[breadcrumb]', '').strip())}

## Essential Patterns

- **Two Pointers**: Moving pointers from ends toward center, or slow/fast pointers moving in same direction.
- **Sliding Window**: Maintaining a window of elements to solve substring or subarray queries in linear time.
- **Prefix Sums**: Precomputing sums to perform constant-time range sum queries.
- **Hash Maps**: Using frequency counts or index tracking to trade space for time complexity.
- **In-Place Partitioning**: Rearranging elements in-place to optimize space usage.

---

## Notion Practice & Question Bank

{sanitize_mdx(arrays_problems_notion.replace('# Arrays - Problems', '').replace('[breadcrumb]', '').replace('[table_of_contents]', '').replace('[unsupported]', '').strip())}

---

## Curated External Resources (Bookmarks)

### String Resources & Interactive Practice
{bookmarks_to_md(tuts_bookmarks[:5])}
- [CodingBat Java String-1](http://codingbat.com/java/String-1)
- [Puddle of Riddles!: Strings](http://puddleofriddles.blogspot.com/search/label/Strings)

### Array Algorithms Deep-Dives
- [Arrays | Algorithms TutorialHorizon](http://algorithms.tutorialhorizon.com/category/arrays/)
"""
write_file(os.path.join(docs_dir, 'coding', 'arrays-and-strings.mdx'), arrays_md)


# 3. dynamic-programming.mdx (Enriched with Code Blocks)
dp_live_notion = read_file(os.path.join(notion_mirror_dir, 'DP -Live Session.md'))
dp_recipe_notion = read_file(os.path.join(notion_mirror_dir, 'Dynamic Programming_46b4a779.md'))
dp_profit_notion = read_file(os.path.join(notion_mirror_dir, 'Dynamic Programming_86adf812.md'))

dp_md = f"""---
title: Dynamic Programming
sidebar_position: 3
---

# Dynamic Programming

Dynamic programming is useful when a problem has overlapping subproblems and an optimal choice structure that can be expressed as a recurrence.

## Core Rules of DP
- **Optimal Substructure**: An optimal solution can be constructed from optimal solutions to its subproblems.
- **Overlapping Subproblems**: The recursive solution solves the same subproblems repeatedly.

## Top-Down vs Bottom-Up
- **Tabulation (Bottom-Up)**:
  - *Performance*: Loops typically run faster due to cache locality.
  - *Scalability*: Avoids stack overflow errors since no recursion stack is built.
- **Memoization (Top-Down)**:
  - *Selective Computation*: Only computes solutions to the subproblems that you actually need for your overall problem.

---

## Interview Approach Template

1. **Define the State**: State what each cell or function call represents in plain words before writing code.
2. **Write the Recurrence Relation**: Write the formula or code that describes how to compose a bigger problem from smaller subproblems.
3. **Pick Base Cases**: Define boundaries (like index 0 or negative inputs) to terminate recurrence.
4. **Choose Execution Shape**: Decide between memoization (recursive array/map lookup) or tabulation (iterative loop).
5. **Analyze Complexity**: Compute the exact Time and Space complexity.

---

## Coding Templates & Recipes

### Memoization Recipe
{sanitize_mdx(dp_recipe_notion.replace('# Dynamic Programming (ID: 46b4a779-c96b-4c57-a5c8-5bffa96f156d)', '').replace('[breadcrumb]', '').replace('[video]', '').strip())}

### Maximum Sell Profit (Java)
{sanitize_mdx(dp_profit_notion.replace('# Dynamic Programming (ID: 86adf812-0530-47b1-8bb5-cea1e6deff59)', '').replace('[breadcrumb]', '').replace('[unsupported]', '').strip())}

---

## Practice Problem Sets

### Notion Live Session Reference
{sanitize_mdx(clean_names(dp_live_notion.replace('# DP -Live Session', '').replace('[breadcrumb]', '').strip()))}

### Must-Do DP Bookmarks
- [Dynamic Programming Practice Problems (Clemson)](http://people.cs.clemson.edu/~bcdean/dp_practice/)
- [Minimum jumps to reach the end](https://www.educative.io/courses/grokking-dynamic-programming-patterns-for-coding-interviews/7nAKN0Qz67r)
- [Word Break Problem](https://www.educative.io/courses/coderust-hacking-the-coding-interview/mZypr)
"""
write_file(os.path.join(docs_dir, 'coding', 'dynamic-programming.mdx'), dp_md)


# 4. NEW: graphs.mdx (Graphs templates and problems)
graphs_notes_notion = read_file(os.path.join(notion_mirror_dir, 'Graphs_88f372d3.md'))
graphs_beginners_notion = read_file(os.path.join(notion_mirror_dir, 'Graph For Beginners [Problems _ Pattern _ Sample Solutions].md'))

graphs_md = f"""---
title: Graphs
sidebar_position: 4
---

# Graphs

Graph structures, traversals, and algorithms form a major part of technical coding assessments. Below are standard traversal code templates and a structured path of practice problems.

## Graph Traversal Templates (Java)

{sanitize_mdx(graphs_notes_notion.replace('# Graphs (ID: 88f372d3-9f77-4bb9-9e4f-3a7e30c76a3c)', '').replace('[breadcrumb]', '').strip())}

---

## Practice Path: Graphs for Beginners

{sanitize_mdx(graphs_beginners_notion.replace('# Graph For Beginners [Problems | Pattern | Sample Solutions]', '').strip())}
"""
write_file(os.path.join(docs_dir, 'coding', 'graphs.mdx'), graphs_md)


# ----------------- Write System Design files -----------------

# fundamentals.mdx (Enriched)
fundamentals_md = f"""---
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
write_file(os.path.join(docs_dir, 'system-design', 'fundamentals.mdx'), fundamentals_md)


# cap-pacelc.mdx
cap_notes = read_file(os.path.join(notion_mirror_dir, 'CAP - PACELC.md'))
cap_md = f"""---
title: CAP vs PACELC
sidebar_position: 2
---

# CAP vs PACELC Theorem

In a distributed data store, trade-offs between consistency, availability, and latency are fundamental and dictated by network physical constraints.

## Concept Overview

{sanitize_mdx(cap_notes.replace('# CAP - PACELC', '').strip())}

---

## Deeper Look at PACELC

- **If there is a Partition (P)**:
  - **Availability (A)** vs **Consistency (C)**: The classic CAP trade-off. Does the system return an error/stale data to remain responsive (AP), or block/reject writes to ensure absolute correctness (CP)?
- **Else (E) - Operating Normally**:
  - **Latency (L)** vs **Consistency (C)**: The latency trade-off. Does the database replicate synchronously to all replicas before returning success (maximizing consistency but increasing latency), or return success immediately after writing to one node and replicate asynchronously (low latency but eventual consistency)?
"""
write_file(os.path.join(docs_dir, 'system-design', 'cap-pacelc.mdx'), cap_md)


# dns-lookup.mdx
dns_notes = read_file(os.path.join(notion_mirror_dir, 'DNS Lookup.md'))
dns_md = f"""---
title: DNS Lookup
sidebar_position: 3
---

# DNS Lookup Walkthrough

Understanding how a browser resolves a human-readable domain name to an IP address is a fundamental concept in networking and system design.

{sanitize_mdx(dns_notes.replace('# DNS Lookup', '').replace('[image]', '').strip())}
"""
write_file(os.path.join(docs_dir, 'system-design', 'dns-lookup.mdx'), dns_md)


# whitepapers.mdx
whitepapers_notes = read_file(os.path.join(notion_mirror_dir, 'White Papers.md'))

papers = []
lines = [l.strip() for l in whitepapers_notes.split('\n') if l.strip()]
i = 0
while i < len(lines):
    if lines[i].startswith('#'):
        i += 1
        continue
    match = re.match(r"^\d+\s+(.*)", lines[i])
    if match:
        name = match.group(1).strip()
        desc = lines[i+1].strip() if i+1 < len(lines) else ""
        link = lines[i+2].strip() if i+2 < len(lines) else ""
        papers.append({"name": name, "desc": desc, "link": link})
        i += 3
    else:
        i += 1

table_rows = []
for p in papers:
    table_rows.append(f"| **{sanitize_mdx(p['name'])}** | {sanitize_mdx(p['desc'])} | [Link]({p['link']}) |")

whitepapers_md = f"""---
title: Distributed Systems Whitepapers
sidebar_position: 4
---

# Distributed Systems Whitepapers

Reading original architectural research papers is the best way to build intuition around consistency models, storage layout, and cluster orchestration.

| System / Concept | Focus / Description | Research Link |
| :--- | :--- | :--- |
{"\n".join(table_rows)}
"""
write_file(os.path.join(docs_dir, 'system-design', 'whitepapers.mdx'), whitepapers_md)


# case-studies.mdx
case_studies_notes = read_file(os.path.join(notion_mirror_dir, 'Case Studies.md'))
cases = []
lines = [l.strip() for l in case_studies_notes.split('\n') if l.strip()]
i = 0
while i < len(lines):
    if lines[i].startswith('#'):
        i += 1
        continue
    match = re.match(r"^\d+\s+(.*)", lines[i])
    if match:
        name = match.group(1).strip()
        link_line = lines[i+1].strip() if i+1 < len(lines) else ""
        link = link_line.replace('↳', '').strip()
        cases.append({"name": name, "link": link})
        i += 2
    else:
        i += 1

case_table_rows = []
for c in cases:
    case_table_rows.append(f"| **{sanitize_mdx(c['name'])}** | [Source Link]({c['link']}) |")

scenarios_md = []
for sc in scenarios:
    sc_md = f"""
### {sc['title']}
*Source: {sc['file'].replace('.md', '')}*

**Scenario Question:**
> {sc['question']}

**Recommended Architecture:**
* **{sc['answer']}**

<details>
<summary><b>Detailed Trade-offs & Analysis</b></summary>

{sc['explanation']}

</details>

---
"""
    scenarios_md.append(sc_md)

case_studies_md = f"""---
title: Corporate Case Studies & Scenarios
sidebar_position: 5
---

# Corporate Case Studies & Scenarios

Real-world architectures and structured decision scenarios showing how major platforms balance availability, latency, and consistency.

## Tech Case Studies Reference

| Platform Case Study | Source Link |
| :--- | :--- |
{"\n".join(case_table_rows)}

---

## Real-World Architectural Q&A Scenarios

These scenarios test trade-offs and decision making under high load, network partitions, and strict latency/availability SLOs.

{"\n".join(scenarios_md)}
"""
write_file(os.path.join(docs_dir, 'system-design', 'case-studies.mdx'), case_studies_md)


# ----------------- Write Coaching files -----------------

coaching_category = """{
  "label": "Coaching & Training",
  "position": 5,
  "link": {
    "type": "generated-index",
    "description": "Notes from coaching sessions, live classes, and training reviews."
  }
}
"""
write_file(os.path.join(docs_dir, 'coaching', '_category_.json'), coaching_category)

# Get files
coaching_notes_notion = read_file(os.path.join(notion_mirror_dir, 'Coding Technical Coaching Sessions.md'))
db_design_notion = read_file(os.path.join(notion_mirror_dir, 'Shelby Cohen\'s Database Design Training Session.md'))

coaching_md = f"""---
title: Coaching Notes & Exercises
sidebar_position: 1
---

# Coaching Notes & Exercises

Structured notes, training exercises, and design patterns from technical coaching sessions.

## Technical Coaching Sessions

{clean_names(sanitize_mdx(coaching_notes_notion.replace('# Coding Technical Coaching Sessions', '').replace('[breadcrumb]', '').strip()))}

---

## Database Design Notes

{clean_names(sanitize_mdx(db_design_notion.replace('# Shelby Cohen\'s Database Design Training Session', '').strip()))}

---

## System Design Problems & Exercises

### 1. Proximity Search & Yelp Design
Curated resources and architectural design patterns for location-based search:
- **Geohash Proximity Searches**: Use grid-based partitioning to perform proximity queries. Refer to the [Geohash Proximity Search Reference](https://gis.stackexchange.com/questions/18330/using-geohash-for-proximity-searches).
- **QuadTree Search**: Hierarchical spatial indexing technique to partition 2D space recursively.
- **Geospatial Indexing**: Utilizing specialized spatial databases like PostGIS for indexing latitude/longitude coordinates.
- **Scaling, Sharding & Replication**: Sharding the geospatial database by geohash range or grid index to distribute load.

### 2. Real-Time Billionth Search Counter
Design for real-time notifications when a domain hits a specific request count:
- **Scale**: Handles 70,000 to 100,000 requests/second across geo-distributed regions.
- **Microservice Design**: Single-writer bottleneck with high concurrency.
- **Evaluated Solutions**:
  1. *Map-Reduce*: Not feasible (designed for batch, not real-time).
  2. *Distributed Sharded Counter*: Nodes maintain local counters in-memory and write updates to shards. Read operations query all shards and aggregate.
  3. *Central Aggregator (Geo-Aggregation)*: 99% of requests are processed and aggregated locally in regional datacenters, with only the final 1% of threshold-crossing events forwarded to a central aggregator.
- **Reference**: [Billionth Search Slide Presentation](https://docs.google.com/presentation/d/1r-jnMy7jXiTsQGMHSwHbyF5wA0FKKipkElV_njuaqyM/edit#slide=id.g10c89afe8ad_0_20).

### 3. Driver Tracking & Ride Hailing (Uber Clone)
Architectural considerations for real-time tracking:
- **Vehicle Tracking Service**: Handles continuous location updates from drivers publishing to a pub-sub message queue (e.g., Kafka).
- **Location-Based Dashboard Service**: Renders active drivers on a map in real-time.
- **Trip Management Service**: Coordinates ride requests, matching, and active trips.
- **References & Tools**:
  - [GeoHash Explorer Interactive Tool](https://geohash.softeng.co/)
  - [Consistent Hashing and Rendezvous Hashing Explained](https://www.francofernando.com/blog/distributed%20systems/2021-12-24-distributed-hashing/)
  - [Load Balancing Algorithms and Techniques](https://kemptechnologies.com/load-balancer/load-balancing-algorithms-techniques/)

### 4. Image Sharing (Instagram Clone) & Web Crawler
- **Stateless vs Stateful Load Balancers**: Tradeoffs in routing policies (session affinity vs round-robin/least-connections).
- **Web Crawler User Cases**: Functional requirements, URL frontier, politeness, and indexing.

---

## External Playlists & References

### System Design Playlists
- [System Design Playlist Reference](https://www.youtube.com/playlist?list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX)

### Database Design & Location Algorithms
- [Food delivery algorithms: Designing a location database](https://www.youtube.com/watch?v=OcUKFIjhKu0)

### Tech Interview Preparation
- [Tech Interview Prep Playlist](https://www.youtube.com/watch?v=t5M3ttm9c8Y)
"""
write_file(os.path.join(docs_dir, 'coaching', 'index.mdx'), coaching_md)


# ----------------- Write Strategy files -----------------

strategy_category = """{
  "label": "Preparation Strategy",
  "position": 6,
  "link": {
    "type": "generated-index",
    "description": "General interview advice, behavioral metrics, and engineering mindset."
  }
}
"""
write_file(os.path.join(docs_dir, 'strategy', '_category_.json'), strategy_category)

brain_foods_notion = read_file(os.path.join(notion_mirror_dir, '10 Brain foods to grow as an Engineer.md'))
guides_notion = read_file(os.path.join(notion_mirror_dir, 'Interview Process & Tips.md'))
questions_notion = read_file(os.path.join(notion_mirror_dir, 'My Interview Questions.md'))

strategy_md = f"""---
title: Preparation Strategy & Tips
sidebar_position: 1
---

# Preparation Strategy & Tips

A collection of high-signal reads, developer handbooks, behavioral insights, and step-by-step career growth strategies.

## General Interview Tips & Guides

{clean_names(sanitize_mdx(guides_notion.replace('# Interview Process & Tips', '').strip()))}
- **Google Prep Guide**: [Get that job at Google](http://steve-yegge.blogspot.com/2008/03/get-that-job-at-google.html)
- **Gainlo Mock Interview Blog**: [Gainlo blog reference](http://blog.gainlo.co/)

---

## Behavioral Interview Signal Areas (Bookmarks)

Notes and signals evaluated by behavioral interviewers from the *Behavioral Substack*:
- [What Behavioral Interviewers Write About You](https://thebehavioral.substack.com/p/what-behavioral-interviewers-write)
- [Deeper Dive into Signal Areas for Behavioral Interviews](https://thebehavioral.substack.com/p/deeper-dive-into-the-signal-areas?sort=community)

---

## 10 Brain Foods for Engineering Growth

{clean_names(sanitize_mdx(brain_foods_notion.replace('# 10 Brain foods to grow as an Engineer', '').strip()))}

---

## Git Guides & Handbooks (Bookmarks)

Use these to master Git branch patterns and repository collaborative workflows:
- [Git Immersion Lab 14](http://gitimmersion.com/lab_14.html)
- [Learn Git Branching (Interactive)](https://learngitbranching.js.org/)
- [Git Book (Official)](http://git-scm.com/book/en/v2)
- [First Aid Git](http://ricardofilipe.com/projects/firstaidgit/)

---

## My Interview Question Checklist

{clean_names(sanitize_mdx(questions_notion.replace('# My Interview Questions', '').strip()))}
"""
write_file(os.path.join(docs_dir, 'strategy', 'index.mdx'), strategy_md)

print("Successfully compiled all Docusaurus pages from Notion mirror and bookmarks!")
