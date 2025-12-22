import os
from groq import Groq
from typing import List, Dict

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=GROQ_API_KEY)


class AIChatClient:
    """Encapsulate Groq client for the AI coach chat."""

    def __init__(self, groq_client: Groq) -> None:
        self._client = groq_client

    def get_client(self) -> Groq:
        return self._client

    def set_client(self, groq_client: Groq) -> None:
        self._client = groq_client

    def chat_with_ai_coach(
        self,
        user_name: str,
        age: int,
        gender: str,
        height: int,
        weight: int,
        message: str,
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Send a message to the AI coach and get response.

        Args:
            user_name: User's name
            age: User's age
            gender: User's gender
            height: User's height in cm
            weight: User's weight in kg
            message: Current user message
            chat_history: List of previous messages in format [{"role": "user"/"ai", "content": "..."}]

        Returns:
            AI response text
        """
        # Create system prompt with user stats
        system_prompt = create_chat_system_prompt(user_name, age, gender, height, weight)

        # Build messages for the API
        messages = [{"role": "system", "content": system_prompt}]

        # Add chat history (convert to API format)
        for msg in chat_history:
            role = msg.get("role", "user")
            # Convert "ai" role to "assistant" for Groq API
            if role == "ai":
                role = "assistant"
            messages.append({
                "role": role,
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
            return reply_text

        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"I'm sorry, I encountered an error. Please try again. Error: {str(e)}"


def create_chat_system_prompt(user_name: str, age: int, gender: str, height: int, weight: int) -> str:
    """Create system prompt for the general AI fitness coach chatbot."""
    return f"""You are an expert AI fitness coach and nutritionist for Athleticore.AI. Your role is to provide personalized fitness, nutrition, and wellness guidance to users.

User Information:
- Name: {user_name}
- Age: {age}
- Gender: {gender}
- Height: {height} cm
- Weight: {weight} kg

Your expertise includes:
- Workout programming and exercise form
- Nutrition and meal planning
- Weight management (cutting, bulking, maintaining)
- Muscle building and strength training
- Cardiovascular fitness
- Recovery and rest
- Supplement guidance
- General health and wellness

Guidelines:
- Be conversational, friendly, and encouraging
- Provide accurate, evidence-based advice
- Ask clarifying questions when needed
- Keep responses concise but informative
- Personalize advice based on the user's stats
- Be supportive and motivational
- If asked about topics outside fitness/nutrition, politely redirect to fitness-related topics

Always maintain a professional yet approachable tone. Help users achieve their fitness goals safely and effectively."""


def chat_with_ai_coach(
    user_name: str,
    age: int,
    gender: str,
    height: int,
    weight: int,
    message: str,
    chat_history: List[Dict[str, str]]
) -> str:
    return AIChatClient(client).chat_with_ai_coach(
        user_name, age, gender, height, weight, message, chat_history
    )

