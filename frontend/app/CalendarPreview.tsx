"use client";

interface CalendarEvent {
  title: string;
  days: string[];
  start_time: string;
  end_time: string;
  location: string;
  room: string;
}

export default function CalendarPreview({ previewData }: { previewData: any }) {
  const events: CalendarEvent[] = previewData.classes || [];

  if (!events.length) return <p>No events found.</p>;

  return (
    <div className="bg-white p-4 rounded-xl shadow-md mt-6 max-h-80 overflow-y-auto">
      <h2 className="text-lg font-bold mb-2 text-center text-red-800">Preview of Your Schedule</h2>
      {events.map((e, i) => (
        <div key={i} className="mb-2 p-2 border-b last:border-b-0">
          <p className="font-semibold text-red-800">{e.title}</p>
          <p className="text-sm text-gray-600">
            {e.days.join(", ")} | {e.start_time} - {e.end_time}
          </p>
          <p className="text-sm text-gray-600">{e.location} Room {e.room}</p>
        </div>
      ))}
    </div>
  );
}
