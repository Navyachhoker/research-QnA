// src/components/FileUpload.jsx
import { useState, useRef } from 'react'

export default function FileUpload({ onUpload, loading }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef()

  const handle = (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      alert('Please select a PDF file.')
      return
    }
    onUpload(file)
  }

  return (
    <div
      onClick={() => inputRef.current.click()}
      onDragOver={(e)  => { e.preventDefault(); setDragging(true)  }}
      onDragLeave={()  => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        handle(e.dataTransfer.files[0])
      }}
      className={`border-2 border-dashed rounded-xl p-14 text-center cursor-pointer transition-colors ${
        dragging
          ? 'border-accent bg-accent-bg'
          : 'border-surface-border hover:border-accent-border hover:bg-surface-raised'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => handle(e.target.files[0])}
      />

      {loading ? (
        <div className="space-y-2">
          <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-accent-light font-medium">Ingesting paper...</p>
          <p className="text-xs text-ink-muted">This may take a moment</p>
        </div>
      ) : (
        <>
          {/* Upload icon */}
          <div className="w-10 h-10 bg-accent-bg rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg className="w-5 h-5 text-accent-light" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M16 10l-4-4-4 4M12 6v10"/>
            </svg>
          </div>
          <p className="text-sm font-medium text-ink-DEFAULT mb-1">Drag and drop a PDF</p>
          <p className="text-xs text-ink-muted mb-4">or click to browse your files</p>
          <span className="inline-block text-xs font-medium bg-accent text-surface-base px-4 py-2 rounded-lg">
            Choose file
          </span>
        </>
      )}
    </div>
  )
}