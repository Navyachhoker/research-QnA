// src/pages/PapersPage.jsx
import { useEffect, useState } from 'react'
import { listPapers } from '../api/client'

export default function PapersPage() {
  const [papers, setPapers]   = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listPapers()
      .then(({ data }) => setPapers(data.papers))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-xl font-semibold text-ink mb-1">Knowledge base</h1>
      <p className="text-sm text-ink-secondary mb-8">
        {loading ? 'Loading...' : `${papers.length} paper${papers.length !== 1 ? 's' : ''} ingested`}
      </p>

      {!loading && papers.length === 0 && (
        <div className="text-center py-20 border border-dashed border-surface-border rounded-xl">
          <div className="w-10 h-10 bg-accent-bg rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-5 h-5 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <p className="text-sm text-ink-secondary">No papers yet</p>
          <p className="text-xs text-ink-muted mt-1">Upload PDFs from the Upload page</p>
        </div>
      )}

      <div className="space-y-2">
        {papers.map((name, i) => (
          <div
            key={name}
            className="flex items-center gap-3 bg-surface-raised border border-surface-border rounded-xl px-4 py-3 group"
          >
            <div className="w-9 h-9 bg-accent-bg rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-ink truncate">{name}</p>
              <p className="text-xs text-ink-muted">Paper {i + 1}</p>
            </div>
            <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-xs bg-accent-bg border border-accent-border text-accent-light px-2.5 py-1 rounded-md cursor-pointer">
                Ask
              </span>
              <span className="text-xs border border-surface-border text-ink-secondary px-2.5 py-1 rounded-md cursor-pointer hover:text-ink">
                Summarize
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}