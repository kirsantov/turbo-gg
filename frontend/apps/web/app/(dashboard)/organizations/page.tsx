export default function OrganizationsPage() {
  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Organizations</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700">
          Add Organization
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="text-center py-12 text-gray-500">
          <p>No organizations yet. Organizations will appear here.</p>
          <p className="mt-2 text-sm">API integration needed for live data</p>
        </div>
      </div>
    </div>
  )
}
