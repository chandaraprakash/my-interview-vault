import json
import urllib.request
import urllib.error
import ssl
import os
import time

token = "ntn_y19558721956eSjDkpiMOQ3tECUPtxtTmpcQSdQijAj5Fd"
headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
context = ssl._create_unverified_context()

output_dir = "/Users/kcp/.gemini/antigravity-ide/brain/e586f335-e544-4d2f-9f38-ee1b923422b1/scratch/notion_mirror"

duplicates = {
    "Data Structures": ["ca08bbc0-6785-4414-9d4b-510e6b2252aa", "3ea589aa-1e3e-48fb-91f0-31ec0e67713b"],
    "Graphs": ["b38bc2ec-6bab-41cf-aa98-b0d1a6ae9ccb", "88f372d3-9f77-4bb9-9e4f-3a7e30c76a3c"],
    "Recursion": ["aa3143e4-ef11-413a-bbe8-71252b8c8073", "94dd1101-0afa-432c-8f70-3cc379b2d4a7"],
    "Big": ["544411e2-0dfd-422c-9ef0-07f8eae0a560", "887c9369-268b-4600-b7fe-00db1a8b0d3f"],
    "Arrays": ["0b71982d-97f8-4903-87b7-342a47f888dd", "49b6d394-9de6-46ef-93d5-80902f1ea9e1"],
    "Dynamic Programming": ["86adf812-0530-47b1-8bb5-cea1e6deff59", "e8d6f80e-68dc-414b-8645-adaabab7563c", "46b4a779-c96b-4c57-a5c8-5bffa96f156d"]
}

def get_text_from_rich_text(rich_text_list):
    return "".join([part.get("plain_text", "") for part in rich_text_list])

def get_block_markdown(block):
    btype = block.get("type")
    content = block.get(btype, {})
    rich_text = content.get("rich_text", [])
    text = get_text_from_rich_text(rich_text)
    
    if btype == "paragraph":
        return text
    elif btype == "heading_1":
        return f"\n# {text}"
    elif btype == "heading_2":
        return f"\n## {text}"
    elif btype == "heading_3":
        return f"\n### {text}"
    elif btype == "bulleted_list_item":
        return f"* {text}"
    elif btype == "numbered_list_item":
        return f"1. {text}"
    elif btype == "to_do":
        checked = "[x]" if content.get("checked") else "[ ]"
        return f"{checked} {text}"
    elif btype == "code":
        lang = content.get("language", "")
        code_text = get_text_from_rich_text(content.get("rich_text", []))
        return f"```{lang}\n{code_text}\n```"
    elif btype == "quote":
        return f"> {text}"
    elif btype == "callout":
        return f"> [!NOTE]\n> {text}"
    elif btype == "divider":
        return "---"
    elif btype == "child_page":
        title = content.get("title", "Untitled Subpage")
        return f"**[Subpage: {title}]** (ID: {block.get('id')})"
    elif btype == "child_database":
        title = content.get("title", "Untitled Database")
        return f"**[Database: {title}]** (ID: {block.get('id')})"
    return f"[{btype}] {text}" if text else f"[{btype}]"

def fetch_all_children(block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    all_blocks = []
    cursor = None
    while True:
        request_url = url
        if cursor:
            request_url += f"&start_cursor={cursor}"
            
        req = urllib.request.Request(request_url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, context=context) as response:
                res_data = response.read().decode('utf-8')
                parsed = json.loads(res_data)
                all_blocks.extend(parsed.get("results", []))
                if parsed.get("has_more") and parsed.get("next_cursor"):
                    cursor = parsed.get("next_cursor")
                else:
                    break
        except Exception as e:
            print(f"Error fetching children for block {block_id}: {e}")
            break
    return all_blocks

def render_tree(block_id, depth=0):
    lines = []
    children = fetch_all_children(block_id)
    for child in children:
        child_id = child.get("id")
        line = get_block_markdown(child)
        indent = "  " * depth
        if line:
            if line.startswith("\n"):
                lines.append(line)
            else:
                lines.append(f"{indent}{line}")
                
        has_children = child.get("has_children", False)
        btype = child.get("type")
        if has_children and btype not in ["child_page", "child_database"]:
            sub_lines = render_tree(child_id, depth + 1)
            lines.extend(sub_lines)
            
    return lines

for title, ids in duplicates.items():
    for pid in ids:
        filename = f"{title}_{pid[:8]}.md"
        file_path = os.path.join(output_dir, filename)
        print(f"Fetching {title} (ID: {pid}) -> {filename}...")
        
        lines = []
        lines.append(f"# {title} (ID: {pid})\n")
        lines.extend(render_tree(pid))
        
        markdown_content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Saved to {file_path}")
        time.sleep(0.3)

print("All duplicates downloaded successfully!")
