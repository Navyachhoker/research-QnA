// src/pages/AnalyzePage.jsx

import { useEffect, useState } from "react";

import ReactMarkdown from "react-markdown";

import {

  listPapers,

  summarizePaper,

  comparePapers,

  generateRelatedWork,

} from "../api/client";

export default function AnalyzePage() {

  const [papers, setPapers] =
    useState([]);

  const [mode, setMode] =
    useState("summary");

  const [paper1, setPaper1] =
    useState("");

  const [paper2, setPaper2] =
    useState("");

  const [topic, setTopic] =
    useState("");

  const [output, setOutput] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {

    async function load() {

      const { data } =
        await listPapers();

      setPapers(data.papers);

    }

    load();

  }, []);

  async function handleRun() {

    try {

      setLoading(true);

      if (mode === "summary") {

        const { data } =
          await summarizePaper(
            paper1
          );

        setOutput(data.summary);

      }

      else if (mode === "compare") {

        const { data } =
          await comparePapers(
            paper1,
            paper2
          );

        setOutput(
          data.comparison
        );

      }

      else {

        const { data } =
          await generateRelatedWork(
            topic
          );

        setOutput(
          data.related_work
        );

      }

    }

    finally {

      setLoading(false);

    }

  }

  return (

    <div className="max-w-5xl mx-auto">

      <h1 className="text-3xl font-bold mb-8">

        Paper Analysis

      </h1>

      <div className="flex gap-3 mb-6">

        <button
          onClick={() =>
            setMode("summary")
          }
          className="bg-indigo-600 text-white px-4 py-2 rounded"
        >

          Summary

        </button>

        <button
          onClick={() =>
            setMode("compare")
          }
          className="bg-indigo-600 text-white px-4 py-2 rounded"
        >

          Compare

        </button>

        <button
          onClick={() =>
            setMode("related")
          }
          className="bg-indigo-600 text-white px-4 py-2 rounded"
        >

          Related Work

        </button>

      </div>

      {mode === "summary" && (

        <select
          value={paper1}
          onChange={(e) =>
            setPaper1(e.target.value)
          }
          className="border rounded p-3 mb-5"
        >

          <option value="">
            Select Paper
          </option>

          {papers.map((paper) => (

            <option
              key={paper}
              value={paper}
            >

              {paper}

            </option>

          ))}

        </select>

      )}

      {mode === "compare" && (

        <div className="grid grid-cols-2 gap-4 mb-5">

          <select
            value={paper1}
            onChange={(e) =>
              setPaper1(e.target.value)
            }
            className="border rounded p-3"
          >

            <option value="">
              Paper A
            </option>

            {papers.map((paper) => (

              <option
                key={paper}
                value={paper}
              >

                {paper}

              </option>

            ))}

          </select>

          <select
            value={paper2}
            onChange={(e) =>
              setPaper2(e.target.value)
            }
            className="border rounded p-3"
          >

            <option value="">
              Paper B
            </option>

            {papers.map((paper) => (

              <option
                key={paper}
                value={paper}
              >

                {paper}

              </option>

            ))}

          </select>

        </div>

      )}

      {mode === "related" && (

        <input
          className="border rounded p-3 w-full mb-5"
          placeholder="Enter topic..."
          value={topic}
          onChange={(e) =>
            setTopic(e.target.value)
          }
        />

      )}

      <button
        onClick={handleRun}
        className="bg-green-600 text-white px-6 py-3 rounded"
      >

        {loading ? "Running..." : "Generate"}

      </button>

      {output && (

        <div className="mt-8 bg-white border rounded-xl p-6 prose max-w-none">

          <ReactMarkdown>

            {output}

          </ReactMarkdown>

        </div>

      )}

    </div>

  );

}