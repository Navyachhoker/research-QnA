// src/pages/AskPage.jsx

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

import {
  askQuestion,
  listPapers,
} from "../api/client";

import SourceCard from "../components/SourceCard";

export default function AskPage() {

  const [papers, setPapers] = useState([]);

  const [selectedPaper, setSelectedPaper] =
    useState("");

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [sources, setSources] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {

    async function loadPapers() {

      const { data } =
        await listPapers();

      setPapers(data.papers);

    }

    loadPapers();

  }, []);

  async function handleAsk() {

    if (!question.trim()) return;

    try {

      setLoading(true);

      const { data } =
        await askQuestion(
          question,
          selectedPaper || null
        );

      setAnswer(data.answer);

      setSources(data.sources);

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="max-w-4xl mx-auto">

      <h1 className="text-3xl font-bold mb-6">

        Ask Questions

      </h1>

      <select
        value={selectedPaper}
        onChange={(e) =>
          setSelectedPaper(e.target.value)
        }
        className="border rounded-lg px-3 py-2 mb-5"
      >

        <option value="">

          All Papers

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

      <div className="flex gap-3">

        <input
          className="flex-1 border rounded-lg px-4 py-3"
          placeholder="Ask anything..."
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
        />

        <button
          onClick={handleAsk}
          disabled={loading}
          className="bg-indigo-600 text-white px-6 rounded-lg"
        >

          {loading ? "Thinking..." : "Ask"}

        </button>

      </div>

      {answer && (

        <div className="mt-8">

          <div className="bg-white border rounded-xl p-6 prose max-w-none">

            <ReactMarkdown>

              {answer}

            </ReactMarkdown>

          </div>

          {sources.length > 0 && (

            <div className="space-y-4 mt-6">

              <h3 className="font-semibold">

                Sources

              </h3>

              {sources.map((source) => (

                <SourceCard
                  key={source.source_num}
                  source={source}
                />

              ))}

            </div>

          )}

        </div>

      )}

    </div>

  );

}