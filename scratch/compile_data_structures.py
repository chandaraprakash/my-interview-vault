import os
import re
import shutil

# Source paths
scratch_dir = "/Users/kcp/Documents/work/my-interview-vault/scratch"
ds_src = os.path.join(scratch_dir, "Data Structures")
ib_src = os.path.join(scratch_dir, "Interview And Beyond")

docs_root = "/Users/kcp/Documents/work/my-interview-vault/docs"
ds_dest = os.path.join(docs_root, "data-structures")
aiml_dest = os.path.join(docs_root, "ai-ml")
tpm_dest = os.path.join(docs_root, "tpm")
ib_dest = os.path.join(docs_root, "interview-and-beyond")
old_dsa_dest = os.path.join(docs_root, "data-structures-and-algorithms")

static_img_dest = "/Users/kcp/Documents/work/my-interview-vault/static/img/data-structures/big"

# Ensure target directories exist
os.makedirs(ds_dest, exist_ok=True)
os.makedirs(aiml_dest, exist_ok=True)
os.makedirs(tpm_dest, exist_ok=True)
os.makedirs(ib_dest, exist_ok=True)
os.makedirs(static_img_dest, exist_ok=True)

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

# ==========================================
# 1. COPY SCREENSHOT ASSETS
# ==========================================
print("Copying BigO screenshot assets...")
big_img_src = os.path.join(ds_src, "BigO/Big")
if os.path.exists(big_img_src):
    for filename in os.listdir(big_img_src):
        src_path = os.path.join(big_img_src, filename)
        if os.path.isfile(src_path):
            shutil.copy(src_path, static_img_dest)
            print(f"  Copied screenshot: {filename}")

# ==========================================
# 2. DELETE OLD DIRECTORY
# ==========================================
if os.path.exists(old_dsa_dest):
    print("Deleting old data-structures-and-algorithms directory...")
    shutil.rmtree(old_dsa_dest)

# ==========================================
# 3. COMPILE DATA STRUCTURES CATEGORY
# ==========================================
print("Compiling data-structures files...")

# Write _category_.json
ds_category = """{
  "label": "Data Structures",
  "position": 2,
  "link": {
    "type": "generated-index",
    "slug": "/category/data-structures",
    "description": "Basic and advanced data structures, traversal algorithms, and complexity cheat sheets."
  }
}
"""
write_file(os.path.join(ds_dest, "_category_.json"), ds_category)

# Write index.mdx
ds_index = """---
title: Data Structures Overview
sidebar_position: 1
---

# Data Structures & Traversal Algorithms

Welcome to the Data Structures section. Here you will find detailed references, cheat sheets, and practice lists covering essential computer science primitives.

## Topics Covered
1. **Concepts**: High-level checklist of topics to cover for technical coding interviews.
2. **Big-O Algorithm Complexity Cheat Sheet**: Complete reference tables and charts detailing operations and sorting bounds.
3. **Bit Manipulation**: Detailed explanation of basic operators, bitwise hacks, and LeetCode problems.
4. **Graphs**: Traversal templates (DFS, BFS), Union Find, topological sort, and practice exercises.
5. **Blind Top 75**: Curated list of high-signal questions from the Blind Top 75.
6. **Curated Resources & Playlists**: Curated links, books, and Kevin Naughton's Facebook prep videos.
"""
write_file(os.path.join(ds_dest, "index.mdx"), ds_index)

# Parse Concepts
concepts_raw = read_file(os.path.join(ds_src, "Concepts/Concepts.md"))
concepts_md = f"""---
title: Concepts Checklist
sidebar_position: 2
---

# Concepts to Cover for Technical Interviews

This checklist maps out the data structures, algorithms, and common coding patterns to cover during preparation.

{sanitize_mdx(concepts_raw.replace("### Concepts to cover for Interview", "").strip())}
"""
write_file(os.path.join(ds_dest, "concepts.mdx"), concepts_md)

# Parse Big-O Cheat Sheet
bigo_raw = read_file(os.path.join(ds_src, "BigO/Big-O Algorithm Complexity Cheat .md"))
bigo_clean = bigo_raw.strip()

