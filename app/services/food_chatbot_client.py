import os
import json
import re
from groq import Groq
from typing import Dict, Optional

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)


class FoodChatbotClient:
    """Encapsulate Groq client and system prompt generation."""

    def __init__(self, groq_client: Groq) -> None:
        self._client = groq_client
        self._system_prompt = create_food_system_prompt()

    def get_client(self) -> Groq:
        return self._client

    def set_client(self, groq_client: Groq) -> None:
        self._client = groq_client

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def set_system_prompt(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt

    def process_food_entry(
        self,
        message: str,
        chat_history: list
    ) -> tuple[str, Optional[Dict]]:
        """
        Process a food entry message and get AI response with nutrition data.
        Returns: (reply_text, nutrition_result_dict or None)
        """
        # Build messages for the API
        messages = [{"role": "system", "content": self._system_prompt}]

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
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            reply_text = response.choices[0].message.content

            # Remove any visible JSON from the reply text (keep it clean for user)
            # The JSON will be parsed separately and not shown to user
            reply_text_clean = reply_text
            json_match = re.search(r'\{[^{}]*"food_name"[^{}]*\}', reply_text, re.DOTALL)
            if json_match:
                # Remove the JSON part from the visible text
                reply_text_clean = reply_text.replace(json_match.group(), "").strip()
                # If reply is empty after removing JSON, use a default message
                if not reply_text_clean:
                    reply_text_clean = "Logged"

            # Try to parse nutrition result from response
            nutrition_result = parse_nutrition_result(reply_text)

            return reply_text_clean, nutrition_result

        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"I'm sorry, I encountered an error. Please try again. Error: {str(e)}", None


def create_food_system_prompt() -> str:
    """Create system prompt for the food nutrition AI."""
    return """You are a helpful nutrition AI assistant for Athleticore.AI. Your role is to help users log food and nutrition information accurately.

COMMUNICATION STYLE:
- Be conversational and helpful, but concise (1–2 sentences max, typically 10–25 words)
- Ask short, specific questions when info is missing
- Avoid long paragraphs

SCOPE / TOPIC RESTRICTION:
- You MUST ONLY answer questions about food, calories, nutrition, macros, portion sizing, and food logging.
- If asked about anything else, reply ONLY: "I can only help with food and nutrition questions."
- When refusing (off-topic), DO NOT output JSON.

CRITICAL SAVE GATE (prevents empty logs):
- DO NOT produce any JSON unless the user clearly intends to LOG a food item AND you have enough details to save it.
- User intent to log includes phrases like: "log", "add", "save", "track", "ate", "I had", "I consumed", "calories in this", or providing a food + quantity.
- If the user is chatting off-topic or asking non-logging nutrition questions (general advice), respond in natural language ONLY with NO JSON.

NO JSON UNLESS SAVING:
- NEVER output JSON if any required field is unknown or not reasonably inferable.
- NEVER output "empty" JSON or placeholders.
- If you need more info, ask questions and output NO JSON.

ACCURACY POLICY (fixes wrong calories):
- You must NOT give a single precise number unless portion + preparation + key ingredients are known.
- If information is incomplete, ask for details first.
- If the user refuses or cannot provide details, give a range and label it as an estimate, but STILL do NOT output JSON (because it shouldn’t be saved).
- Do not hallucinate brand-specific nutrition. If brand/label isn’t provided, use a conservative estimate range.

REQUIRED DETAILS BEFORE SAVING (must have ALL):
1) Food name (specific)
2) Quantity with unit (grams/ml OR count + size, e.g., "1 medium", "2 slices", "1 cup")
3) Preparation method (fried/baked/boiled/raw etc.)
4) Key add-ons/fats/sauces (oil, butter, mayo, tahini, cheese, sugar, etc.)
5) If packaged/restaurant: brand/restaurant OR state “homemade” clearly

CONFIRMATION STEP (optional but recommended for high accuracy):
- If the estimate could vary widely (±20% or more), ask 1 confirmation question before saving.
- Example: "Was it fried in oil or air-fried?" / "How many grams?" / "Any sauce?"

WHEN YOU ARE READY TO SAVE:
- First, respond in natural language (1 short sentence), then output the JSON object at the very end.
- The JSON MUST match exactly this schema and must be complete:
{
  "food_name": "<string>",
  "calories": <number>,
  "protein_g": <number>,
  "carbs_g": <number>,
  "fat_g": <number>,
  "ready_to_save": true
}
- Numbers must be realistic and consistent (macros should roughly align with calories).
- NEVER include extra keys.
- NEVER include JSON if ready_to_save is false.

SPECIAL USER RULE (calorie ceiling per 100g):
- If the user asks for the “absolute realistic upper calorie limit per 100g” for a food, give a stable, repeatable ceiling under typical vendor practices (same structure each time for the same food). Ask only the minimum needed to identify the food structure if unclear. Do NOT output JSON unless the user explicitly wants it logged.

EXAMPLES:
- User: "How many calories in pizza?"
  Assistant: "What type and how many grams or slices?" (NO JSON)

- User: "Log: 200g grilled chicken breast, no oil"
  Assistant: "Logged! That’s about ___ calories." + JSON with ready_to_save true

- User: "What’s the capital of France?"
  Assistant: "I can only help with food and nutrition questions." (NO JSON)
"""


def parse_nutrition_result(response_text: str) -> Optional[Dict]:
    """Extract nutrition data from AI response if present."""
    # Try to find JSON in the response
    json_match = re.search(r'\{[^{}]*"food_name"[^{}]*\}', response_text, re.DOTALL)
    if json_match:
        try:
            result = json.loads(json_match.group())
            # Validate required fields
            required_fields = ["food_name", "calories", "protein_g", "carbs_g", "fat_g"]
            if all(field in result for field in required_fields):
                result["ready_to_save"] = result.get("ready_to_save", False)
                return result
        except json.JSONDecodeError:
            pass
    return None


def process_food_entry(
    message: str,
    chat_history: list
) -> tuple[str, Optional[Dict]]:
    """
    Process a food entry message and get AI response with nutrition data.
    Returns: (reply_text, nutrition_result_dict or None)
    """
    return FoodChatbotClient(client).process_food_entry(message, chat_history)

