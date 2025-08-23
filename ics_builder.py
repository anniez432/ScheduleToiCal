from icalendar import Calendar, Event
from datetime import datetime, date, time
import pytz, uuid

timezone = pytz.timezone("America/Chicago")

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
        event.add("summary", classEvent["course"] + classEvent["room"])
        event.add("location", classEvent["location"])
    
        dtstart = timezone.localize(datetime.combine(term_start, str_to_time(classEvent["start_time"])))
        dtend = timezone.localize(datetime.combine(term_start, str_to_time(classEvent["end_time"])))
    
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        event.add("rrule", {
            "FREQ": "WEEKLY",
            "BYDAY": ",".join(classEvent["days"]),
            "UNTIL": timezone.localize(datetime.combine(term_end, time(23,59))).astimezone(pytz.UTC)
        })
        event.add("uid", str(uuid.uuid4()))

        cal.add_component(event)

    for exam in parsed["exams"]:
        event = Event()
        event.add("summary", f"{exam['course']} Exam")
        event.add("location", exam["location"])

        exam_date = datetime.strptime(exam["date"] + " " + exam["start_time"], "%B %d %I:%M %p")
        dtstart = timezone.localize(exam_date)
        dtend = timezone.localize(datetime.strptime(exam["date"] + " " + exam["end_time"], "%B %d %I:%M %p"))

        event.add("dtstart", dtstart)
        event.add("dtend", dtend)
        event.add("uid", str(uuid.uuid4()))

        cal.add_component(event)

    return cal.to_ical()