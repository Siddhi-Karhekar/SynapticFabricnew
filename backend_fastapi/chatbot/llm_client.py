# ==========================================
# 🤖 LLM CLIENT (PRODUCTION-GRADE)
# FAST + SAFE + STREAMING + FALLBACK
# ==========================================

import ollama
import time


# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
MODEL_NAME = "phi3:mini"
MAX_RETRIES = 2
TIMEOUT_SECONDS = 3


# ==========================================
# 🧠 SYSTEM PROMPT (OPTIMIZED FOR YOUR USE CASE)
# ==========================================
SYSTEM_PROMPT = (
    "You are a senior industrial AI engineer.\n"
    "Respond in 1 short, precise, technical sentence.\n"
    "Focus on cause, risk, or action.\n"
    "Avoid explanations unless necessary."
)


# ==========================================
# ⚡ SAFE LLM CALL (WITH RETRY + TIMEOUT)
# ==========================================
def generate_llm_response(prompt: str) -> str:

    for attempt in range(MAX_RETRIES):

        try:
            start = time.time()

            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "num_predict": 40,       # ⚡ faster
                    "temperature": 0.1,      # ⚡ stable + precise
                    "top_p": 0.9,
                }
            )

            # ⏱ TIMEOUT CHECK
            if time.time() - start > TIMEOUT_SECONDS:
                raise TimeoutError("LLM response too slow")

            content = response.get("message", {}).get("content", "").strip()

            if content:
                return content

        except Exception as e:
            print(f"LLM ERROR (attempt {attempt+1}):", e)

    # ==========================================
    # 🔴 FALLBACK (NEVER FAIL)
    # ==========================================
    return "Unable to generate AI response, but system data is available."


# ==========================================
# ⚡ STREAMING VERSION (REAL-TIME UX)
# ==========================================
def generate_llm_stream(prompt: str):

    try:
        stream = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            options={
                "num_predict": 40,
                "temperature": 0.1,
                "top_p": 0.9,
            }
        )

        for chunk in stream:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]

    except Exception as e:
        print("STREAM ERROR:", e)
        yield "⚠️ AI stream interrupted."


# ==========================================
# ⚡ LIGHTWEIGHT FAST RESPONSE (OPTIONAL)
# Used when you want ultra-fast LLM fallback
# ==========================================
def generate_fast_llm_response(prompt: str) -> str:

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "num_predict": 25,   # 🔥 ultra fast
                "temperature": 0.0   # deterministic
            }
        )

        return response.get("message", {}).get("content", "").strip()

    except Exception as e:
        print("FAST LLM ERROR:", e)
        return "Quick response unavailable."