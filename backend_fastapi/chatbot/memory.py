# ==========================================
# 🧠 CHAT MEMORY (PER SESSION)
# ==========================================

from collections import deque

MAX_HISTORY = 5

CHAT_MEMORY = deque(maxlen=MAX_HISTORY)


def add_to_memory(question, response):
    CHAT_MEMORY.append({
        "q": question,
        "a": response
    })


def get_memory_context():
    context = ""

    for item in CHAT_MEMORY:
        context += f"Q: {item['q']}\nA: {item['a']}\n"

    return context.strip()