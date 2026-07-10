// src/pages/AnalyzePage.jsx
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { listPapers, summarizePaper, comparePapers, generateRelatedWork } from '../api/client'

const TABS = ['Summarize', 'Compare', 'Related Work']

export default function AnalyzePage() {
  const [papers, setPapers]     = useState([])
  const [tab, setTab]           = useState('Summarize')
  const [result, setResult]     = useState('')
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [sumPaper, setSumPaper] = useState('')
  const [paperA, setPaperA]     = useState('')
  const [paperB, setPaperB]     = useState('')
  const [topic, setTopic]       = useState('')

  useEffect(() => {
    listPapers().then(({ data }) => setPapers(data.papers))
  }, [])

  const run = async () => {
    setLoading(true)
    setError('')
    setResult('')
    try {
      let data
      if (tab === 'Summarize') {
        ;({ data } = await summarizePaper(sumPaper))
        setResult(data.summary)
      } else if (tab === 'Compare') {
        ;({ data } = await comparePapers(paperA, paperB))
        setResult(data.comparison)
      } else {
        ;({ data } = await generateRelatedWork(topic))
        setResult(data.related_work)
      }
    } catch (e) {
      setError(e.response?.data?.detail || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const canRun =
    tab === 'Summarize'  ? !!sumPaper :
    tab === 'Compare'    ? (!!paperA && !!paperB && paperA !== paperB) :
                           !!topic.trim()

  const selectClass = "w-full bg-surface-raised border border-surface-border rounded-lg px-3 py-2 text-sm text-ink focus:outline-none focus:border-accent-border"
  const inputClass  = "w-full bg-surface-raised border border-surface-border rounded-lg px-3 py-2 text-sm text-ink placeholder:text-ink-muted focus:outline-none focus:border-accent-border"

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <h1 className="text-xl font-semibold text-ink mb-1">Analyze papers</h1>
      <p className="text-sm text-ink-secondary mb-8">
        Summarize, compare, or generate related work
      </p>

      {/* Tabs */}
      <div className="flex border-b border-surface-border mb-8">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => { setTab(t); setResult(''); setError('') }}
            className={`px-5 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
              tab === t
                ? 'border-accent text-accent-light'
                : 'border-transparent text-ink-muted hover:text-ink-secondary'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Controls */}
      <div className="space-y-4 mb-6">
        {tab === 'Summarize' && (
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-2">
              Select paper
            </label>
            <select value={sumPaper} onChange={(e) => setSumPaper(e.target.value)} className={selectClass}>
              <option value="">— choose a paper —</option>
              {papers.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
        )}

        {tab === 'Compare' && (
          <div className="grid grid-cols-2 gap-4">
            {[['Paper A', paperA, setPaperA], ['Paper B', paperB, setPaperB]].map(([label, val, setter]) => (
              <div key={label}>
                <label className="block text-xs font-medium text-ink-secondary mb-2">{label}</label>
                <select value={val} onChange={(e) => setter(e.target.value)} className={selectClass}>
                  <option value="">— choose —</option>
                  {papers.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            ))}
          </div>
        )}

        {tab === 'Related Work' && (
          <div>
            <label className="block text-xs font-medium text-ink-secondary mb-2">Topic</label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. transformer-based language models"
              className={inputClass}
            />
          </div>
        )}
      </div>

      <button
        onClick={run}
        disabled={loading || !canRun}
        className="bg-accent text-surface-base px-6 py-2.5 rounded-xl text-sm font-medium hover:bg-accent-light disabled:opacity-40 transition-colors mb-8 flex items-center gap-2"
      >
        {loading
          ? <>
              <span className="w-3.5 h-3.5 border-2 border-surface-base border-t-transparent rounded-full animate-spin" />
              Working...
            </>
          : `Generate ${tab}`
        }
      </button>

      {error && (
        <p className="text-xs text-red-400 bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2 mb-4">
          {error}
        </p>
      )}

      {result && (
        <div className="bg-surface-raised border border-surface-border rounded-xl px-6 py-5">
          <div className="flex items-center gap-2 mb-4 pb-4 border-b border-surface-border">
            <div className="w-6 h-6 bg-accent-bg rounded flex items-center justify-center">
              <svg className="w-3.5 h-3.5 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 12h6M9 16h6M9 8h6M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z"/>
              </svg>
            </div>
            <span className="text-xs font-medium text-ink-secondary">{tab} result</span>
          </div>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}