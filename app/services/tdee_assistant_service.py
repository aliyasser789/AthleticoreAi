from typing import Optional
import os
from groq import Groq
_groq_api_key = os.environ.get("GROQ_API_KEY")
client: Optional[Groq] = None
if _groq_api_key:
    client = Groq(api_key=_groq_api_key)

def tdee_assistant_reply(user_message: str, previous_messages: Optional[list] = None) -> str:
    if client is None:
        reply_text = (
        "Hi, I'm your TDEE assistant (demo mode, no real AI yet).\n"
        f"You said: {user_message}\n\n"
        "To enable the real Llama AI, set the GROQ_API_KEY environment variable.")
        return reply_text
    system_prompt = (
    "You are Athleticore.AI's TDEE assistant.\n"
    "Your job:\n"
    "- Ask the user about age, sex/gender, height (cm), weight (kg), "
    "training days per week, daily steps, and lifestyle.\n"
    "- Help them estimate their TDEE by multiplying activity factor times BMR and choose a calorie target for cutting, bulking, or maintaining.\n"
    "- Explain in simple, friendly language like a coach.\n"
    "- Keep answers focused on fitness, nutrition, and TDEE only.\n")
    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": user_message})
    try:
         completion = client.chat.completions.create(
         model="llama-3.1-8b-instant",
         messages=messages,
          temperature=0.7,)
         reply_text = completion.choices[0].message.content
         return reply_text
    except Exception as e:
         return (
         "There was an error talking to the Llama API:\n"
         f"{e}\n\n"
         "Please check your internet connection or your GROQ_API_KEY and try again."
         )

