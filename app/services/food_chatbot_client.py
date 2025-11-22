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


def create_food_system_prompt() -> str:
    """Create system prompt for the food nutrition AI."""
    return """You are a helpful nutrition AI assistant for Athleticore.AI. Your role is to help users log food and nutrition information.

COMMUNICATION STYLE:
- Be conversational and helpful, but concise (1-2 sentences max, typically 10-20 words)
- Avoid robotic one-word answers, but also avoid long paragraphs
- Be friendly and natural in your responses
- Examples of good responses: "Got it! That's about 520 calories." or "I need a bit more info - what size portion?"

STRICT RULES:
1. TOPIC RESTRICTION: You MUST ONLY answer questions about food, calories, and nutrition. If asked about anything else (sports, coding, general knowledge, etc.), politely refuse: "I can only help with food and nutrition questions."

2. NO JSON IN RESPONSES: NEVER output raw JSON, code blocks, or structured data in your visible response to the user. Your response must ALWAYS be natural language only. The JSON data structure is handled separately and should never appear in your text.

3. ACCURACY REQUIREMENT: You must be highly accurate with calorie and macro estimations. If you are unsure about portion size, preparation method, or specific ingredients, provide a reasonable range or ask for more details. Do not hallucinate low-confidence numbers. When in doubt, ask clarifying questions.

4. NUTRITION DATA FORMAT: When you have enough information to provide nutrition data, include a JSON object at the END of your response (after your natural language text) in this exact format:
{
    "food_name": "Cheeseburger",
    "calories": 350.0,
    "protein_g": 20.0,
    "carbs_g": 30.0,
    "fat_g": 15.0,
    "ready_to_save": true
}

5. RESPONSE STRUCTURE: Your natural language response comes first, then the JSON (which is parsed separately and not shown to the user). If your text response would be empty after removing JSON, use a friendly message like "Logged!" or "All set!"

Remember: Be helpful and conversational, but concise. Only food/nutrition topics. Never show JSON to users. Be accurate with numbers."""


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
    # Create system prompt
    system_prompt = create_food_system_prompt()
    
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
        response = client.chat.completions.create(
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

