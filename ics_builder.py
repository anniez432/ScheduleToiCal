from icalendar import Calendar, Event, Alarm
from datetime import datetime, date, time, timedelta
import pytz, uuid

timezone = pytz.timezone("America/Chicago")

building_address_map = {
    "Van Vleck": "480 Lincoln Dr, Madison, WI 53706",
    "Sterling": "475 N Charter St, Madison, WI 53706",
    "Biochemistry Building": "420 Henry Mall, Madison, WI 53706",
    # add more as needed
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

        summary = f"{classEvent['course']} (Room {classEvent['room']})"
        event.add("summary", summary)

        building = classEvent["location"]
        address = building_address_map.get(building, building)  # fallback: use building name
        event.add("location", address)
    
        dtstart = timezone.localize(datetime.combine(term_start, str_to_time(classEvent["start_time"])))
        dtend = timezone.localize(datetime.combine(term_start, str_to_time(classEvent["end_time"])))
    
        event.add("dtstart", dtstart)
        event.add("dtend", dtend)

        event.add("rrule", {
            "FREQ": "WEEKLY",
            "BYDAY": classEvent["days"],  # keep as list, e.g. ["TU", "TH"]
            "UNTIL": timezone.localize(datetime.combine(term_end, time(23,59))).astimezone(pytz.UTC)
        })
        event.add("uid", str(uuid.uuid4()))
        
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "Leave now")
        alarm.add("trigger", timedelta(minutes=-15))  # 15 minutes before event
        event.add_component(alarm)

        cal.add_component(event)

    for exam in parsed["exams"]:
        event = Event()

        event.add("summary", f"{exam['course']} Exam")
        event.add("location", exam.get("location"), "")

        dtstart = timezone.localize(datetime.strptime(f"{exam['date']} {exam['start_time']}", "%B %d %I:%M %p"))
        dtend = timezone.localize(datetime.strptime(f"{exam['date']} {exam['end_time']}", "%B %d %I:%M %p"))

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