'use client'

import { apiClient, type Invoice, type Organization } from '@/lib/api-client'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [search, setSearch] = useState('')
  const [organizationFilter, setOrganizationFilter] = useState<number | ''>('')
  const [providerFilter, setProviderFilter] = useState<string>('')

  // Pagination
  const [page, setPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

  useEffect(() => {
    loadOrganizations()
  }, [])

  useEffect(() => {
    loadInvoices()
  }, [search, organizationFilter, providerFilter, page])

  const loadOrganizations = async () => {
    try {
      const data = await apiClient.getOrganizations()
      setOrganizations(data.results)
    } catch (err) {
      console.error('Failed to load organizations:', err)
    }
  }

  const loadInvoices = async () => {
    setLoading(true)
    setError(null)

    try {
      const params: any = { page }

      if (search) params.search = search
      if (organizationFilter) params.organization = organizationFilter
      if (providerFilter) params.provider = providerFilter

      const data = await apiClient.getInvoices(params)
      setInvoices(data.results)
      setTotalCount(data.count)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load invoices')
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

  const getProviderBadge = (provider: string) => {
    const colors: Record<string, string> = {
      olmocr: 'bg-blue-100 text-blue-800',
      marker_deepseek_r1: 'bg-purple-100 text-purple-800',
    }
    return colors[provider] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Invoices</h1>
        <Link
          href="/dashboard/upload"
          className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
        >
          Upload New
        </Link>
      </div>

      {/* Filters */}
      <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <div className="grid gap-4 md:grid-cols-4">
          <div className="md:col-span-2">
            <input
              type="text"
              placeholder="Search by invoice number, supplier, buyer..."
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
            />
          </div>
          <div>
            <select
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
              value={organizationFilter}
              onChange={(e) => {
                setOrganizationFilter(e.target.value ? Number(e.target.value) : '')
                setPage(1)
              }}
            >
              <option value="">All Organizations</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <select
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
              value={providerFilter}
              onChange={(e) => {
                setProviderFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All Providers</option>
              <option value="olmocr">OlmOCR</option>
              <option value="marker_deepseek_r1">Marker + DeepSeek R1</option>
            </select>
          </div>
        </div>
        {(search || organizationFilter || providerFilter) && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-sm text-gray-600">Active filters:</span>
            {search && (
              <span className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800">
                Search: {search}
              </span>
            )}
            {organizationFilter && (
              <span className="rounded-full bg-purple-100 px-3 py-1 text-sm text-purple-800">
                Org: {organizations.find((o) => o.id === organizationFilter)?.name}
              </span>
            )}
            {providerFilter && (
              <span className="rounded-full bg-green-100 px-3 py-1 text-sm text-green-800">
                Provider: {providerFilter}
              </span>
            )}
            <button
              onClick={() => {
                setSearch('')
                setOrganizationFilter('')
                setProviderFilter('')
                setPage(1)
              }}
              className="text-sm text-red-600 hover:underline"
            >
              Clear all
            </button>
          </div>
        )}
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
          <p className="mt-4 text-gray-600">Loading invoices...</p>
        </div>
      ) : invoices.length === 0 ? (
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="mt-4 text-lg font-medium text-gray-900">No invoices found</p>
          <p className="mt-2 text-gray-600">
            {search || organizationFilter || providerFilter
              ? 'Try adjusting your filters'
              : 'Upload your first invoice to get started'}
          </p>
          <Link
            href="/dashboard/upload"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-6 py-2 font-medium text-white transition hover:bg-blue-700"
          >
            Upload Invoice
          </Link>
        </div>
      ) : (
        <>
          {/* Results count */}
          <div className="mb-4 text-sm text-gray-600">
            Showing {invoices.length} of {totalCount} invoice{totalCount !== 1 && 's'}
          </div>

          {/* Invoices Table */}
          <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Invoice #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Organization
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Supplier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Issue Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Total
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Provider
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-700">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {invoices.map((invoice) => (
                    <tr key={invoice.id} className="hover:bg-gray-50">
                      <td className="whitespace-nowrap px-6 py-4">
                        <Link
                          href={`/dashboard/invoices/${invoice.id}`}
                          className="font-medium text-blue-600 hover:underline"
                        >
                          {invoice.number}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {invoice.organization_name}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {invoice.supplier_name}
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                        {formatDate(invoice.issue_date)}
                      </td>
                      <td className="whitespace-nowrap px-6 py-4">
                        <div className="text-sm font-semibold text-gray-900">
                          {parseFloat(invoice.total_amount).toFixed(2)} {invoice.currency}
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-6 py-4">
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-medium ${getProviderBadge(invoice.provider)}`}
                        >
                          {invoice.provider === 'olmocr' ? 'OlmOCR' : 'Marker+DS'}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-6 py-4 text-sm">
                        <Link
                          href={`/dashboard/invoices/${invoice.id}`}
                          className="text-blue-600 hover:underline"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {totalCount > 10 && (
            <div className="mt-6 flex items-center justify-between">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {Math.ceil(totalCount / 10)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(totalCount / 10)}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
