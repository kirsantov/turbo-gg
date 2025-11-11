'use client'

import { apiClient, type Organization } from '@/lib/api-client'
import { useEffect, useState } from 'react'

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadOrganizations()
  }, [search])

  const loadOrganizations = async () => {
    setLoading(true)
    setError(null)

    try {
      const params: any = {}
      if (search) params.search = search

      const data = await apiClient.getOrganizations(params)
      setOrganizations(data.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organizations')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Organizations</h1>
        <a
          href="http://localhost:8000/admin/billing/organization/add/"
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
        >
          Add in Admin
        </a>
      </div>

      {/* Search */}
      <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <input
          type="text"
          placeholder="Search organizations by name or tax ID..."
          className="w-full rounded-lg border border-gray-300 px-4 py-2"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">{error}</p>
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center shadow-sm">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading organizations...</p>
        </div>
      ) : organizations.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center shadow-sm">
          <svg
            className="mx-auto h-16 w-16 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
          <p className="mt-4 text-lg font-medium text-gray-900">No organizations found</p>
          <p className="mt-2 text-gray-600">
            {search
              ? 'Try a different search term'
              : 'Create organizations when uploading invoices or in the admin panel'}
          </p>
        </div>
      ) : (
        <>
          <div className="mb-4 text-sm text-gray-600">
            {organizations.length} organization{organizations.length !== 1 && 's'} found
          </div>

          {/* Organizations Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {organizations.map((org) => (
              <div
                key={org.id}
                className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
                    <svg
                      className="h-6 w-6 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                      />
                    </svg>
                  </div>
                  <a
                    href={`http://localhost:8000/admin/billing/organization/${org.id}/change/`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    Edit
                  </a>
                </div>

                <h3 className="mb-2 text-lg font-semibold text-gray-900">{org.name}</h3>

                {org.tax_id && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-600">Tax ID</p>
                    <p className="text-sm text-gray-900">{org.tax_id}</p>
                  </div>
                )}

                {org.address && (
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-600">Address</p>
                    <p className="text-sm text-gray-900">{org.address}</p>
                  </div>
                )}

                <div className="mt-4 border-t border-gray-100 pt-3">
                  <p className="text-xs text-gray-500">
                    Created {formatDate(org.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
