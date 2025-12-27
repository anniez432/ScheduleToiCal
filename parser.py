import re

# expand the madison weekday abbreviations
day_map = {
    "M": "MO",
    "T": "TU",
    "W": "WE",
    "R": "TH",
    "F": "FR",
    "TR": ["TU", "TH"],
    "MWF": ["MO", "WE", "FR"],
    "WF": ["WE", "FR"],
    "MW": ["MO", "WE"],
    "MR": ["MO", "TH"],
}
class_pattern = re.compile(
    r"^(?:[*•«¢+\-]\s*)?"                        # optional bullet/symbol
    r"(LEC|DIS|SEM|LAB)\s+(\d+)\s+"           # section type + number
    r"([MTWRF\s,]+)\s+"                          # days (like MWF, TR, MW, etc.)
    r"(\d{1,2}:\d{2}\s*[APMapm]+)\s*-\s*"     # start time
    r"(\d{1,2}:\d{2}\s*[APMapm]+)\s+"         # end time
    r"(.+?)\s+Room\s+([\w-]+)[.,]?$"               # building + room
)

def normalize_course_name(raw_course):
    """
    Convert things like 'B M 576' or 'B M1576' into 'BM 1576'
    """
    # remove spaces inside letters, but keep digits separate
    match = re.match(r"([A-Z](?:\s?[A-Z])*)\s*(\d+)", raw_course.replace(" ", ""))
    if match:
        dept = match.group(1)
        number = match.group(2)
        return f"{dept} {number}"
    return raw_course



# function to return list of day(s)
def expand_days(days_str: str):
    days_str = days_str.strip().replace(",","")
    if days_str in day_map:
        return day_map[days_str] if isinstance(day_map[days_str], list) else [day_map[days_str]]
    
    result = []
    for char in days_str:
        if char in day_map:
            mapped = day_map[char]
            result.append(mapped if isinstance(mapped, str) else mapped[0])
        else:
            raise ValueError(f"Expected weekday abbreviation, got: {char}")
        
    return result

# function that parses the text into necessary info
def parse_schedule(text: str):
    classes, exams = [], []
    current_course = None
    shortened_course = None


    # break down the lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    current_course = None
    in_exams = False

    print("=== RAW LINES ===")

    for line in lines:
        line = line.strip()
        line = re.sub(r"\s+", " ", line)
        line = line.replace("\u200b", "")
        
        if "ONLINE" in line.upper():
            continue
        print(repr(line))

        course_pattern = re.compile(r"^([A-Z\s]+?)(\d+):")

        if course_pattern.match(line):
            current_course = line
            shortened_course = normalize_course_name(line.split(":")[0].strip())
            in_exams = False
            continue


        # detect exam section
        if line.lower().startswith("exams"):
            in_exams = True
            continue

        if not in_exams and re.match(r"^(?:[*•«¢+\-]\s*)?(LEC|DIS|SEM|LAB)", line):


            match = class_pattern.match(line)
            # match the class info
            if match:
                section_type = match.group(1)
                section_number = match.group(2)
                days_str = days_str = match.group(3).replace(" ", "").replace(",", "")
                start_time = match.group(4)
                end_time = match.group(5)
                building = match.group(6).strip()
                room = match.group(7)

                # add to class info
                classes.append({
            "course": shortened_course or current_course,
            "section_type": section_type,
            "section_number": section_number,
            "days": expand_days(days_str),
            "start_time": start_time,
            "end_time": end_time,
            "title": f"{shortened_course} {section_type} {section_number} (Room {room})",  # <-- goes in summary/title
            "location": building,  # <-- goes in ICS location field
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
                r"^[*•\s]*([A-Za-z]+ \d{1,2}),\s+(\d{1,2}:\d{2}\s*[APMpm]+)\s*-\s*(\d{1,2}:\d{2}\s*[APMpm]+)(?:\s*-\s*(.*))?$",
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