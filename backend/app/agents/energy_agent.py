
import re


def analyze_energy(energy_data: str):

    if not energy_data or not energy_data.strip():
        return {
            "agent": "Energy Analysis Agent",
            "status": "error",
            "summary": "No energy information provided.",
            "energy_issues": [],
            "recommendations": []
        }

    text = energy_data.lower()

    energy_issues = []
    recommendations = []

    previous = None
    current = None

    # Pattern 1: from 12000 to 16000 kWh
    range_match = re.search(
        r"from\s+([\d,]+(?:\.\d+)?)\s*"
        r"(?:kwh\s*)?to\s+([\d,]+(?:\.\d+)?)\s*kwh",
        energy_data,
        re.IGNORECASE
    )

    if range_match:
        previous = float(range_match.group(1).replace(",", ""))
        current = float(range_match.group(2).replace(",", ""))

    else:
        # Pattern 2: 12000 kWh and 16000 kWh
        readings = re.findall(
            r"([\d,]+(?:\.\d+)?)\s*kwh",
            energy_data,
            re.IGNORECASE
        )

        if len(readings) >= 2:
            previous = float(readings[0].replace(",", ""))
            current = float(readings[1].replace(",", ""))

    summary = (
        "Energy information reviewed. "
        "More consumption readings are needed for a numerical comparison."
    )

    if previous is not None and current is not None:

        difference = current - previous

        if previous > 0:
            percentage = abs(difference) / previous * 100
        else:
            percentage = None

        if difference > 0:
            summary = (
                f"Electricity consumption increased by "
                f"{difference:,.2f} kWh."
            )

            if percentage is not None:
                summary += f" This is a {percentage:.2f}% increase."

            energy_issues.append(summary)

            recommendations.append(
                "Investigate the increase in electricity consumption "
                "across campus buildings."
            )

            recommendations.append(
                "Introduce energy-saving practices and monitor "
                "monthly electricity usage."
            )

        elif difference < 0:
            summary = (
                f"Electricity consumption decreased by "
                f"{abs(difference):,.2f} kWh."
            )

            if percentage is not None:
                summary += f" This is a {percentage:.2f}% decrease."

            energy_issues.append(summary)

            recommendations.append(
                "Continue monitoring electricity consumption "
                "to maintain the improvement."
            )

        else:
            summary = (
                "Electricity consumption remained unchanged "
                "between the two readings."
            )

    # Detect unnecessary electricity usage
    if "light" in text and any(
        word in text for word in ["left on", "running", "unnecessarily"]
    ):
        energy_issues.append(
            "Classroom lights may be left running unnecessarily."
        )
        recommendations.append(
            "Switch off classroom lights when rooms are not in use."
        )

    if "fan" in text and any(
        word in text for word in ["left on", "running", "unnecessarily"]
    ):
        energy_issues.append(
            "Fans may be left running after classes."
        )
        recommendations.append(
            "Switch off fans after classroom activities."
        )

    if (
        "increased electricity consumption" in text
        and not any("increased by" in issue for issue in energy_issues)
    ):
        energy_issues.append(
            "The campus has reported increased electricity consumption."
        )
        recommendations.append(
            "Review electricity usage across campus buildings."
        )

    if not energy_issues:
        energy_issues.append(
            "No specific energy issue could be identified "
            "from the supplied information."
        )

    if not recommendations:
        recommendations.append(
            "Collect regular electricity readings to identify usage patterns."
        )

    return {
        "agent": "Energy Analysis Agent",
        "status": "success",
        "summary": summary,
        "energy_issues": energy_issues,
        "recommendations": recommendations
    }
