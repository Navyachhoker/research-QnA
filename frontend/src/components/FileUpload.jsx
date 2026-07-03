// src/components/FileUpload.jsx

import { useRef, useState } from "react";

export default function FileUpload({
  onUpload,
  loading,
}) {
  const inputRef = useRef(null);

  const [dragging, setDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Please select a PDF file.");
      return;
    }

    onUpload(file);
  };

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFile(e.dataTransfer.files[0]);
      }}
      className={`
        border-2
        border-dashed
        rounded-xl
        p-12
        text-center
        cursor-pointer
        transition

        ${
          dragging
            ? "border-indigo-500 bg-indigo-50"
            : "border-gray-300 hover:border-indigo-400"
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) =>
          handleFile(e.target.files[0])
        }
      />

      {loading ? (
        <div>
          <p className="text-indigo-600 font-semibold">
            Uploading...
          </p>
        </div>
      ) : (
        <>
          <div className="text-5xl mb-4">
            📄
          </div>

          <h2 className="font-semibold text-lg">
            Drag & Drop PDF
          </h2>

          <p className="text-gray-500 mt-2">
            or click to browse
          </p>
        </>
      )}
    </div>
  );
}