"use client";

import { useState } from "react";

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

        <input
          type="file"
          accept="image/*"
          onChange ={(e) => setFile(e.target.files ? e.target.files[0] : null)}
          className="mb-4 w-full"
        />

        <button
          onClick={upload}
          className="w-full bg-white text-blue-600 py-2 rounded-lg hover:bg-blue-700 hover:text-white transition disabled:opacity-50"
          disabled={loading}
        >
          Generate iCal
        </button>

        <p className = "mt-4 text-center text-white">{status}</p>
      </div>
    </main>
  );
}