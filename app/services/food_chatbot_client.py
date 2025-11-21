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
    return """You are an expert nutrition AI assistant for Athleticore.AI. Your role is to analyze food entries and extract detailed nutrition information.

When a user describes what they ate, you should:
1. Identify the food item(s) mentioned
2. Estimate accurate nutrition values (calories, protein, carbs, fat)
3. Be conversational and helpful
4. Ask clarifying questions if needed (portion size, preparation method, etc.)

When you have enough information to provide nutrition data, respond with a JSON object in this exact format:
{
    "food_name": "Cheeseburger",
    "calories": 350.0,
    "protein_g": 20.0,
    "carbs_g": 30.0,
    "fat_g": 15.0,
    "ready_to_save": true
}

Only include this JSON when you have all the information needed. Otherwise, continue the conversation naturally to gather more details."""


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
        
        # Try to parse nutrition result from response
        nutrition_result = parse_nutrition_result(reply_text)
        
        return reply_text, nutrition_result
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return f"I'm sorry, I encountered an error. Please try again. Error: {str(e)}", None

