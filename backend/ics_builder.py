from icalendar import Calendar, Event, Alarm, vDuration
from datetime import datetime, date, time, timedelta
import pytz, uuid

timezone = pytz.timezone("America/Chicago")

building_address_map = {
    "Van Vleck": "Van Vleck, 480 Lincoln Dr, Madison, WI 53706",
    "Sterling": "Sterling Hall, 475 N Charter St, Madison, WI 53706",
    "Biochemistry Building": "Biochemistry Building, 420 Henry Mall, Madison, WI 53706",
    "Engineering Hall": "Engineering Hall, 1415 Engineering Dr, Madison, WI 53706",
    "Chemistry": "Chemistry, 1101 University Ave, Madison, WI 53706",
    "Helen C. White Hall": "Helen C. White Hall, 600 N Park St, Madison, WI 53706",
    "Morgridge Hall": "Morgridge Hall, 1205 University Ave, Madison, WI 53706",
    "Genetics-Biotechnology Center Building": "Genetics Building, 425 Henry Mall, Madison, WI 53706",
    "Van Hise Hall": "Van Hise, 1220 Linden Dr, Madison, WI 53706",
    "Noland Hall": "Noland Hall, 223 N Charter St, Madison, WI 53706",
    "Grainger Hall": "Grainger Hall, 975 University Ave, Madison, WI 53706"
}


def str_to_time(s):
    return datetime.strptime(s.strip().upper(), "%I:%M %p").time()

# convert to .ics calendar
def build_ics(parsed, term_start, term_end):
    cal = Calendar()
    cal.add("prodid", "-//ScheduleToiCal//example.com//")
    cal.add("version", "2.0")

    # add the classes
    for classEvent in parsed["classes"]:
        event = Event()

        event.add("summary", classEvent["title"])

        building = normalize_building(classEvent["location"])
        location = building_address_map.get(building, classEvent["location"])  # fallback: use building name
        event.add("location", location)
    
        first_day = first_class_date(term_start, classEvent["days"])

        dtstart = timezone.localize(datetime.combine(first_day, str_to_time(classEvent["start_time"])))
        dtend = timezone.localize(datetime.combine(first_day, str_to_time(classEvent["end_time"])))

    
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)

        event.add("rrule", {
            "FREQ": "WEEKLY",
            "BYDAY": classEvent["days"],  # keep as list, e.g. ["TU", "TH"]
            "UNTIL": timezone.localize(datetime.combine(term_end, time(23,59))).astimezone(pytz.UTC)
        })
        event.add("uid", str(uuid.uuid4()))



        alarm = Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Leave now')
        alarm.add('TRIGGER', vDuration(timedelta(minutes=-15)))
        alarm['TRIGGER'].params['RELATED'] = 'START'
        event.add_component(alarm)

        event.add("X-APPLE-TRAVEL-ADVISORY-BEHAVIOR", "AUTOMATIC")
        event.add("X-APPLE-TRAVEL-TIME", "15")  # or your travel estimate

        cal.add_component(event)
        print(event.to_ical().decode())


    for exam in parsed["exams"]:
        if not exam.get("month") or not exam.get("day") or not exam.get("start_time"):
            continue


        event = Event()

        event.add("summary", f"{exam['course']} Exam")
        event.add("location", exam.get("location", "Location not specified"))

        exam_year = term_end.year

        dtstart = timezone.localize(datetime.strptime(f"{exam['month']} {exam['day']} {exam_year} {exam['start_time']}", "%B %d %Y %I:%M %p"))
        dtend = timezone.localize(datetime.strptime(f"{exam['month']} {exam['day']} {exam_year} {exam['end_time']}", "%B %d %Y %I:%M %p"))

        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        event.add("uid", str(uuid.uuid4()))

        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "Leave for exam")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)
        cal.add_component(event)

    return cal.to_ical()

weekday_map = {
    "MO": 0,
    "TU": 1,
    "WE": 2,
    "TH": 3,
    "FR": 4
}

def first_class_date(term_start, days):
    start = term_start
    valid_days = {weekday_map[d] for d in days}
    while start.weekday() not in valid_days:
        start += timedelta(days=1)
    return start

def normalize_building(building:str) -> str:
    return building.split(" Room ")[0].strip()
