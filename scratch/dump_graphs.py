import json
import urllib.request
import urllib.error
import ssl

token = "ntn_y19558721956eSjDkpiMOQ3tECUPtxtTmpcQSdQijAj5Fd"
headers = {
    "Authorization": f"Bearer {token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}
context = ssl._create_unverified_context()

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

print("Fetching Graphs subpage...")
lines = render_tree("88f372d3-9f77-4bb9-9e4f-3a7e30c76a3c")
print("\n".join(lines))
