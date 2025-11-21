from typing import Optional, List, Dict, Any
import os
import json
from groq import Groq

_groq_api_key = os.environ.get("GROQ_API_KEY")
client: Optional[Groq] = None
if _groq_api_key:
    client = Groq(api_key=_groq_api_key)


def _build_response(
    reply_text: str,
    extracted_inputs: Optional[Dict[str, Any]] = None,
    tdee_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "reply": reply_text,
        "extracted_inputs": extracted_inputs or {},
        "tdee_result": tdee_result,
    }


def _calculate_tdee_from_inputs(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        age = float(data["age"])
        height = float(data["height_cm"])
        weight = float(data["weight_kg"])
        activity = float(data["activity_level"])
        gender = str(data["gender"]).lower()
    except (KeyError, TypeError, ValueError):
        return None

    if gender not in {"male", "female"}:
        return None

    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    tdee_value = bmr * activity

    goal_type = data.get("goal_type", "maintain")
    goal_offset = data.get("goal_offset")
    try:
        goal_offset = float(goal_offset)
    except (TypeError, ValueError):
        goal_offset = 0.0

    if goal_offset == 0.0:
        goal_offset = 300.0 if goal_type == "bulk" else -500.0 if goal_type == "cut" else 0.0

    goal_calories = tdee_value + goal_offset

    return {
        "tdee_value": tdee_value,
        "goal_type": goal_type,
        "goal_offset": goal_offset,
        "goal_calories": goal_calories,
        "ready_to_save": True,
    }


def _parse_assistant_json(content: str) -> Dict[str, Any]:
    try:
        payload = json.loads(content)
        reply_text = payload.get("assistant_reply") or payload.get("reply") or content
        extracted = payload.get("collected_data") or payload.get("extracted_inputs") or {}
        tdee_result = payload.get("tdee_result")
        return {
            "reply_text": reply_text,
            "extracted_inputs": extracted,
            "tdee_result": tdee_result,
        }
    except json.JSONDecodeError:
        return {
            "reply_text": content,
            "extracted_inputs": {},
            "tdee_result": None,
        }


def tdee_assistant_reply(
    user_message: str,
    username: Optional[str] = None,
    previous_messages: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    assistant_name = username or "Athlete"

    if client is None:
        demo_inputs = {
            "gender": "female",
            "age": 29,
            "height_cm": 165,
            "weight_kg": 60,
            "activity_level": 1.55,
            "goal_type": "cut",
            "goal_offset": -500,
        }
        demo_result = _calculate_tdee_from_inputs(demo_inputs)
        reply_text = (
            f"Hi {assistant_name}, I'm running in demo mode. "
            "Here's a sample TDEE plan so you can see the flow working."
        )
        return _build_response(reply_text, demo_inputs, demo_result)

    system_prompt = (
        "You are Athleticore.AI's TDEE assistant.\n"
        "Always respond as valid JSON matching this schema:\n"
        "{\n"
        '  "assistant_reply": "text you would normally say to the user",\n'
        '  "collected_data": {\n'
        '      "age": number,\n'
        '      "gender": "male|female",\n'
        '      "height_cm": number,\n'
        '      "weight_kg": number,\n'
        '      "activity_level": number,\n'
        '      "goal_type": "cut|bulk|maintain",\n'
        '      "goal_offset": number\n'
        "  },\n"
        '  "tdee_result": {\n'
        '      "tdee_value": number,\n'
        '      "goal_type": "cut|bulk|maintain",\n'
        '      "goal_offset": number,\n'
        '      "goal_calories": number,\n'
        '      "ready_to_save": boolean\n'
        "  }\n"
        "}\n"
        "Keep responses concise, coach-like, and fill in collected_data as you learn more.\n"
        "Only include tdee_result once you have enough data; set ready_to_save true when complete."
    )

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if previous_messages:
        for msg in previous_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": f"{assistant_name}: {user_message}"})

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.4,
        )
        content = completion.choices[0].message.content
        parsed = _parse_assistant_json(content)
        reply_text = parsed["reply_text"]
        extracted_inputs = parsed["extracted_inputs"]
        tdee_result = parsed["tdee_result"]

        if not tdee_result and extracted_inputs:
            tdee_result = _calculate_tdee_from_inputs(extracted_inputs)

        return _build_response(reply_text, extracted_inputs, tdee_result)
    except Exception as e:
        return _build_response(
            "There was an error talking to the Llama API.\n"
            "Please check your internet connection or GROQ_API_KEY and try again.",
            tdee_result={"error": str(e)},
        )

