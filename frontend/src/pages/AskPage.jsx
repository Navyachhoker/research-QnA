// src/pages/AskPage.jsx
import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  askQuestion, listPapers, listSessions,
  createSession, getHistory, deleteSession
} from '../api/client'
import SourceCard from '../components/SourceCard'

export default function AskPage() {
  const [papers, setPapers]        = useState([])
  const [sessions, setSessions]    = useState([])
  const [activeSession, setActive] = useState(null)
  const [history, setHistory]      = useState([])
  const [paper, setPaper]          = useState('')
  const [question, setQuestion]    = useState('')
  const [loading, setLoading]      = useState(false)
  const [error, setError]          = useState('')
  const [newName, setNewName]      = useState('')
  const bottomRef                  = useRef()

  useEffect(() => {
    listPapers().then(({ data }) => setPapers(data.papers))
    fetchSessions()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history])

  const fetchSessions = async () => {
    const { data } = await listSessions()
    setSessions(data)
  }

  const handleCreateSession = async () => {
    const name = newName.trim() || `Session ${Date.now()}`
    const { data } = await createSession(name)
    setNewName('')
    await fetchSessions()
    selectSession(data)
  }

  const selectSession = async (session) => {
    setActive(session)
    setHistory([])
    const { data } = await getHistory(session.id)
    setHistory(data.turns.map((t) => ({ question: t.question, answer: t.answer, sources: [] })))
  }

  const handleDelete = async (e, sessionId) => {
    e.stopPropagation()
    await deleteSession(sessionId)
    if (activeSession?.id === sessionId) {
      setActive(null)
      setHistory([])
    }
    await fetchSessions()
  }

  const handleAsk = async () => {
    if (!question.trim()) return
    setLoading(true)
    setError('')
    const q = question
    setQuestion('')
    try {
      const { data } = await askQuestion(q, paper || null, 5, activeSession?.id ?? null)
      setHistory((prev) => [...prev, { question: q, answer: data.answer, sources: data.sources }])
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-49px)]">

      {/* Sidebar */}
      <div className="w-56 bg-surface border-r border-surface-border flex flex-col p-3 gap-3 flex-shrink-0">
        <p className="text-xs font-medium text-ink-muted uppercase tracking-widest px-1">
          Sessions
        </p>

        <div className="flex gap-1.5">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreateSession()}
            placeholder="New session..."
            className="flex-1 bg-surface-raised border border-surface-border rounded-lg px-2.5 py-1.5 text-xs text-ink-secondary placeholder:text-ink-muted focus:outline-none focus:border-accent-border"
          />
          <button
            onClick={handleCreateSession}
            className="w-7 h-7 bg-accent rounded-lg text-surface-base font-bold text-sm flex items-center justify-center hover:bg-accent-light transition-colors flex-shrink-0"
          >
            +
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-0.5">
          {sessions.length === 0 && (
            <p className="text-xs text-ink-muted text-center mt-6">No sessions yet</p>
          )}
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => selectSession(s)}
              className={[
                'flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer group transition-colors',
                activeSession?.id === s.id
                  ? 'bg-accent-bg text-accent-light'
                  : 'text-ink-secondary hover:bg-surface-raised hover:text-ink'
              ].join(' ')}
            >
              <span className="text-xs font-medium truncate">{s.name}</span>
              <button
                onClick={(e) => handleDelete(e, s.id)}
                className="text-ink-muted hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity ml-1 flex-shrink-0"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-6 py-5">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h1 className="text-sm font-semibold text-ink">
            {activeSession ? activeSession.name : 'Select or create a session'}
          </h1>
          <select
            value={paper}
            onChange={(e) => setPaper(e.target.value)}
            className="bg-surface-raised border border-surface-border text-ink-secondary text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-accent-border"
          >
            <option value="">All papers</option>
            {papers.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-5 mb-4 pr-1">

          {!activeSession && (
            <div className="text-center py-24">
              <div className="w-10 h-10 bg-accent-bg rounded-xl flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
              </div>
              <p className="text-sm text-ink-secondary">Create or select a session to start</p>
            </div>
          )}

          {history.map((item, i) => (
            <div key={i} className="space-y-3">

              {/* User bubble */}
              <div className="flex justify-end">
                <div className="bg-accent-bg border border-accent-border text-amber-200 rounded-2xl rounded-br-sm px-4 py-2.5 max-w-xl text-sm">
                  {item.question}
                </div>
              </div>

              {/* AI bubble */}
              <div className="bg-surface-raised border border-surface-border rounded-2xl rounded-bl-sm px-5 py-4 max-w-2xl">
                <div className="prose prose-sm">
                  <ReactMarkdown>{item.answer}</ReactMarkdown>
                </div>
              </div>

              {/* Sources */}
              {item.sources?.length > 0 && (
                <div className="space-y-1.5 pl-1">
                  <p className="text-xs text-ink-muted font-medium uppercase tracking-widest">
                    Sources
                  </p>
                  {item.sources.map((s) => (
                    <SourceCard key={s.source_num} source={s} />
                  ))}
                </div>
              )}

            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-ink-muted text-xs pl-1">
              <div className="w-3.5 h-3.5 border border-accent border-t-transparent rounded-full animate-spin" />
              Thinking...
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Error */}
        {error && (
          <p className="text-xs text-red-400 bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2 mb-2">
            {error}
          </p>
        )}

        {/* Input */}
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && handleAsk()}
            disabled={!activeSession}
            placeholder={activeSession ? 'Ask a question about your papers...' : 'Select a session first'}
            className="flex-1 bg-surface-raised border border-surface-border rounded-xl px-4 py-2.5 text-sm text-ink placeholder:text-ink-muted focus:outline-none focus:border-accent-border disabled:opacity-40 transition-colors"
          />
          <button
            onClick={handleAsk}
            disabled={loading || !question.trim() || !activeSession}
            className="bg-accent text-surface-base px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-accent-light disabled:opacity-40 transition-colors"
          >
            Ask
          </button>
        </div>

      </div>
    </div>
  )
}


