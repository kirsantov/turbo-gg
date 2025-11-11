'use client'

import { apiClient, type Invoice } from '@/lib/api-client'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function InvoiceDetailPage() {
  const params = useParams()
  const id = params.id as string

  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadInvoice()
  }, [id])

  const loadInvoice = async () => {
    setLoading(true)
    setError(null)

    try {
      const data = await apiClient.getInvoice(Number(id))
      setInvoice(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load invoice')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-12 text-center shadow-sm">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading invoice...</p>
      </div>
    )
  }

  if (error || !invoice) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6">
        <p className="text-red-800">{error || 'Invoice not found'}</p>
        <Link
          href="/dashboard/invoices"
          className="mt-4 inline-block text-blue-600 hover:underline"
        >
          ← Back to Invoices
        </Link>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            href="/dashboard/invoices"
            className="mb-2 inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
          >
            <svg
              className="mr-1 h-4 w-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Back to Invoices
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Invoice {invoice.number}</h1>
        </div>
        <a
          href={`http://localhost:8000${invoice.source_file}`}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
        >
          View Source File
        </a>
      </div>

      {/* Invoice Details */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Invoice Information</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm font-medium text-gray-600">Invoice Number</p>
                <p className="mt-1 text-base font-semibold text-gray-900">{invoice.number}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Organization</p>
                <p className="mt-1 text-base text-gray-900">{invoice.organization_name}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Issue Date</p>
                <p className="mt-1 text-base text-gray-900">{formatDate(invoice.issue_date)}</p>
              </div>
              {invoice.due_date && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Due Date</p>
                  <p className="mt-1 text-base text-gray-900">{formatDate(invoice.due_date)}</p>
                </div>
              )}
              <div>
                <p className="text-sm font-medium text-gray-600">Currency</p>
                <p className="mt-1 text-base text-gray-900">{invoice.currency}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">OCR Provider</p>
                <p className="mt-1 text-base text-gray-900">
                  {invoice.provider === 'olmocr' ? 'OlmOCR' : 'Marker + DeepSeek R1'}
                </p>
              </div>
            </div>
          </div>

          {/* Supplier */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Supplier</h2>
            <div className="space-y-2">
              <div>
                <p className="text-sm font-medium text-gray-600">Name</p>
                <p className="text-base text-gray-900">{invoice.supplier_name}</p>
              </div>
              {invoice.supplier_tax_id && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Tax ID</p>
                  <p className="text-base text-gray-900">{invoice.supplier_tax_id}</p>
                </div>
              )}
              {invoice.supplier_address && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Address</p>
                  <p className="text-base text-gray-900">{invoice.supplier_address}</p>
                </div>
              )}
            </div>
          </div>

          {/* Buyer */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Buyer</h2>
            <div className="space-y-2">
              <div>
                <p className="text-sm font-medium text-gray-600">Name</p>
                <p className="text-base text-gray-900">{invoice.buyer_name}</p>
              </div>
              {invoice.buyer_tax_id && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Tax ID</p>
                  <p className="text-base text-gray-900">{invoice.buyer_tax_id}</p>
                </div>
              )}
              {invoice.buyer_address && (
                <div>
                  <p className="text-sm font-medium text-gray-600">Address</p>
                  <p className="text-base text-gray-900">{invoice.buyer_address}</p>
                </div>
              )}
            </div>
          </div>

          {/* Line Items */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Line Items</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-gray-200">
                  <tr>
                    <th className="pb-3 text-left text-sm font-medium text-gray-700">
                      Description
                    </th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-700">Qty</th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-700">
                      Unit Price
                    </th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-700">
                      Tax Rate
                    </th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-700">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {invoice.line_items.map((item) => (
                    <tr key={item.id}>
                      <td className="py-3 text-sm text-gray-900">{item.description}</td>
                      <td className="py-3 text-right text-sm text-gray-900">
                        {parseFloat(item.quantity).toFixed(2)} {item.unit || ''}
                      </td>
                      <td className="py-3 text-right text-sm text-gray-900">
                        {parseFloat(item.unit_price).toFixed(2)}
                      </td>
                      <td className="py-3 text-right text-sm text-gray-900">
                        {item.tax_rate ? `${parseFloat(item.tax_rate).toFixed(1)}%` : '-'}
                      </td>
                      <td className="py-3 text-right text-sm font-semibold text-gray-900">
                        {parseFloat(item.total).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sidebar - Totals and Metadata */}
        <div className="space-y-6">
          {/* Financial Totals */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Totals</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Subtotal</span>
                <span className="font-medium text-gray-900">
                  {parseFloat(invoice.subtotal_amount).toFixed(2)} {invoice.currency}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">VAT</span>
                <span className="font-medium text-gray-900">
                  {parseFloat(invoice.vat_amount).toFixed(2)} {invoice.currency}
                </span>
              </div>
              <div className="border-t border-gray-200 pt-3">
                <div className="flex justify-between">
                  <span className="text-base font-semibold text-gray-900">Total</span>
                  <span className="text-xl font-bold text-blue-600">
                    {parseFloat(invoice.total_amount).toFixed(2)} {invoice.currency}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* OCR Metadata */}
          {invoice.provider_payload && Object.keys(invoice.provider_payload).length > 0 && (
            <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-lg font-semibold text-gray-900">OCR Metadata</h2>
              <div className="space-y-2">
                {invoice.provider_payload.confidence !== undefined && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Confidence</p>
                    <p className="text-base text-gray-900">
                      {(invoice.provider_payload.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                )}
                {invoice.provider_payload.latency_ms && (
                  <div>
                    <p className="text-sm font-medium text-gray-600">Processing Time</p>
                    <p className="text-base text-gray-900">
                      {invoice.provider_payload.latency_ms}ms
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Timestamps</h2>
            <div className="space-y-2">
              <div>
                <p className="text-sm font-medium text-gray-600">Created</p>
                <p className="text-sm text-gray-900">
                  {new Date(invoice.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Updated</p>
                <p className="text-sm text-gray-900">
                  {new Date(invoice.updated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
