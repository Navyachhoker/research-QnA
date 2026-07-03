// src/pages/PapersPage.jsx

import {
  useEffect,
  useState,
} from "react";

import {
  listPapers,
} from "../api/client";

export default function PapersPage() {

  const [papers, setPapers] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {

    const fetchPapers = async () => {

      try {

        const { data } =
          await listPapers();

        setPapers(data.papers);

      } finally {

        setLoading(false);

      }

    };

    fetchPapers();

  }, []);

  if (loading) {
    return (
      <h2 className="text-center text-gray-500">
        Loading...
      </h2>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">

      <h1 className="text-3xl font-bold mb-2">
        Ingested Papers
      </h1>

      <p className="text-gray-500 mb-8">
        Papers currently available in the knowledge base.
      </p>

      {papers.length === 0 ? (

        <div className="bg-white rounded-xl p-10 text-center shadow">

          <div className="text-5xl">
            📭
          </div>

          <p className="mt-4 text-gray-500">
            No papers uploaded yet.
          </p>

        </div>

      ) : (

        <div className="space-y-4">

          {papers.map((paper) => (

            <div
              key={paper}
              className="bg-white shadow rounded-xl p-4 flex items-center gap-4"
            >

              <div className="text-3xl">
                📄
              </div>

              <div>

                <h2 className="font-semibold">
                  {paper}
                </h2>

              </div>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}