import ast
import json
import operator as op
import os
import re

import numpy as np
import requests
import streamlit as st

# ---------- Settings ----------
CHAT_URL = "http://localhost:11434/api/chat"
EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL = "qwen2.5:3b"            # use "qwen2.5:1.5b" on a very slow laptop
EMBED_MODEL = "nomic-embed-text"
INDEX_FILE = "index.json"

SUBJECTS = {
    "General help": "Help with any learning question.",
    "Math": "Teach math step by step. Show each step and check the answer.",
    "Science": "Explain science with simple everyday examples.",
    "English": "Teach English. Correct mistakes gently and explain why.",
    "Computer skills": "Teach computers and coding to a complete beginner.",
}

LANGUAGES = {
    "English": "Answer in English.",
    "Dari": "Answer in Dari (Persian) using simple words.",
    "Pashto": "Answer in Pashto using simple words.",
}

TASKS = {
    "Chat": "",
    "Summarize": "Summarize the text the learner gives you in 5 simple points.",
    "Explain simply": "Explain the topic simply, like to a 12 year old, with one example.",
    "Quiz me": "Ask 5 questions about the topic, one at a time, and wait for the answer.",
    "Check my answer": "Check the learner's answer. Say what is right, what is wrong, and why.",
}


def build_system_prompt(subject, language, task):
    return (
        "You are a kind, patient teacher for Afghan women and girls. "
        "Explain step by step in simple words, give small examples, "
        "and encourage the learner. If you are not sure, say so honestly. "
        f"{SUBJECTS[subject]} {LANGUAGES[language]} {TASKS[task]}"
    )


# ---------- Exact math (Python calculates, the AI explains) ----------
OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Mod: op.mod, ast.Pow: op.pow,
    ast.USub: op.neg, ast.UAdd: op.pos,
}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e6):
            raise ValueError("too big")
        return OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("not allowed")


def try_calculate(text):
    text = re.sub(r"(?<=\d)\s*[x×]\s*(?=\d)", "*", text)
    text = text.replace("÷", "/").replace("^", "**")
    match = re.search(r"[\d\(][\d\.\s\+\-\*/\(\)%]*[\d\)]", text)
    if not match or not re.search(r"[\+\-\*/%]", match.group()):
        return None
    try:
        result = _eval(ast.parse(match.group().strip(), mode="eval").body)
    except Exception:
        return None
    if isinstance(result, float):
        result = int(result) if result.is_integer() else round(result, 6)
    return result


# ---------- Offline library search (works after you run ingest.py) ----------
@st.cache_resource
def load_index():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def embed(text):
    r = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=120)
    return np.array(r.json()["embedding"])


def search(question, k=3):
    index = load_index()
    if not index:
        return []
    q = embed(question)
    scored = []
    for item in index:
        v = np.array(item["vec"])
        score = float(q @ v / (np.linalg.norm(q) * np.linalg.norm(v)))
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:k]]


# ---------- Page ----------
st.set_page_config(page_title="Offline Learning Assistant", page_icon="📚")
st.title("📚 Offline Learning Assistant")
st.caption("Works without internet. Your questions stay on your computer.")

with st.sidebar:
    subject = st.selectbox("Subject", list(SUBJECTS))
    language = st.selectbox("Language", list(LANGUAGES))
    task = st.selectbox("What do you want to do?", list(TASKS))
    if st.button("New chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("Library: " + ("on" if load_index() else "off (run ingest.py to turn on)"))

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


def stream_reply(messages):
    question = messages[-1]["content"]
    system = build_system_prompt(subject, language, task)

    exact = try_calculate(question)
    if exact is not None:
        system += f"\n\nThe exact answer to the calculation is {exact}. Explain step by step how to get it."

    try:
        pieces = search(question)
    except Exception:
        pieces = []
    if pieces:
        context = "\n\n".join(p["text"] for p in pieces)
        system += ("\n\nUse this lesson material to answer. "
                   "If the answer is not in it, say so.\n\n" + context)

    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}] + messages,
        "stream": True,
    }
    try:
        with requests.post(CHAT_URL, json=payload, stream=True, timeout=600) as r:
            for line in r.iter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("message", {}).get("content", "")
    except requests.exceptions.ConnectionError:
        yield "I cannot reach Ollama. Please open the Ollama app and try again."


if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = st.write_stream(stream_reply(st.session_state.messages))
    st.session_state.messages.append({"role": "assistant", "content": reply})
