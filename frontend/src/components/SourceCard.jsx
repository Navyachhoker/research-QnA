// src/components/SourceCard.jsx
export default function SourceCard({ source }) {
  return (
    <div className="border border-surface-border rounded-lg p-3 bg-surface-raised">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-xs font-semibold bg-accent-bg text-accent-light border border-accent-border px-2 py-0.5 rounded">
          Source {source.source_num}
        </span>
        <span className="text-xs font-medium text-ink-DEFAULT">{source.paper}</span>
        <span className="text-xs text-ink-muted ml-auto">Page {source.page}</span>
      </div>
      <p className="text-xs text-ink-secondary leading-relaxed">{source.snippet}</p>
    </div>
  )
}