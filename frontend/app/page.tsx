"use client";

import { useState } from "react";
import Image from "next/image";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(false);

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
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "schedule.ics";
        a.click();

        setStatus("Calendar downloaded successfully!");
      } else {
        setStatus("Failed to process.");
      }
    } catch (error) {
      setStatus("An error occurred during upload.");
    }
  };

  return (
    <main className = "min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-blue-600 p-8 rounded-xl shadow-md w-[420px]">
        <h1 className="text-2xl font-bold mb-4 text-center">
          UW-Madison Schedule to iCal Converter
        </h1>

        <Image
          src="/example.png"
          alt="Example schedule screenshot"
          width={400}
          height={300}
          className="rounded-lg border mb-4"
        />

        <p className="text-sm text-white text-center mb-4">
          Upload a screenshot like this. How to: UW portal - Course Schedule - Zoom out to capture full schedule
        </p>

        <label
          htmlFor="file-upload"
          className="cursor-pointer bg-white/90 hover:bg-white transition
                    border-2 border-dashed border-white
                    rounded-xl p-6 mb-4 flex flex-col items-center text-blue-700"
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
            <span className="text-xs mt-1 text-blue-600">
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
          className="w-full bg-white text-blue-700 font-semibold py-2 rounded-lg
                    hover:bg-blue-100 disabled:opacity-50"
        >
          {loading ? "Processing…" : "Generate iCal"}
        </button>

        <p className = "mt-4 text-center text-white">{status}</p>
      </div>
    </main>
  );
}