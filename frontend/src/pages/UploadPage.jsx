// src/pages/UploadPage.jsx

import { useState } from "react";

import FileUpload from "../components/FileUpload";

import { uploadPaper } from "../api/client";

export default function UploadPage() {
  const [loading, setLoading] =
    useState(false);

  const [uploaded, setUploaded] =
    useState([]);

  const [error, setError] =
    useState("");

  const handleUpload = async (file) => {
    try {
      setLoading(true);
      setError("");

      const { data } =
        await uploadPaper(file);

      setUploaded((prev) => [
        data,
        ...prev,
      ]);
    } catch (err) {
      setError(
        err.response?.data?.detail ??
          "Upload failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">

      <h1 className="text-3xl font-bold mb-2">
        Upload Research Papers
      </h1>

      <p className="text-gray-500 mb-8">
        Upload PDFs to your knowledge base.
      </p>

      <FileUpload
        onUpload={handleUpload}
        loading={loading}
      />

      {error && (
        <p className="text-red-500 mt-4">
          {error}
        </p>
      )}

      {uploaded.length > 0 && (
        <div className="mt-10">

          <h2 className="font-semibold mb-4">
            Uploaded Papers
          </h2>

          <div className="space-y-3">

            {uploaded.map((paper, index) => (
              <div
                key={index}
                className="bg-green-50 border border-green-300 rounded-lg p-4 flex justify-between items-center"
              >
                <div>

                  <p className="font-semibold">
                    {paper.paper_name}
                  </p>

                  <p className="text-sm text-gray-500">
                    {paper.chunk_count} chunks stored
                  </p>

                </div>

                <span className="text-green-600 text-xl">
                  ✓
                </span>

              </div>
            ))}

          </div>

        </div>
      )}

    </div>
  );
}