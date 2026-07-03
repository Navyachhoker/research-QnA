// src/components/SourceCard.jsx

export default function SourceCard({ source }) {
  return (
    <div className="border rounded-lg p-4 bg-gray-50">

      <div className="flex items-center gap-2 mb-2">

        <span className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-2 py-1 rounded">
          Source {source.source_num}
        </span>

        <span className="font-medium text-gray-700">
          {source.paper}
        </span>

        <span className="text-xs text-gray-400">
          Page {source.page}
        </span>

      </div>

      <p className="text-sm text-gray-600 leading-6">
        {source.snippet}
      </p>

    </div>
  );
}