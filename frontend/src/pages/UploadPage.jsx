// src/pages/UploadPage.jsx
import { useState } from 'react'
import FileUpload from '../components/FileUpload'
import { uploadPaper } from '../api/client'

export default function UploadPage() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState([])
  const [error, setError]     = useState('')

  const handleUpload = async (file) => {
    setLoading(true)
    setError('')
    try {
      const { data } = await uploadPaper(file)
      setResults((prev) => [data, ...prev])
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-xl font-semibold text-ink mb-1">Upload papers</h1>
      <p className="text-sm text-ink-secondary mb-8">Add PDFs to your knowledge base</p>

      <FileUpload onUpload={handleUpload} loading={loading} />

      {error && (
        <p className="mt-4 text-xs text-red-400 bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2">
          {error}
        </p>
      )}

      {results.length > 0 && (
        <div className="mt-8 space-y-2">
          <p className="text-xs font-medium text-ink-muted uppercase tracking-widest mb-3">
            Ingested this session
          </p>
          {results.map((r, i) => (
            <div
              key={i}
              className="flex items-center gap-3 bg-surface-raised border border-surface-border rounded-xl px-4 py-3"
            >
              <div className="w-8 h-8 bg-accent-bg rounded-lg flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-ink truncate">{r.paper_name}</p>
                <p className="text-xs text-ink-muted">{r.chunk_count} chunks stored</p>
              </div>
              <span className="text-xs bg-green-950/50 text-green-400 border border-green-900/40 px-2 py-0.5 rounded flex-shrink-0">
                ✓ Ingested
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}