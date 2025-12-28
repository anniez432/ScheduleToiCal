"use client";

import { useState } from "react";
import Image from "next/image";
import CalendarPreview from "./CalendarPreview";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null); // store classes/exams
  const [downloadUrl, setDownloadUrl] = useState<string>("");

  const upload = async () => {
    if (!file) {
      setStatus("Please choose an image to upload.");
      return;
    }
    
    setLoading(true);
    setStatus("Processing...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        /*
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "schedule.ics";
        a.click();

        setStatus("Calendar downloaded successfully!");
        */
        const data = await response.json();

        // Set preview for the UI
        setPreviewData({ classes: data.classes, exams: data.exams });
        setStatus("Preview loaded!");

        // Convert base64 ICS to downloadable blob
        const icsBlob = new Blob([Uint8Array.from(atob(data.ics_base64), c => c.charCodeAt(0))], {
          type: "text/calendar",
        });
        const url = window.URL.createObjectURL(icsBlob);
        setDownloadUrl(url);


      } else {
        setStatus("Failed to process.");
      }
    } catch (error) {
      console.error(error);
      setStatus("An error occurred during upload.");
    }
    finally{
      setLoading(false);
    }
  };

  return (
    <main className = "min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-red-800 p-8 rounded-xl shadow-md w-[420px]">
        <h1 className="text-2xl font-bold mb-4 text-center text-white/92">
          UW-Madison Schedule to iCal Converter
        </h1>

        <Image
          src="/example.png"
          alt="Example schedule screenshot"
          width={400}
          height={300}
          className="rounded-lg border mb-4"
          style={{opacity: 0.94}}
        />

        <p className="text-sm text-white/92 text-center mb-4 underline">
          Upload a screenshot like this (easiest on a laptop)
        </p>

        <p className="text-sm text-white/92 text-center mb-4">
          UW portal &rarr; Course Schedule &rarr; Zoom out to capture full schedule
        </p>

        <label
          htmlFor="file-upload"
          className="cursor-pointer bg-white/95 hover:bg-white/90 transition
                    border-2 border-dashed border-white
                    rounded-xl p-6 mb-4 flex flex-col items-center text-red-800"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-10 w-10 mb-2"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1 M12 12v5 M8 12l4-4 4 4 M12 3"
            />
          </svg>

          <span className="font-semibold">
            {file ? "Change image" : "Choose schedule image"}
          </span>

          {file && (
            <span className="text-xs mt-1 text-red-700">
              {file.name}
            </span>
          )}
        </label>

        <input
          id="file-upload"
          type="file"
          accept="image/*"
          onChange ={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          className="hidden"
        />

        <button
          onClick={upload}
          disabled={loading}
          className="w-full bg-white/95 text-red-800 font-semibold py-2 rounded-lg
                    hover:bg-red-100 disabled:opacity-50"
        >
          {loading ? "Processing…" : "Generate iCal"}
        </button>

        <p className = "mt-4 text-center text-white">{status}</p>
      

        {previewData && <CalendarPreview previewData={previewData} />}

        {downloadUrl && (
          <a
            href={downloadUrl}
            download="schedule.ics"
            className="block mt-4 text-center font-semibold text-red-800 bg-white/95 py-2 rounded-lg hover:bg-red-100"
          >
            Download / Add to Calendar
          </a>
        )}

      </div>
    </main>
  );
}