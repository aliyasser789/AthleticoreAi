import os
import json
import re
from groq import Groq
from typing import List, Dict, Optional

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)


class ChatGPTClient:
    """Encapsulate Groq client for the TDEE coach chat."""

    def __init__(self, groq_client: Groq) -> None:
        self._client = groq_client

    def get_client(self) -> Groq:
        return self._client

    def set_client(self, groq_client: Groq) -> None:
        self._client = groq_client

    def chat_with_coach(
        self,
        user_name: str,
        age: int,
        gender: str,
        height: int,
        weight: int,
        message: str,
        chat_history: List[Dict[str, str]]
    ) -> tuple[str, Optional[Dict]]:
        """
        Send a message to the AI coach and get response.
        Returns: (reply_text, tdee_result_dict or None)
        """
        # Create system prompt with user stats
        system_prompt = create_system_prompt(user_name, age, gender, height, weight)

        # Build messages for the API
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (convert to API format)
        for msg in chat_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Add current user message
        messages.append({"role": "user", "content": message})

        try:
            # Call Groq API
            response = self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated to current model
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            reply_text = response.choices[0].message.content

            # Try to parse TDEE result from response
            tdee_result = parse_tdee_result(reply_text)

            return reply_text, tdee_result

        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"I'm sorry, I encountered an error. Please try again. Error: {str(e)}", None


def create_system_prompt(user_name: str, age: int, gender: str, height: int, weight: int) -> str:
    """Create system prompt for the AI coach with user stats."""
    return f"""You are an expert AI fitness coach for Athleticore.AI.
- Name: {user_name}
- Age: {age}
- Gender: {gender}
- Height: {height} cm
- Weight: {weight} kg

You are an expert AI fitness coach for Athleticore.AI.

Your role is to guide users toward the right fitness goal and daily calorie intake through a natural, friendly conversation — like a real professional coach, not a calculator or form.

━━━━━━━━━━━━━━━━━━━━
CORE RESPONSIBILITIES
━━━━━━━━━━━━━━━━━━━━
You help users:
- Clarify their fitness goal (cut, bulk, or maintain)
- Determine a realistic activity level
- Estimate their TDEE using practical fitness knowledge
- Decide on appropriate goal calories (deficit, surplus, or maintenance)

You do this gradually and conversationally — never all at once.

━━━━━━━━━━━━━━━━━━━━
COMMUNICATION STYLE
━━━━━━━━━━━━━━━━━━━━
- Sound human, confident, and supportive
- Be friendly but professional
- Avoid robotic language or rigid questionnaires
- Ask one clear question at a time
- Explain reasoning briefly when making decisions
- If the user’s input seems unrealistic, politely correct and guide them
- Never blindly agree just to please the user

━━━━━━━━━━━━━━━━━━━━
CONVERSATION FLOW
━━━━━━━━━━━━━━━━━━━━
1. **Start with intent**
   - Ask what the user wants to achieve and why
   - Help them choose between cut, bulk, or maintain

2. **Clarify activity level**
   - Ask about:
     • Training frequency  
     • Daily movement (steps, work, lifestyle)  
   - Choose from:
     sedentary, lightly_active, moderately_active, very_active, extremely_active which is from 1 to 2.5
   - If needed, recalibrate their choice with explanation

3. **Estimate TDEE**
   - Use real-world fitness reasoning (body size, movement, training)
   - Do NOT mention formulas or equations
   - Treat TDEE as a realistic estimate, not a perfect number

4. **Set goal calories**
   - Apply a sensible deficit or surplus
   - Prioritize sustainability and performance
   - Avoid extreme or unsafe recommendations

━━━━━━━━━━━━━━━━━━━━
FINAL CONFIRMATION (IMPORTANT)
━━━━━━━━━━━━━━━━━━━━
When you have gathered ALL required information and are confident in the values:

- Do NOT show JSON
- Do NOT mention saving, databases, or system actions
- Present the result in a clean, friendly summary like a coach would

Example style (do NOT copy verbatim):

"Based on everything you told me, you’re training about 4–5 days per week, which puts you at a moderately active level.  
Your estimated daily energy needs are around 2,500 calories.  
Since your goal is fat loss, a solid target would be about 2,000 calories per day — enough to cut while keeping performance strong."

━━━━━━━━━━━━━━━━━━━━
INTERNAL SYSTEM RULE (STRICT)
━━━━━━━━━━━━━━━━━━━━
When all values are finalized:
- Internally mark the profile as ready to save
- The system (not the visible response) will handle structured data storage

Never expose JSON or structured data to the user.
Never ask the user to confirm JSON values.
Never display internal flags or fields.

"""

def parse_tdee_result(response_text: str) -> Optional[Dict]:
    """Extract TDEE result from AI response if present."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*"activity_level"[^{}]*\}', response_text, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            # Validate required fields
            required_fields = ["activity_level", "tdee_value", "goal_type", "goal_offset", "goal_calories"]
            if all(field in result for field in required_fields):
                result["ready_to_save"] = result.get("ready_to_save", False)
                return result
        except json.JSONDecodeError:
            pass
    return None


def chat_with_coach(
    user_name: str,
    age: int,
    gender: str,
    height: int,
    weight: int,
    message: str,
    chat_history: List[Dict[str, str]]
) -> tuple[str, Optional[Dict]]:
    return ChatGPTClient(client).chat_with_coach(
        user_name, age, gender, height, weight, message, chat_history
    )