# Inject images right under headers
bigo_clean = bigo_clean.replace(
    "## Big-O Complexity Chart\n\n`Horrible``Bad``Fair``Good``Excellent`",
    "## Big-O Complexity Chart\n\n`Horrible` `Bad` `Fair` `Good` `Excellent`\n\n![Big-O Complexity Chart](/img/data-structures/big/Screen_Shot_2020-10-12_at_11.39.33_PM.png)"
)
bigo_clean = bigo_clean.replace(
    "## Common Data Structure Operations",
    "## Common Data Structure Operations\n\n![Common Data Structure Operations](/img/data-structures/big/Screen_Shot_2020-10-12_at_11.40.40_PM.png)"
)
bigo_clean = bigo_clean.replace(
    "## Array Sorting Algorithms",
    "## Array Sorting Algorithms\n\n![Array Sorting Algorithms](/img/data-structures/big/Screen_Shot_2020-10-12_at_11.41.26_PM.png)"
)

bigo_md = f"""---
title: Big-O Cheat Sheet
sidebar_position: 3
---

# Big-O Algorithm Complexity Cheat Sheet

Comparing the time and space complexity of common data structure operations and sorting algorithms is a core requirement of technical preparation.

{sanitize_mdx(bigo_clean)}
"""
write_file(os.path.join(ds_dest, "big-o-cheat-sheet.mdx"), bigo_md)

# Parse Bit Manipulation
bit_raw = read_file(os.path.join(ds_src, "Bit Manipulation/BIT MANIPULATION.md"))
bit_md = f"""---
title: Bit Manipulation
sidebar_position: 4
---

# Bit Manipulation Guide

Bit manipulation is an essential technique to optimize time and space complexity in competitive coding and technical interviews.

{sanitize_mdx(bit_raw)}
"""
write_file(os.path.join(ds_dest, "bit-manipulation.mdx"), bit_md)

# Parse Graphs
graphs_raw = read_file(os.path.join(ds_src, "Graphs/Graph For Beginners.md"))
graphs_md = f"""---
title: Graphs
sidebar_position: 5
---

# Graphs for Beginners

Topic-wise graph problems, patterns, standard templates, and sample solutions to build graph traversal intuition.

{sanitize_mdx(graphs_raw.replace("Title: Graph For Beginners [Problems | Pattern | Sample Solutions] - Discuss - LeetCode", "").strip())}
"""
write_file(os.path.join(ds_dest, "graphs.mdx"), graphs_md)

# Parse Blind Top 75
blind_raw = read_file(os.path.join(ds_src, "Interview Problems/Blind Top 75.md"))
blind_md = f"""---
title: Blind Top 75
sidebar_position: 6
---

# Blind Curated List of Top LeetCode Questions

A curated checklist of high-signal LeetCode questions categorized by topic.

{sanitize_mdx(blind_raw)}
"""
write_file(os.path.join(ds_dest, "blind-top-75.mdx"), blind_md)

# Parse Resources: Links & Browser Bookmarks
links_raw = read_file(os.path.join(ds_src, "Resources/Important and Useful links.md"))
bookmarks_raw = read_file("/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/scratch/relevant_bookmarks.md")
bookmarks_clean = bookmarks_raw.replace("# Filtered Technical and Interview Bookmarks\n\n", "").strip()

links_md = f"""---
title: Important Links
sidebar_position: 7
---

# Important & Useful Links

A collection of bookmarks, online tutorials, interactive visualization sites, and algorithmic reference guides.

{sanitize_mdx(links_raw)}

---

# Bookmarked Technical Resources

Curated bookmarks exported from browser folders.

{sanitize_mdx(bookmarks_clean)}
"""
write_file(os.path.join(ds_dest, "resources-links.mdx"), links_md)

# Parse Resources: YouTube & Books (with Kevin Naughton's Facebook Playlist merged)
yt_raw = read_file(os.path.join(ds_src, "Resources/YouTube-Books-And-More.md"))
kevin_raw = read_file(os.path.join(ds_src, "Resources/Kevin Naughton's Facebook Playlist.md"))

