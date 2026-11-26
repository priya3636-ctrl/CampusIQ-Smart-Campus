
import re


DAYS = (
    "Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
)


def analyze_schedule(schedule_data: str):

    if not schedule_data or not schedule_data.strip():
        return {
            "agent": "Scheduling Agent",
            "status": "error",
            "summary": "No scheduling information provided.",
            "conflicts": [],
            "recommendations": []
        }

    assignments = {}

    def add_assignment(room, day, time, department=None, count=1):

        room = re.sub(r"\s+", " ", room.strip()).strip(" ,.")
        day = day.capitalize()
        time = re.sub(r"\s+", " ", time.strip()).upper()

        key = (
            room.lower(),
            day.lower(),
            time.lower()
        )

        if key not in assignments:
            assignments[key] = {
                "room": room,
                "day": day,
                "time": time,
                "departments": [],
                "unnamed_count": 0
            }

        assignment = assignments[key]

        if department:
            department = department.strip().upper()

            if department not in assignment["departments"]:
                assignment["departments"].append(department)
        else:
            assignment["unnamed_count"] += count

    # Split the information into individual sentences.
    sentences = re.split(r"[.!?\n]+", schedule_data)

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Format 1:
        # CSE department has booked Computer Lab 1
        # on Monday at 10 AM.

        booking_pattern = re.compile(
            rf"\b(?P<department>[A-Z][A-Za-z0-9& -]*?)"
            rf"\s+department\s+"
            rf"(?:has|have)\s+"
            rf"(?:also\s+)?booked\s+"
            rf"(?P<room>.+?)\s+"
            rf"on\s+(?P<day>{DAYS})\s+"
            rf"at\s+(?P<time>\d{{1,2}}(?::\d{{2}})?\s*(?:am|pm))\b",
            re.IGNORECASE
        )

        match = booking_pattern.search(sentence)

        if match:
            add_assignment(
                room=match.group("room"),
                day=match.group("day"),
                time=match.group("time"),
                department=match.group("department")
            )
            continue

        # Format 2:
        # Two departments have booked Seminar Hall
        # on Tuesday at 2 PM.

        general_booking_pattern = re.compile(
            rf"\b(?P<count>two|2|multiple|several)"
            rf"\s+departments?\s+"
            rf"(?:have|has)\s+booked\s+"
            rf"(?P<room>.+?)\s+"
            rf"on\s+(?P<day>{DAYS})\s+"
            rf"at\s+(?P<time>\d{{1,2}}(?::\d{{2}})?\s*(?:am|pm))\b",
            re.IGNORECASE
        )

        match = general_booking_pattern.search(sentence)

        if match:
            count_text = match.group("count").lower()

            count = {
                "two": 2,
                "2": 2,
                "multiple": 2,
                "several": 2
            }.get(count_text, 2)

            add_assignment(
                room=match.group("room"),
                day=match.group("day"),
                time=match.group("time"),
                count=count
            )
            continue

        # Format 3:
        # CSE and ECE are assigned to Computer Lab 1
        # at 10 AM on Monday.

        assigned_pattern = re.compile(
            rf"\b(?P<departments>[A-Z][A-Za-z0-9& -]*?)"
            rf"\s+(?:students\s+)?"
            rf"(?:are\s+)?(?:also\s+)?assigned\s+(?:to\s+)?"
            rf"(?P<room>[\w][\w\s-]*?)\s+"
            rf"at\s+(?P<time>\d{{1,2}}(?::\d{{2}})?\s*(?:am|pm))"
            rf"\s+(?:on\s+)?"
            rf"(?P<day>{DAYS})\b",
            re.IGNORECASE
        )

        match = assigned_pattern.search(sentence)

        if match:

            departments = re.split(
                r"\s+and\s+",
                match.group("departments"),
                flags=re.IGNORECASE
            )

            for department in departments:
                add_assignment(
                    room=match.group("room"),
                    day=match.group("day"),
                    time=match.group("time"),
                    department=department
                )
                        # Format 4:
        # CSE and ECE classes are both scheduled in
        # Computer Lab 1 on Monday at 10 AM.

        scheduled_pattern = re.compile(
            rf"\b(?P<departments>[A-Z][A-Za-z0-9& -]*?)"
            rf"\s+classes?\s+"
            rf"(?:are\s+)?(?:both\s+)?scheduled\s+"
            rf"(?:in|at)\s+"
            rf"(?P<room>[\w][\w\s-]*?)\s+"
            rf"on\s+(?P<day>{DAYS})\s+"
            rf"at\s+(?P<time>\d{{1,2}}(?::\d{{2}})?\s*(?:am|pm))\b",
            re.IGNORECASE
        )

        match = scheduled_pattern.search(sentence)

        if match:
            departments = re.split(
                r"\s+and\s+",
                match.group("departments"),
                flags=re.IGNORECASE
            )

            for department in departments:
                add_assignment(
                    room=match.group("room"),
                    day=match.group("day"),
                    time=match.group("time"),
                    department=department
                )

    conflicts = []
    recommendations = []

    # Detect multiple bookings for the same room, day and time.
    for assignment in assignments.values():

        departments = assignment["departments"]
        total_bookings = len(departments) + assignment["unnamed_count"]

        if total_bookings < 2:
            continue

        if departments:
            department_names = " and ".join(departments)

            if assignment["unnamed_count"]:
                department_names += (
                    f" and {assignment['unnamed_count']} "
                    "additional unnamed booking(s)"
                )
        else:
            department_names = (
                f"{assignment['unnamed_count']} departments"
            )

        conflict = (
            f"{department_names} have overlapping bookings for "
            f"{assignment['room']} on "
            f"{assignment['day']} at {assignment['time']}."
        )

        conflicts.append(conflict)

        recommendations.append(
            f"Review the bookings for {assignment['room']} on "
            f"{assignment['day']} at {assignment['time']}. "
            "Reschedule one booking or assign another available room."
        )

    if conflicts:
        summary = (
            f"{len(conflicts)} scheduling conflict(s) detected."
        )
    else:
        summary = (
            "No confirmed scheduling conflict was identified "
            "from the supplied information."
        )

        recommendations.append(
            "Review room assignments, class timings, and availability "
            "before finalizing the timetable."
        )

    return {
        "agent": "Scheduling Agent",
        "status": "success",
        "summary": summary,
        "conflicts": conflicts,
        "recommendations": recommendations
    }
