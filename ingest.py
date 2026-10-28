import json
import pathlib

import requests

EMBED_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def embed(text):
    r = requests.post(EMBED_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=120)
    return r.json()["embedding"]


def chunk(text, size=800, overlap=100):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


library = pathlib.Path("library")
if not library.exists():
    raise SystemExit("Make a folder called 'library' and put .txt lesson files in it.")

index = []
for f in sorted(library.glob("*.txt")):
    text = f.read_text(encoding="utf-8")
    for c in chunk(text):
        index.append({"source": f.name, "text": c, "vec": embed(c)})
    print("Done:", f.name)

with open("index.json", "w", encoding="utf-8") as out:
    json.dump(index, out)
print(len(index), "pieces saved to index.json")
