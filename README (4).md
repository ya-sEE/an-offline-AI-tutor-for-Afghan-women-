# Offline Learning Assistant

Hello world, this is Yaser.

I wanted to find a way, in this era of AI, to build an offline GPT from first
principles. So I asked a simple question: what is the main problem for students?
The answer was money. Many students cannot afford internet access.

So I asked: what if we make a GPT that works without internet and without
spending money? That is how I came to build this offline AI tutor for Afghan
women and girls.

## Why even small progress matters
Life is about the rate of growth. If a learner improves by just 1 percent each
day, that is far better than not learning at all, and it adds up over time.

## Why I want to learn more
I want to learn from other people, especially at UWC, so I can improve this
project and one day make it available to learners around the world. New ideas
and technologies may help share it widely in the future, and I want to keep
learning about them.

---

An AI tutor that runs fully offline on an ordinary laptop. No internet, no account, and nothing leaves the computer.

## Why
Many Afghan women and girls have no school access and little or no internet. This project gives them a private study helper that works anywhere after a one-time setup.

## What it does
- Chat tutor for math, science, English and computer skills
- Summarize, explain simply, quiz me, and check my answer
- Exact math: Python calculates the answer and the AI explains the steps
- Offline library: answers from lesson files you add (RAG)
- Languages: English, Dari, Pashto (Dari and Pashto quality is still being tested)

## How it works
Browser (Streamlit) -> app.py -> Ollama (local) -> small language model (qwen2.5:3b)

## Setup
1. Install Ollama from ollama.com
2. `ollama pull qwen2.5:3b` and `ollama pull nomic-embed-text`
3. `pip install -r requirements.txt`
4. Put `.txt` lessons in the `library` folder, then run `python ingest.py`
5. `streamlit run app.py`

## Tested on
Windows laptop, 8 GB RAM, no dedicated graphics card.

## Limits (honest)
- Small models can make mistakes, especially on hard math and facts from memory
- Dari and Pashto answers may be weak
- Answers from the library are more reliable than answers from the model's memory

## Roadmap
- More lessons in the library
- Progress tracking and spaced repetition
- Voice input and output
- Testing with real learners

## Credits
Built with Ollama, Qwen2.5, Streamlit and nomic-embed-text. Add the sources of every lesson you include in the library.
