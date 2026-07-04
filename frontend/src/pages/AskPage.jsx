// src/pages/AskPage.jsx

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

import {
  askQuestion,
  listPapers,
  listSessions,
  createSession,
  getHistory,
  deleteSession,
} from "../api/client";

import SourceCard from "../components/SourceCard";

export default function AskPage() {
  const [papers, setPapers] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActive] = useState(null);
  const [history, setHistory] = useState([]);
  const [paper, setPaper] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [newName, setNewName] = useState("");

  const bottomRef = useRef();

  useEffect(() => {
    listPapers().then(({ data }) => setPapers(data.papers));
    fetchSessions();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [history]);

  const fetchSessions = async () => {
    const { data } = await listSessions();
    setSessions(data);
  };

  const handleCreateSession = async () => {
    const name = newName.trim() || `Session ${Date.now()}`;

    const { data } = await createSession(name);

    setNewName("");

    await fetchSessions();

    selectSession(data);
  };

  const selectSession = async (session) => {
    setActive(session);

    setHistory([]);

    const { data } = await getHistory(session.id);

    setHistory(
      data.turns.map((turn) => ({
        question: turn.question,
        answer: turn.answer,
        sources: [],
      }))
    );
  };

  const handleDelete = async (sessionId) => {
    await deleteSession(sessionId);

    if (activeSession?.id === sessionId) {
      setActive(null);
      setHistory([]);
    }

    await fetchSessions();
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");

    const q = question;

    setQuestion("");

    try {
      const { data } = await askQuestion(
        q,
        paper || null,
        5,
        activeSession?.id ?? null
      );

      setHistory((prev) => [
        ...prev,
        {
          question: q,
          answer: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (e) {
      setError(
        e.response?.data?.detail ||
          "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)]">

      {/* Sidebar */}

      <div className="w-64 bg-white border-r border-gray-200 flex flex-col p-4 gap-3">

        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
          Sessions
        </p>

        <div className="flex gap-1">

          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && handleCreateSession()
            }
            placeholder="New session..."
            className="flex-1 text-xs border border-gray-300 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-400"
          />

          <button
            onClick={handleCreateSession}
            className="text-xs bg-indigo-600 text-white px-2 py-1.5 rounded-lg hover:bg-indigo-700"
          >
            +
          </button>

        </div>

        <div className="flex-1 overflow-y-auto space-y-1">

          {sessions.length === 0 && (
            <p className="text-xs text-gray-400 text-center mt-4">
              No sessions yet.
            </p>
          )}

          {sessions.map((session) => (

            <div
              key={session.id}
              onClick={() => selectSession(session)}
              className={`flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer group transition-colors ${
                activeSession?.id === session.id
                  ? "bg-indigo-50 text-indigo-700"
                  : "hover:bg-gray-100 text-gray-700"
              }`}
            >

              <span className="text-xs font-medium truncate">
                {session.name}
              </span>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(session.id);
                }}
                className="text-gray-300 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity ml-1"
              >
                ✕
              </button>

            </div>

          ))}

        </div>

      </div>

      {/* Chat Area */}

      <div className="flex-1 flex flex-col px-6 py-6 max-w-3xl mx-auto w-full">

        <div className="flex items-center justify-between mb-4">

          <h1 className="text-lg font-bold text-gray-800">

            {activeSession
              ? activeSession.name
              : "Select or create a session"}

          </h1>

          <select
            value={paper}
            onChange={(e) => setPaper(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >

            <option value="">
              All Papers
            </option>

            {papers.map((paperName) => (

              <option
                key={paperName}
                value={paperName}
              >
                {paperName}
              </option>

            ))}

          </select>

        </div>

        <div className="flex-1 overflow-y-auto space-y-6 mb-4">

          {!activeSession && (

            <div className="text-center py-20 text-gray-400">

              <p className="text-4xl mb-3">
                💬
              </p>

              <p>
                Create or select a session to start chatting.
              </p>

            </div>

          )}

          {history.map((item, index) => (

            <div
              key={index}
              className="space-y-3"
            >

              <div className="flex justify-end">

                <div className="bg-indigo-600 text-white rounded-2xl rounded-br-sm px-4 py-2.5 max-w-xl text-sm">

                  {item.question}

                </div>

              </div>

              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-5 py-4 text-sm text-gray-800 prose prose-sm">

                <ReactMarkdown>
                  {item.answer}
                </ReactMarkdown>

              </div>

              {item.sources?.length > 0 && (

                <div className="space-y-2 pl-2">

                  <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
                    Sources
                  </p>

                  {item.sources.map((source) => (

                    <SourceCard
                      key={source.source_num}
                      source={source}
                    />

                  ))}

                </div>

              )}

            </div>

          ))}

          {loading && (

            <div className="flex items-center gap-2 text-gray-400 text-sm">

              <span className="animate-spin">
                ⏳
              </span>

              Thinking...

            </div>

          )}

          <div ref={bottomRef} />

        </div>

        {error && (
          <p className="text-red-500 text-sm mb-2">
            {error}
          </p>
        )}

        <div className="flex gap-2">

          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" &&
              !loading &&
              handleAsk()
            }
            disabled={!activeSession}
            placeholder={
              activeSession
                ? "Ask a question..."
                : "Select a session first"
            }
            className="flex-1 border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-gray-50 disabled:text-gray-400"
          />

          <button
            onClick={handleAsk}
            disabled={
              loading ||
              !question.trim() ||
              !activeSession
            }
            className="bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
          >
            Ask
          </button>

        </div>

      </div>

    </div>
  );
}