import re

# expand the madison weekday abbreviations
day_map = {"M": "MO", "T": "TU", "W": "WE", "R": "TH", "F": "FR", "TR": ["TU", "TH"]}

# function to return list of day(s)
def expand_days(days_str: str):
    days_str = days_str.strip()
    if days_str in day_map:
        return day_map[days_str] if isinstance(day_map[days_str], list) else [day_map[days_str]]
    return list(days_str)

# function that parses the text into necessary info
def parse_schedule(text: str):
    classes, exams = [], []

    # break down the lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    current_course = None
    in_exams = False

    print("=== RAW LINES ===")

    for line in lines:
        print(repr(line))

        # detect course
        if re.match(r"^[A-Z][A-Z &]+ \d+:", line):
            current_course = line
            in_exams = False
            continue

        # detect exam section
        if line.lower().startswith("exams"):
            in_exams = True
            continue

        if not in_exams and re.match(r"^(LEC|DIS|SEM|LAB)", line):
            match = re.match(
                r"^(LEC|DIS|SEM|LAB)\s+(\d+)\s+([A-Za-z]+)\s+(\d{1,2}:\d{2}\s*[APMapm]+)\s*-\s*(\d{1,2}:\d{2}\s*[APMapm]+)\s+(.+?)\s+Room\s+([A-Za-z0-9]+)$",
                line
            )
            # match the class info
            if match:
                section_type = match.group(1)
                section_number = match.group(2)
                days_str = match.group(3)
                start_time = match.group(4)
                end_time = match.group(5)
                building = match.group(6)
                room = match.group(7)

                # add to class info
                classes.append({
                    "course": current_course,
                    "section_type": section_type,
                    "section_number": section_number,
                    "days": expand_days(days_str),
                    "start_time": start_time,
                    "end_time": end_time,
                    "location": building,
                    "room": room
                })
            else:
                print("Did not match class line:", line)

        # match the exam info
        elif in_exams:
            if line.lower().startswith("none"):
                exams.append({"course": current_course, "date": None, "start_time": None, "end_time": None, "location": None})
                continue

            match = re.match(
                r"^([A-Za-z]+ \d{1,2}),\s+(\d{1,2}:\d{2}\s*[APMpm]+)\s*-\s*(\d{1,2}:\d{2}\s*[APMpm]+)(?:\s*-\s*(.*))?$",
                line
            )
            if match:
                exams.append({
                    "course": current_course,
                    "date": match.group(1),
                    "start_time": match.group(2),
                    "end_time": match.group(3),
                    "location": match.group(4) or "Location not specified"
                })
            else:
                print("Did not match exam line:", line)
    print("=================")

    return {"classes": classes, "exams": exams}


if __name__ == "__main__":
    sample_input = """
STAT 453: Introduction to Deep Learning and Generative Models
Weekly Meetings
LEC 001 MW 8:00 AM - 9:15 AM MORGRIDGE Room 1524
.
Exams
December 17, 5:05 PM - 7:05 PM - Location not specified
"""
    result = parse_schedule(sample_input)
    from pprint import pprint
    pprint(result)