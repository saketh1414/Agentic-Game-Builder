"""
Handles writing generated game files to disk.
"""
import os
import re


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_game")


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def write_game_files(files: dict) -> str:
    """
    Write a dict of {filename: content} to the generated_game/ directory.
    Returns the output directory path.
    """
    ensure_output_dir()
    written = []
    for filename, content in files.items():
        # Safety: only allow expected file names
        safe_name = os.path.basename(filename)
        if safe_name not in ["index.html", "style.css", "game.js"]:
            continue
        filepath = os.path.join(OUTPUT_DIR, safe_name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(filepath)
    return OUTPUT_DIR


def extract_files_from_response(response_text: str) -> dict:
    """
    Parse agent output to extract code blocks for each file.
    Looks for patterns like:
        ### index.html
        ```html
        ...
        ```
    Also handles plain ``` blocks labeled with filename.
    """
    files = {}

    # Pattern 1: Marked with filename header then code block
    patterns = [
        # ### filename\n```lang\ncontent\n```
        r"###?\s*(index\.html|style\.css|game\.js)\s*\n```[a-zA-Z]*\n(.*?)```",
        # --- filename ---\n```lang\ncontent\n```
        r"---\s*(index\.html|style\.css|game\.js)\s*---\s*\n```[a-zA-Z]*\n(.*?)```",
        # **filename**\n```lang\ncontent\n```
        r"\*\*\s*(index\.html|style\.css|game\.js)\s*\*\*\s*\n```[a-zA-Z]*\n(.*?)```",
        # FILE: filename\n```lang\ncontent\n```
        r"FILE:\s*(index\.html|style\.css|game\.js)\s*\n```[a-zA-Z]*\n(.*?)```",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
        for filename, content in matches:
            files[filename.strip()] = content.strip()

    # Pattern 2: Direct ```html / ```css / ```javascript blocks (infer filename)
    if "index.html" not in files:
        html_match = re.search(r"```html\n(.*?)```", response_text, re.DOTALL)
        if html_match:
            files["index.html"] = html_match.group(1).strip()

    if "style.css" not in files:
        css_match = re.search(r"```css\n(.*?)```", response_text, re.DOTALL)
        if css_match:
            files["style.css"] = css_match.group(1).strip()

    if "game.js" not in files:
        js_match = re.search(r"```javascript\n(.*?)```", response_text, re.DOTALL)
        if js_match:
            files["game.js"] = js_match.group(1).strip()
        elif "game.js" not in files:
            js_match2 = re.search(r"```js\n(.*?)```", response_text, re.DOTALL)
            if js_match2:
                files["game.js"] = js_match2.group(1).strip()

    return files