yt_md = f"""---
title: YouTube & Books
sidebar_position: 8
---

# YouTube, Books, and More

Recommended textbook reading and YouTube channels for data structure concepts.

{sanitize_mdx(yt_raw)}

---

## Kevin Naughton's Facebook Playlist

Detailed walkthrough solutions and playlists for Facebook/Meta interview questions.

{sanitize_mdx(kevin_raw)}
"""
write_file(os.path.join(ds_dest, "youtube-books.mdx"), yt_md)

# Clean up old Kevin Naughton Playlist file if it exists
kevin_file_path = os.path.join(ds_dest, "kevin-naughton-playlist.mdx")
if os.path.exists(kevin_file_path):
    os.remove(kevin_file_path)
    print("  Removed legacy page: kevin-naughton-playlist.mdx")


# ==========================================
# 4. COMPILE AI/ML CATEGORY (ai-ml)
# ==========================================
print("Compiling AI/ML placeholder...")
aiml_category = """{
  "label": "AI/ML",
  "position": 5,
  "link": {
    "type": "generated-index",
    "slug": "/category/ai-ml",
    "description": "Artificial Intelligence and Machine Learning interview preparation."
  }
}
"""
write_file(os.path.join(aiml_dest, "_category_.json"), aiml_category)

aiml_index = """---
title: AI/ML Overview
sidebar_position: 1
---

# AI/ML Interview Preparation

*This section is blank. Add your AI/ML concepts, machine learning system designs, and algorithms here.*
"""
write_file(os.path.join(aiml_dest, "index.mdx"), aiml_index)


# ==========================================
# 5. COMPILE TPM CATEGORY (tpm)
# ==========================================
print("Compiling TPM placeholder...")
tpm_category = """{
  "label": "TPM",
  "position": 6,
  "link": {
    "type": "generated-index",
    "slug": "/category/tpm",
    "description": "Technical Program Management interview resources and execution guides."
  }
}
"""
write_file(os.path.join(tpm_dest, "_category_.json"), tpm_category)

tpm_index = """---
title: TPM Overview
sidebar_position: 1
---

# TPM Interview Preparation

*This section is blank. Add your Technical Program Management, system execution, roadmap, and leadership guides here.*
"""
write_file(os.path.join(tpm_dest, "index.mdx"), tpm_index)


# ==========================================
# 6. COMPILE INTERVIEW AND BEYOND CATEGORY (interview-and-beyond)
# ==========================================
print("Compiling Interview and Beyond files...")

ib_category = """{
  "label": "Interview and Beyond",
  "position": 7,
  "link": {
    "type": "generated-index",
    "slug": "/category/interview-and-beyond",
    "description": "Company-specific interview guides, mock platforms, and career progression notes."
  }
}
"""
write_file(os.path.join(ib_dest, "_category_.json"), ib_category)

ib_index = """---
title: Overview
sidebar_position: 1
---

# Interview & Beyond

Welcome to the Interview and Beyond section. This category gathers company-specific preparation guides, mock interview platforms, negotiation tips, and career guides.

## Sections
1. **Interview Guides**: Targeted prep tips and documentation links for Google, Meta, Amazon, Apple, Microsoft, OpenAI, and more.
2. **Mock Interviews**: Links to peer-to-peer and expert mock interview practice platforms.
"""
write_file(os.path.join(ib_dest, "index.mdx"), ib_index)

# Parse Guides
guides_raw = read_file(os.path.join(ib_src, "Interview Guides.md"))
guides_md = f"""---
title: Company Interview Guides
sidebar_position: 2
---

# Company Interview Guides

Company-specific preparation tips and resources for top tech companies.

{sanitize_mdx(guides_raw)}
"""
write_file(os.path.join(ib_dest, "interview-guides.mdx"), guides_md)

# Parse Mocks
mocks_raw = read_file(os.path.join(ib_src, "Mock Interviews.md"))
mocks_md = f"""---
title: Mock Interview Platforms
sidebar_position: 3
---

# Mock Interview Platforms

Recommended platforms for peer-to-peer and expert mock interview practice.

{sanitize_mdx(mocks_raw)}
"""
write_file(os.path.join(ib_dest, "mock-interviews.mdx"), mocks_md)

print("Successfully compiled all categories!")
