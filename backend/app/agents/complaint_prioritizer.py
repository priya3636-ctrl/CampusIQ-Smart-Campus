
import json


from app.services.llm_service import get_groq_llm


# ==========================================
# CAMPUSIQ - AI COMPLAINT PRIORITIZER
# ==========================================


DEPARTMENT_MAPPING = {
    "Electrical": "Electrical Department",
    "Plumbing": "Plumbing Department",
    "IT": "IT Support Department",
    "IT Equipment": "IT Support Department",
    "Furniture": "Furniture Maintenance Department",
    "Cleaning": "Housekeeping Department"
}

CRITICAL_KEYWORDS = [
    "fire",
    "smoke",
    "electric shock",
    "gas leak",
    "sparking",
    "exposed wire",
    "ceiling collapse",
    "structural damage"
]

HIGH_KEYWORDS = [
    "power failure",
    "water leakage",
    "server down",
    "projector not working",
    "computer not working",
    "broken door",
    "severe leakage"
]

MEDIUM_KEYWORDS = [
    "fan not working",
    "light not working",
    "chair broken",
    "slow internet",
    "tap not working"
]


def fallback_analysis(title, description, category):
    """Rule-based fallback if the hosted AI service is unavailable."""

    complaint_text = f"{title} {description}".lower()

    if any(word in complaint_text for word in CRITICAL_KEYWORDS):
        priority = "Critical"
        reason = (
            "Potential safety emergency. "
            "Immediate human attention is required."
        )

    elif any(word in complaint_text for word in HIGH_KEYWORDS):
        priority = "High"
        reason = "The issue may significantly affect campus activities."

    elif any(word in complaint_text for word in MEDIUM_KEYWORDS):
        priority = "Medium"
        reason = "The issue requires maintenance attention."

    else:
        priority = "Low"
        reason = "Routine maintenance is recommended."

    return {
        "recommended_priority": priority,
        "recommended_department": DEPARTMENT_MAPPING.get(
            category,
            "General Maintenance Department"
        ),
        "reason": reason
    }


def prioritize_complaint(title: str, description: str, category: str):
    """
    Analyze a maintenance complaint using the hosted Groq AI service.
    Critical safety indicators always take precedence.
    """

    complaint_text = f"{title} {description}".lower()

    # 1. Safety-first emergency detection
    if any(word in complaint_text for word in CRITICAL_KEYWORDS):
        return {
            "recommended_priority": "Critical",
            "recommended_department": DEPARTMENT_MAPPING.get(
                category,
                "General Maintenance Department"
            ),
            "reason": (
                "Potential safety emergency detected. "
                "Notify responsible campus personnel immediately "
                "and follow campus emergency procedures."
            )
        }

    # 2. Initialize local language model
    try:
        llm = get_groq_llm(temperature=0.0)

        # 3. Prepare structured AI prompt
        prompt = f"""
You are CampusIQ, a campus maintenance complaint assistant.

Analyze this complaint and return ONLY a valid JSON object.

Complaint title: {title}
Description: {description}
Category: {category}

Choose exactly one priority:
Low, Medium, or High.

Department mapping:
Electrical = Electrical Department
Plumbing = Plumbing Department
IT Equipment = IT Support Department
Furniture = Furniture Maintenance Department
Cleaning = Housekeeping Department

Return exactly these JSON keys:
{{
  "recommended_priority": "Low, Medium, or High",
  "recommended_department": "Department name",
  "reason": "Short explanation"
}}

Do not include Markdown or text outside the JSON.
"""

        # 4. Ask the hosted AI model
        response = llm.invoke(prompt)

        # 5. Parse and validate AI response, tolerating JSON code fences.
        raw_response = str(response.content).strip()
        if raw_response.startswith("```"):
            raw_response = raw_response.strip("`")
            if raw_response.lower().startswith("json"):
                raw_response = raw_response[4:].strip()

        json_start = raw_response.find("{")
        json_end = raw_response.rfind("}")
        if json_start < 0 or json_end <= json_start:
            raise ValueError("AI response did not contain a JSON object.")

        result = json.loads(raw_response[json_start:json_end + 1])

        valid_priorities = {"Low", "Medium", "High"}

        if result.get("recommended_priority") not in valid_priorities:
            raise ValueError("Invalid priority returned by AI")

        expected_department = DEPARTMENT_MAPPING.get(
            category,
            "General Maintenance Department"
        )

        # Use the trusted category mapping rather than an
        # unverified department name returned by the model.
        return {
            "recommended_priority": result["recommended_priority"],
            "recommended_department": expected_department,
            "reason": str(result.get("reason", "AI analysis completed."))
        }

    except Exception as error:
        print(f"CampusIQ AI fallback activated: {error}")

        return fallback_analysis(
            title,
            description,
            category
        )
