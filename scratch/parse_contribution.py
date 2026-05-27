import os
import re
import sys

def sanitize_filename(name):
    # Keep only alphanumeric and hyphen/underscore, lowercase
    name = name.lower().strip()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_]+", "-", name)
    return name

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

def parse_issue(issue_body_path):
    if not os.path.exists(issue_body_path):
        print(f"Error: Issue body file not found at {issue_body_path}")
        sys.exit(1)

    with open(issue_body_path, "r", encoding="utf-8") as f:
        body = f.read()

    # Extract fields using regex matching the headers in submit-contribution.yml
    title_match = re.search(r"### Document Title\s*\n\s*(.*?)(?=\n###|\Z)", body, re.DOTALL)
    category_match = re.search(r"### Category\s*\n\s*(.*?)(?=\n###|\Z)", body, re.DOTALL)
    content_match = re.search(r"### Content\s*\n\s*(.*?)(?=\n###|\Z)", body, re.DOTALL)
    submitter_match = re.search(r"### Submitter Name / GitHub Username\s*\n\s*(.*?)(?=\n###|\Z)", body, re.DOTALL)

    if not title_match or not category_match or not content_match:
        print("Error: Could not parse all required fields from issue body.")
        print(f"  Title parsed: {bool(title_match)}")
        print(f"  Category parsed: {bool(category_match)}")
        print(f"  Content parsed: {bool(content_match)}")
        sys.exit(1)

    title = title_match.group(1).strip()
    category = category_match.group(1).strip().lower()
    content = content_match.group(1).strip()
    submitter = submitter_match.group(1).strip() if submitter_match else "anonymous"

    # Validate category options matching the dropdown options
    valid_categories = ["data-structures", "system-design", "behavioral", "ai-ml", "tpm", "interview-and-beyond"]
    if category not in valid_categories:
        print(f"Error: Invalid category '{category}'. Must be one of {valid_categories}")
        sys.exit(1)

    # Sanitize title to form a valid file name
    filename = sanitize_filename(title) + ".mdx"
    sanitized_content = sanitize_mdx(content)

    # Add Docusaurus MDX frontmatter headers
    frontmatter = f"""---
title: {title}
description: Suggestion submitted by {submitter}
---

# {title}

{sanitized_content}
"""

    submissions_dir = f"submissions/{category}"
    os.makedirs(submissions_dir, exist_ok=True)
    
    dest_file_path = os.path.join(submissions_dir, filename)
    with open(dest_file_path, "w", encoding="utf-8") as out:
        out.write(frontmatter)

    # Print variable values so they can be captured by the GitHub Action
    print(f"FILE_PATH={dest_file_path}")
    print(f"FILE_NAME={filename}")
    print(f"CATEGORY={category}")
    print(f"TITLE={title}")
    print(f"SUBMITTER={submitter}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 parse_contribution.py <issue_body_file_path>")
        sys.exit(1)
    parse_issue(sys.argv[1])
