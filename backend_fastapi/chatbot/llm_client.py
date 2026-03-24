import ollama


def generate_llm_response(prompt: str):

    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are concise. Max 2 sentences. Be precise."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "num_predict": 60,   # 🔥 LIMIT TOKENS (HUGE SPEED BOOST)
                "temperature": 0.2
            }
        )

        return response["message"]["content"].strip()

    except Exception as e:
        return f"LLM error: {str(e)}"