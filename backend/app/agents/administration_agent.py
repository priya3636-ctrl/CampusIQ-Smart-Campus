
def analyze_administration(campus_data: str):

    if not campus_data or not campus_data.strip():
        return {
            "agent": "Administration Agent",
            "status": "error",
            "summary": "No campus administration information provided.",
            "key_findings": [],
            "recommendations": []
        }

    text = campus_data.lower()

    key_findings = []
    recommendations = []

    def add_finding(finding, recommendation):
        if finding not in key_findings:
            key_findings.append(finding)

        if recommendation not in recommendations:
            recommendations.append(recommendation)

    # 1. Projector issues
    if "projector" in text and any(word in text for word in [
        "not working", "broken", "faulty", "problem", "issue",
        "repair", "poor"
    ]):
        add_finding(
            "Projector-related equipment requires attention.",
            "Inspect faulty projectors and arrange necessary repairs."
        )

    # 2. Computer and resource availability
    if any(word in text for word in [
        "computer", "computers", "resource", "resources", "laptop"
    ]) and any(word in text for word in [
        "not working", "limited", "lack", "insufficient",
        "shortage", "need", "broken", "faulty", "unavailable"
    ]):
        add_finding(
            "Campus computer or resource availability requires attention.",
            "Inspect faulty equipment and improve resource availability."
        )

    # 3. Library facilities
    if "library" in text and any(word in text for word in [
        "limited", "lack", "insufficient", "shortage",
        "need", "not working", "poor"
    ]):
        add_finding(
            "Library facilities or resources require improvement.",
            "Review library facilities and improve resource availability."
        )

    # 4. Internet and Wi-Fi
    if any(word in text for word in [
        "wi-fi", "wifi", "internet", "connectivity", "network"
    ]) and any(word in text for word in [
        "need", "poor", "slow", "problem", "issue",
        "unavailable", "not working", "improve"
    ]):
        add_finding(
            "Campus internet connectivity requires attention.",
            "Review network coverage and improve internet connectivity."
        )

    # 5. Drinking water
    if any(phrase in text for phrase in [
        "drinking water", "water facility", "water facilities",
        "water shortage", "water problem"
    ]):
        add_finding(
            "Drinking water facilities require administrative attention.",
            "Ensure clean drinking water is available and regularly maintained."
        )

    # 6. Ventilation
    if any(word in text for word in [
        "ventilation", "air circulation", "airflow"
    ]):
        add_finding(
            "Classroom ventilation requires attention.",
            "Inspect ventilation systems and improve classroom air circulation."
        )

    # 7. Electrical and fan problems
    if any(word in text for word in [
        "electricity", "electrical", "power failure",
        "power outage", "fan", "fans", "light", "lights"
    ]) and any(word in text for word in [
        "not working", "broken", "faulty", "problem",
        "issue", "failure", "repair", "leakage"
    ]):
        add_finding(
            "Electrical equipment and classroom facilities require inspection.",
            "Inspect electrical equipment and arrange necessary repairs."
        )

    # 8. Water leakage
    if any(phrase in text for phrase in [
        "water leakage", "water leak", "leaking pipe",
        "pipe leakage", "leakage near"
    ]):
        add_finding(
            "Water leakage has been reported on campus.",
            "Inspect the affected area and arrange plumbing repairs."
        )

    # 9. Cleanliness and hygiene
    if any(word in text for word in [
        "unclean", "dirty", "cleanliness problem",
        "poor hygiene", "sanitation problem"
    ]):
        add_finding(
            "Campus cleanliness and hygiene require attention.",
            "Improve cleaning schedules and regularly inspect campus hygiene."
        )

    # 10. Increased electricity consumption
    if any(phrase in text for phrase in [
        "increased electricity consumption",
        "electricity consumption increased",
        "high electricity usage",
        "increased electricity bill"
    ]):
        add_finding(
            "Increased electricity consumption has been reported.",
            "Monitor electricity usage and introduce energy-saving practices."
        )

    # 11. General maintenance
    if any(word in text for word in [
        "complaint", "repair", "broken", "faulty", "not working"
    ]):
        add_finding(
            "Campus equipment requires administrative attention.",
            "Review maintenance complaints and prioritize pending repairs."
        )

    if not key_findings:
        key_findings.append(
            "No specific administrative issue was identified."
        )

    if not recommendations:
        recommendations.append(
            "Collect more detailed campus information for further analysis."
        )

    summary = (
        f"Identified {len(key_findings)} administrative finding(s) "
        f"and generated {len(recommendations)} recommendation(s)."
    )

    return {
        "agent": "Administration Agent",
        "status": "success",
        "summary": summary,
        "key_findings": key_findings,
        "recommendations": recommendations
    }
