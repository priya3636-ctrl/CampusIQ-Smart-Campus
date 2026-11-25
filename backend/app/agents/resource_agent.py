
import re


def analyze_resources(resource_data: str):

    if not resource_data or not resource_data.strip():
        return {
            "agent": "Resource Management Agent",
            "status": "error",
            "summary": "No resource information provided.",
            "resource_issues": [],
            "recommendations": []
        }

    text = resource_data.lower()

    resource_issues = []
    recommendations = []
    summary = "Campus resource information reviewed."

    # Initialize values to prevent UnboundLocalError.
    total = None
    working = None
    faulty = None

    # Pattern 1: 22 out of 30 computers are working.
    working_match = re.search(
        r"(\d+)\s+out\s+of\s+(\d+)\s+computers?\s+(?:are\s+)?working",
        text
    )

    # Pattern 2: 30 computers, but only 22 are working.
    only_working_match = re.search(
        r"(\d+)\s+computers?.*?\bonly\s+(\d+)\s+(?:are\s+)?working",
        text
    )
    # Pattern 3: 30 computers, 22 working.
    short_working_match = re.search(
    r"(\d+)\s+computers?\s*,?\s*(\d+)\s+working",
    text
    )

    # Pattern 3: 30 computers, 8 are not working.
    faulty_match = re.search(
        r"(\d+)\s+computers?.*?(\d+)\s+(?:are\s+)?not working",
        text
    )

    # Extract computer availability.
    if working_match:
        working = int(working_match.group(1))
        total = int(working_match.group(2))

    elif only_working_match:
        total = int(only_working_match.group(1))
        working = int(only_working_match.group(2))
    elif short_working_match:
         total = int(short_working_match.group(1))
         working = int(short_working_match.group(2))

    elif faulty_match:
        total = int(faulty_match.group(1))
        faulty = int(faulty_match.group(2))

        if total > 0 and faulty <= total:
            working = total - faulty

    # Calculate computer availability.
    if (
        total is not None
        and working is not None
        and total > 0
        and 0 <= working <= total
    ):
        faulty = total - working

        summary = (
            f"{working} out of {total} computers are working, "
            f"while {faulty} require attention."
        )

        if faulty > 0:
            resource_issues.append(
                f"{faulty} out of {total} computers are not working."
            )

            recommendations.append(
                "Arrange inspection and repair of the non-working computers."
            )

    # Library resources.
    if (
        "limited computer access" in text
        or "limited library computer" in text
        or "insufficient library computers" in text
    ):
        resource_issues.append(
            "The library has limited computer access."
        )

        recommendations.append(
            "Review library computer availability and consider "
            "improving access for students."
        )

    # Projector issues.
    if "projector" in text:
        resource_issues.append(
            "Projector-related resource concerns were reported."
        )

        recommendations.append(
            "Inspect reported projectors and repair faulty equipment."
        )

    # Internet issues.
    if "internet" in text or "wi-fi" in text or "wifi" in text:
        resource_issues.append(
            "Internet connectivity concerns were reported."
        )

        recommendations.append(
            "Check network connectivity and identify affected areas."
        )

    if not resource_issues:
        resource_issues.append(
            "No specific resource issue could be identified."
        )

    if not recommendations:
        recommendations.append(
            "Maintain an updated inventory of campus resources."
        )

    return {
        "agent": "Resource Management Agent",
        "status": "success",
        "summary": summary,
        "resource_issues": resource_issues,
        "recommendations": recommendations
    }
