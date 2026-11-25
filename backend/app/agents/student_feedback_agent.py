
import re
from langchain_ollama import ChatOllama

MODEL_NAME = "qwen2.5:0.5b"


def extract_positive_feedback(text):
    """Extract positive feedback without duplicating sentences."""

    positive_patterns = [
        r"\bclean\b",
        r"\bwell maintained\b",
        r"\bgood\b",
        r"\bexcellent\b",
        r"\bcomfortable\b",
        r"\bhelpful\b",
        r"\bproperly maintained\b",
        r"\bhappy with\b",
        r"\bsatisfied\b"
    ]

    clauses = re.split(
        r"\bbut\b|\bhowever\b|\byet\b",
        text,
        flags=re.IGNORECASE
    )

    positive_points = []

    for clause in clauses:
        clause = clause.strip(" ,.")

        if (
            clause
            and any(
                re.search(pattern, clause, re.IGNORECASE)
                for pattern in positive_patterns
            )
        ):
            positive_points.append(clause)

    return remove_duplicate_issues(positive_points)


def is_negative_feedback(text):
    """Identify complaints and improvement requirements."""

    negative_patterns = [
        r"\bneed\b",
        r"\bneeds\b",
        r"\brequire\b",
        r"\bpoor\b",
        r"\bnot working\b",
        r"\bdoesn't work\b",
        r"\bdoes not work\b",
        r"\bproblem\b",
        r"\bissue\b",
        r"\black of\b",
        r"\binsufficient\b",
        r"\bimprove\b",
        r"\bcomplaint\b",
        r"\bslow\b",
        r"\bshortage\b",
        r"\bmore\b",
        r"\bbetter\b"
    ]

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in negative_patterns
    )


def remove_duplicate_issues(issues):
    """Remove duplicate or repeated feedback."""

    unique_issues = []
    seen = set()

    for issue in issues:
        issue = str(issue).strip(" ,.")

        if not issue:
            continue

        normalized = re.sub(
            r"[^a-z0-9\s]",
            "",
            issue.lower()
        )

        normalized = re.sub(r"\s+", " ", normalized).strip()

        if normalized not in seen:
            seen.add(normalized)
            unique_issues.append(issue)

    return unique_issues

def extract_negative_feedback(text):
    """Separate individual student complaints and clean their wording."""

    clauses = re.split(
        r"\bbut\b|\bhowever\b|\byet\b",
        text,
        flags=re.IGNORECASE
    )

    issues = []

    for clause in clauses:
        if not is_negative_feedback(clause):
            continue

        # Remove introductory phrases.
        clause = re.sub(
            r"^\s*(?:(?:students?|they)\s+)?(?:reported|report|mentioned|mention|complained|complain)\s+",
            "",
            clause,
            flags=re.IGNORECASE
        )

        # Separate individual concerns.
        parts = re.split(
            r"\s*,\s*|\s+\band\b\s+",
            clause,
            flags=re.IGNORECASE
        )

        for part in parts:
            part = part.strip(" ,.")
            part = re.sub(
    r"^(?:they|students?)\s+(?:reported|report|mentioned|mention|complained|complain)\s+",
    "",
    part,
    flags=re.IGNORECASE
)

            # Remove unnecessary introductory wording.
            part = re.sub(
                r"^(?:they\s+)?(?:reported|mentioned|complained)\s+",
                "",
                part,
                flags=re.IGNORECASE
            )

            part = re.sub(
                r"^(?:and\s+)?(?:there\s+is\s+)?(?:a\s+)?(?:need|requirement)\s+for\s+",
                "",
                part,
                flags=re.IGNORECASE
            )

            part = part.strip(" ,.")

            if part and is_negative_feedback(part):
                issues.append(part)

    return remove_duplicate_issues(issues)
def get_recommendation(issue):
    """Generate a recommendation for each reported issue."""

    text = issue.lower()

    if re.search(r"wi[ -]?fi|internet|wireless|network", text):
        return (
            "Assess Wi-Fi coverage and capacity, then improve "
            "network access points where connectivity is weak."
        )

    if re.search(r"computer|laptop", text):
        return (
            "Increase computer availability and arrange inspection "
            "and repair of faulty computers."
        )

    if re.search(r"ventilation|air circulation|airflow", text):
        return (
            "Inspect classroom ventilation systems and improve "
            "air circulation."
        )

    if re.search(r"drinking water|water facility|water facilities", text):
        return (
            "Ensure clean drinking water facilities are available "
            "and regularly maintained."
        )

    if re.search(r"library", text):
        return (
            "Review library facilities and improve the resources "
            "available to students."
        )

    if re.search(r"clean|cleanliness|hygiene", text):
        return (
            "Improve campus cleaning schedules and regularly "
            "inspect cleanliness standards."
        )

    if re.search(r"faculty|teacher", text):
        return (
            "Review student feedback and support faculty "
            "development where necessary."
        )

    return (
        f"Investigate the reported concern ({issue}) "
        "and take appropriate improvement measures."
    )


def analyze_student_feedback(feedback: str):

    if not feedback or not feedback.strip():
        return {
            "agent": "Student Feedback Agent",
            "status": "error",
            "summary": "No student feedback was provided.",
            "positive_points": [],
            "issues": [],
            "recommendations": []
        }

    try:
        # Extract positive and negative feedback using rules.
        positive_points = extract_positive_feedback(feedback)
        issues = extract_negative_feedback(feedback)

        # Generate one recommendation for each unique issue.
        recommendations = remove_duplicate_issues([
            get_recommendation(issue)
            for issue in issues
        ])

        # Use Ollama for the summary.
        try:
            llm = ChatOllama(
                model=MODEL_NAME,
                temperature=0
            )

            prompt = f"""
You are CampusIQ Student Feedback Agent.

Summarize the following student feedback in one or two
clear sentences. Do not invent information.

Student feedback:
{feedback}

Return only the summary text.
"""

            response = llm.invoke(prompt)
            summary = str(response.content).strip()

            if not summary:
                summary = feedback.strip()

            status = "success"

        except Exception as llm_error:
            print(f"Student Feedback LLM error: {llm_error}")
            summary = feedback.strip()
            status = "fallback"

        return {
            "agent": "Student Feedback Agent",
            "status": status,
            "summary": summary,
            "positive_points": positive_points,
            "issues": issues,
            "recommendations": recommendations
        }

    except Exception as error:
        print(f"Student Feedback Agent error: {error}")

        return {
            "agent": "Student Feedback Agent",
            "status": "fallback",
            "summary": feedback.strip(),
            "positive_points": extract_positive_feedback(feedback),
            "issues": extract_negative_feedback(feedback),
            "recommendations": [
                get_recommendation(issue)
                for issue in extract_negative_feedback(feedback)
            ]
        }
