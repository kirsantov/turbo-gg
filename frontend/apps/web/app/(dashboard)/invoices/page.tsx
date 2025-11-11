export default function InvoicesPage() {
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
        <a
          href="http://localhost:8000/api/invoices/"
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
        >
          View API
        </a>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex gap-4">
          <input
            type="text"
            placeholder="Search invoices..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2"
          />
          <select className="rounded-lg border border-gray-300 px-4 py-2">
            <option>All Organizations</option>
          </select>
          <select className="rounded-lg border border-gray-300 px-4 py-2">
            <option>All Providers</option>
            <option>OlmOCR</option>
            <option>Marker + DeepSeek R1</option>
          </select>
        </div>

        <div className="text-center py-12 text-gray-500">
          <p>No invoices found. Upload your first invoice to get started!</p>
          <p className="mt-2 text-sm">API integration needed for live data</p>
        </div>
      </div>
    </div>
  )
}
