# backend/app.py
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
import os
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
CONV_FILE = os.path.join(ROOT, "conversations.json")
ATTACH_DIR = os.path.join(ROOT, "attachments")  # optional folder for attachments

app = Flask(__name__, static_folder=None)
CORS(app, origins=["http://localhost:3000"])

# ---------- Load conversations safely ----------
def load_conversations():

    if not os.path.exists(CONV_FILE):
        print("ERROR: conversations.json not found next to app.py")
        return []

    with open(CONV_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Case 1: export format is { "conversations": [ ... ] }
    if isinstance(data, dict) and "conversations" in data:
        print("Loaded conversations (dict format)")
        return data["conversations"]

    # Case 2: export format is [ {...}, {...}, ... ]
    if isinstance(data, list):
        print("Loaded conversations (list format)")
        return data

    print("ERROR: Unknown conversations.json format")
    return []

conversations = load_conversations()

@app.get("/debug/<cid>")
def debug(cid):
    for c in conversations:
        if c.get("id") == cid:
            mapping = c.get("mapping", {})
            
            # Find first node with a message
            for node_id, node in mapping.items():
                if node.get("message"):  # skip null messages
                    print("\n===== REAL MESSAGE NODE =====\n")
                    print(json.dumps(node, indent=2))
                    return "Check terminal for REAL message node."

            return "No message nodes found"
    return "Conversation not found", 404


def load_json_file(path):
    if not os.path.exists(path):
        return None
    
    # Load your exported conversations.json
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def try_get_messages_from_conv(conv):
    """
    Many export shapes exist. Try a few common keys to find messages.
    Return list of message-like dicts or [].
    """
    candidates = []
    # common keys
    for key in ("messages", "items", "mapping", "messages_list", "chat"):
        if key in conv:
            candidates_val = conv.get(key)
            # mapping sometimes is {id: message}
            if isinstance(candidates_val, dict):
                # Flatten dict values
                for v in candidates_val.values():
                    candidates.append(v)
            elif isinstance(candidates_val, list):
                candidates.extend(candidates_val)
            else:
                # single item
                candidates.append(candidates_val)

    # some exports store the actual message content under "data" or "message"
    if not candidates:
        # if conv itself looks like a message list
        if isinstance(conv, list):
            candidates = conv
    return candidates

def extract_text_from_content(content):
    """
    content can be:
      - a string
      - a list of blocks [{type:'text', 'text': '...'}, ...]
      - a dict with 'text' or 'content'
    Return joined markdown/plain text.
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        # common: {'type':'message', 'text': '...'} or {'content': '...'}
        if "text" in content:
            return content.get("text", "")
        if "content" in content:
            return extract_text_from_content(content.get("content"))
        # sometimes 'parts' or 'items'
        for key in ("parts", "items", "blocks"):
            if key in content:
                return extract_text_from_content(content.get(key))
        # fallback stringify
        return json.dumps(content, ensure_ascii=False)

    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                # common structure: {'type':'text','text':'...'}
                if "text" in part:
                    parts.append(part.get("text",""))
                elif "content" in part:
                    parts.append(extract_text_from_content(part.get("content")))
                else:
                    parts.append(json.dumps(part, ensure_ascii=False))
            else:
                parts.append(str(part))
        return "\n\n".join([p for p in parts if p is not None])
    # fallback
    return str(content)

def normalize_message(msg):
    """
    Produce { role, text, created_at, attachments: [ {name, url} ] }
    """
    role = "user"
    # try role detection
    for k in ("role", "author", "from", "sender"):
        if isinstance(msg, dict) and k in msg:
            val = msg.get(k)
            if isinstance(val, dict):
                role_str = val.get("role") or val.get("name") or ""
            else:
                role_str = str(val)
            role_str = (role_str or "").lower()
            if "assist" in role_str or "bot" in role_str or "gpt" in role_str:
                role = "assistant"
            elif "user" in role_str or "human" in role_str:
                role = "user"
            break

    # text detection
    text = ""
    for k in ("text", "content", "message", "html", "body"):
        if isinstance(msg, dict) and k in msg:
            text = extract_text_from_content(msg.get(k))
            if text:
                break

    # some exports nest content under 'content' -> list -> {'type':'output_text','text':'...'}
    if not text:
        # try common nested shape .get('content',[])[0]['text']
        if isinstance(msg, dict) and "content" in msg:
            text = extract_text_from_content(msg.get("content"))

    # created_at/time
    created_at = None
    for k in ("create_time", "created_at", "timestamp", "time", "date"):
        if isinstance(msg, dict) and k in msg:
            created_at = msg.get(k)
            break
    # attempt to normalize to iso
    if isinstance(created_at, (int, float)):
        try:
            created_at = datetime.utcfromtimestamp(int(created_at)).isoformat() + "Z"
        except Exception:
            created_at = str(created_at)
    elif created_at is None:
        created_at = ""
    else:
        created_at = str(created_at)

    # attachments
    attachments = []
    if isinstance(msg, dict):
        for k in ("attachments", "files", "media"):
            if k in msg and isinstance(msg.get(k), list):
                for a in msg.get(k):
                    if isinstance(a, dict):
                        name = a.get("filename") or a.get("name") or a.get("title") or a.get("id")
                        # if there is a local file path or url
                        url = a.get("url") or a.get("src") or a.get("path")
                        # Provide link to backend attachment proxy if local relative path
                        if url and not url.startswith("http"):
                            # ensure it's relative to attachments folder
                            attachments.append({"name": name, "url": f"/api/attachment/{os.path.basename(url)}"})
                        else:
                            attachments.append({"name": name, "url": url})
                    else:
                        # string entry
                        attachments.append({"name": str(a), "url": str(a)})
                break

    return {
        "role": role,
        "text": text or "",
        "created_at": created_at,
        "attachments": attachments
    }

def parse_conversations():
    """
    Return list of conversations each like:
    { id, title, messages: [ {role, text, created_at, attachments} ] }
    """
    data = load_json_file(CONV_FILE)
    if data is None:
        return []

    convs = []
    # If top-level is dict and has 'conversations'
    if isinstance(data, dict) and "conversations" in data and isinstance(data["conversations"], list):
        raw_convs = data["conversations"]
    elif isinstance(data, list):
        raw_convs = data
    elif isinstance(data, dict):
        # Maybe the file itself is a mapping of id -> conv or contains top-level conversation entries
        # Try to detect any values that are conversation-like (have messages)
        raw_convs = []
        for v in data.values():
            if isinstance(v, dict) and any(k in v for k in ("messages", "items", "mapping")):
                raw_convs.append(v)
        # fallback: if dict seems like a single conversation
        if not raw_convs and any(k in data for k in ("messages", "items", "mapping")):
            raw_convs = [data]
    else:
        raw_convs = []

    # Normalize each conversation
    for idx, conv in enumerate(raw_convs):
        conv_id = conv.get("id") or conv.get("conversation_id") or conv.get("key") or f"conv-{idx}"
        title = conv.get("title") or conv.get("name") or ""
        messages_raw = try_get_messages_from_conv(conv)
        messages = []
        # sometimes mapping contains dict of id->message
        if isinstance(messages_raw, dict):
            messages_list = list(messages_raw.values())
        else:
            messages_list = messages_raw or []

        # If messages list is empty but the conv itself looks like messages, try other heuristics
        if not messages_list:
            # some exports put content at conv['message']
            if "message" in conv:
                messages_list = [conv.get("message")]
        for m in messages_list:
            norm = normalize_message(m if isinstance(m, dict) else {"text": m})
            # ignore messages with no text and no attachments unless they have metadata
            messages.append(norm)

        convs.append({
            "id": conv_id,
            "title": title or (messages[0]["text"][:80] if messages else f"Conversation {idx+1}"),
            "message_count": len(messages),
            "messages": messages
        })
    return convs

# --- Route 1: list all conversations (metadata) ---
# --- List all conversations ---
@app.get("/conversations")
def list_conversations():
    meta = [
        {
            "id": c["id"],
            "title": c.get("title", "Untitled Conversation"),
            "create_time": c.get("create_time"),
            "update_time": c.get("update_time")
        }
        for c in conversations
    ]
    meta.sort(key=lambda x: x["update_time"], reverse=True)
    return jsonify(meta)

def extract_messages(conv):
    messages = []

    mapping = conv.get("mapping", {})

    for node_id, node in mapping.items():
        msg = node.get("message")

        # Skip empty nodes
        if not msg:
            continue

        role = msg.get("author", {}).get("role")

        # Only allow user / assistant
        if role not in ("user", "assistant"):
            continue

        # Skip hidden system/setup messages
        metadata = msg.get("metadata", {})
        if metadata.get("is_visually_hidden_from_conversation"):
            continue

        parts = msg.get("content", {}).get("parts", [])

        # Must contain non-empty text
        if not parts or (len(parts) == 1 and parts[0].strip() == ""):
            continue

        messages.append({
            "id": node_id,
            "role": role,
            "text": "\n".join(parts)
        })

    # Sort by creation order
    messages.sort(key=lambda m: mapping[m["id"]]["message"]["create_time"] or 0)

    return messages


# --- Get messages in a conversation ---
@app.route("/conversation/<cid>")
def get_conversation(cid):
    for c in conversations:
        if c["id"] == cid:
            msgs = extract_messages(c)
            return jsonify(msgs)

    return jsonify({"error": "Conversation not found"}), 404

@app.route("/api/attachment/<path:filename>")
def get_attachment(filename):
    # Serve files from attachments folder if they exist
    safe_name = os.path.basename(filename)
    file_path = os.path.join(ATTACH_DIR, safe_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(ATTACH_DIR, safe_name, as_attachment=True)
    abort(404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
