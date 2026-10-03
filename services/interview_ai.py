from services.groq_service import client

def evaluate_answer(answer):

    prompt = f"""
You are an interview evaluator.

Candidate Answer:
{answer}

Give:

Score out of 10

One Strength

One Weakness

One Improvement

Return JSON only.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content