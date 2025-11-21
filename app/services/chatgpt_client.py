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


def create_system_prompt(user_name: str, age: int, gender: str, height: int, weight: int) -> str:
    """Create system prompt for the AI coach with user stats."""
    return f"""You are an expert AI fitness coach for Athleticore.AI. Your role is to help users determine their fitness goals and calculate their TDEE (Total Daily Energy Expenditure).

User Information:
- Name: {user_name}
- Age: {age}
- Gender: {gender}
- Height: {height} cm
- Weight: {weight} kg

Your tasks:
1. Help the user determine their fitness goal: "cut" (lose weight), "bulk" (gain weight), or "maintain" (maintain current weight)
2. Determine their activity level factor based on their lifestyle and exercise habits. Use standard activity levels: "sedentary", "lightly_active", "moderately_active", "very_active", or "extremely_active"
3. Calculate their TDEE (Total Daily Energy Expenditure) using your knowledge of fitness calculations
4. Calculate their goal calories based on their goal type and a goal offset (calorie deficit/surplus)

Important:
- Use your AI reasoning to calculate TDEE - do not use built-in formulas, but use your understanding of metabolism and energy expenditure
- Be conversational and helpful
- Ask clarifying questions about their activity level and goals
- When you have enough information, provide the values in a structured format

When you have determined the values, respond with a JSON object in this exact format:
{{
    "activity_level": "moderately_active",
    "tdee_value": 2500.0,
    "goal_type": "cut",
    "goal_offset": 500,
    "goal_calories": 2000.0,
    "ready_to_save": true
}}

Only include this JSON when you have all the information needed. Otherwise, continue the conversation naturally."""


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
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # or another Llama model
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

