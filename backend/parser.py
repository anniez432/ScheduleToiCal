# contains functions that are used to parse the schedule
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
    r"(LEC|DIS|SEM|LAB)\s+(\d+)\s+"
    r"([MTWRF]+)\s+"
    r"(\d{1,2}:\d{2}\s*[APMapm]+)\s*-\s*"
    r"(\d{1,2}:\d{2}\s*[APMapm]+)\s+"
    r"(.+?)\s+Room\s+([\w\d]+)[.,]?$",
    re.IGNORECASE
)

room_pattern = re.compile(r"Room\s+([\w-]+)", re.IGNORECASE)

exam_pattern = re.compile(
    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(\d{1,2}),\s+"
    r"(\d{1,2}:\d{2}\s*[APMapm]+)\s*[-–]\s*"
    r"(\d{1,2}:\d{2}\s*[APMapm]+)"
    r"(?:\s*[-–]\s*(.*))?$",
    re.IGNORECASE
)

course_pattern = re.compile(r"^([A-Z\s]+)(\d+):")

def normalize_course_name(raw: str) -> str:
    """
    Convert things like 'B M 576' or 'B M1576' into 'BM 1576'
    """
    # remove spaces inside letters, but keep digits separate
    raw = raw.replace(" ", ""   )
    match = re.match(r"([A-Z]+)(\d+)", raw)
    return f"{match.group(1)} {match.group(2)}" if match else raw



# function to return list of day(s)
def expand_days(days):
    if isinstance(days, list):
        return days
    
    days = days.replace(",","").strip()

    if days in day_map:
        return day_map[days] if isinstance(day_map[days], list) else [day_map[days]]
    
    result = []
    for char in days:
        if char in day_map:
            mapped = day_map[char]
            result.append(mapped if isinstance(mapped, str) else mapped[0])
        else:
            raise ValueError(f"Expected weekday abbreviation, got: {char}")
        
    return result

def clean_line(line: str) -> str:
    line = line.replace("\u200b", "")
    line = re.sub(r"^[^A-Z]*(?=[A-Z])", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip()


# function that parses the text into necessary info
def parse_schedule(text: str):
    classes, exams = [], []
    current_course = None
    shortened_course = None
    in_exams = False


    # break down the lines
    lines = [clean_line(l) for l in text.splitlines() if l.strip()]

    print("=== RAW LINES ===")
    for l in lines:
        print(repr(l))
    print("=================")

    for i, line in enumerate(lines):
        # skil online classes
        if "ONLINE" in line.upper():
            continue

        course_match = course_pattern.match(line)
        if course_match:
            current_course = line
            shortened_course = normalize_course_name(course_match.group(1) + course_match.group(2))
            in_exams = False
            continue


        # detect exam section
        if line.lower().startswith("exams"):
            in_exams = True
            continue

        if not in_exams:
            class_match = class_pattern.match(line)

            # match the class info
            if class_match:
                section_type = class_match.group(1)
                section_number = class_match.group(2)
                days = expand_days(class_match.group(3))
                start_time = class_match.group(4)
                end_time = class_match.group(5)
                building = class_match.group(6).strip()
                room = class_match.group(7)

                """
                room = None
                if i + 1 < len(lines):
                    room_match = room_pattern.search(lines[i + 1])
                    if room_match:
                        room = room_match.group(1) #TODO: STRIP?
                """

                # add to class info
                classes.append({
                    "course": shortened_course or current_course,
                    "section_type": section_type,
                    "section_number": section_number,
                    "days": expand_days(days),
                    "start_time": start_time,
                    "end_time": end_time,
                    "title": f"{shortened_course} {section_type} {section_number}" + (f" (Room {room})" if room else ""),  # <-- goes in summary/title
                    "location": building,  # <-- goes in ICS location field
                    "room": room
                })
            else:
                print("Did not match class line:", line)

        # match the exam info
        if in_exams:
            exam_match = exam_pattern.search(line)
            if exam_match:
                exams.append({
                    "course": shortened_course or current_course,
                    "month": exam_match.group(1),
                    "day": exam_match.group(2),
                    "start_time": exam_match.group(3),
                    "end_time": exam_match.group(4),
                    "location": exam_match.group(5) or "Location not specified"
                })
            else:
                print("Did not match exam line:", line)

    return {"classes": classes, "exams": exams}


