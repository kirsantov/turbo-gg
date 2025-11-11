'use client'

import { apiClient, type OCRResult, type Organization } from '@/lib/api-client'
import Link from 'next/link'
import { useEffect, useState } from 'react'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const [organizationType, setOrganizationType] = useState<'existing' | 'new'>('new')
  const [organizationId, setOrganizationId] = useState<number | undefined>()
  const [organizationName, setOrganizationName] = useState('')
  const [provider, setProvider] = useState('ollama_local')
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<OCRResult | null>(null)

  // Load organizations
  useEffect(() => {
    apiClient
      .getOrganizations()
      .then((data) => setOrganizations(data.results))
      .catch((err) => console.error('Failed to load organizations:', err))
  }, [])

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    // Validate file type
    const allowedTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/tiff',
    ]
    if (!allowedTypes.includes(file.type)) {
      setError('Invalid file type. Please upload PDF, JPEG, PNG, or TIFF.')
      return
    }

    // Validate file size (25MB)
    if (file.size > 25 * 1024 * 1024) {
      setError('File size exceeds 25MB limit.')
      return
    }

    setFile(file)
    setError(null)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    if (!file) {
      setError('Please select a file')
      return
    }

    if (organizationType === 'existing' && !organizationId) {
      setError('Please select an organization')
      return
    }

    if (organizationType === 'new' && !organizationName.trim()) {
      setError('Please enter organization name')
      return
    }

    setLoading(true)

    try {
      const result = await apiClient.uploadInvoice(
        file,
        organizationType === 'existing' ? organizationId : undefined,
        organizationType === 'new' ? organizationName : undefined,
        provider
      )

      setResult(result)
      setFile(null)
      setOrganizationName('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Upload Invoice</h1>

      {/* Success Result */}
      {result && (
        <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-6">
          <div className="mb-4 flex items-center">
            <svg
              className="mr-2 h-6 w-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <h3 className="text-lg font-semibold text-green-900">
              Invoice Processed Successfully!
            </h3>
          </div>

          <div className="mb-4 grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-gray-700">Invoice Number</p>
              <p className="text-lg font-semibold text-gray-900">{result.number}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Issue Date</p>
              <p className="text-lg font-semibold text-gray-900">{result.issue_date}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Supplier</p>
              <p className="text-lg font-semibold text-gray-900">
                {result.supplier.name}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Total Amount</p>
              <p className="text-lg font-semibold text-gray-900">
                {result.totals.total} {result.currency}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">OCR Provider</p>
              <p className="text-lg font-semibold text-gray-900">
                {result.provider_metadata.name}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">Confidence</p>
              <p className="text-lg font-semibold text-gray-900">
                {(result.provider_metadata.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <Link
              href={`/dashboard/invoices/${result.invoice_id}`}
              className="rounded-lg bg-green-600 px-6 py-2 font-medium text-white transition hover:bg-green-700"
            >
              View Invoice Details
            </Link>
            <button
              onClick={() => setResult(null)}
              className="rounded-lg border border-gray-300 px-6 py-2 font-medium text-gray-700 transition hover:bg-gray-50"
            >
              Upload Another
            </button>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-center">
            <svg
              className="mr-2 h-5 w-5 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Upload Form */}
      <form onSubmit={handleSubmit}>
        <div className="max-w-2xl rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
          {/* File Upload */}
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Invoice File *
            </label>
            <div
              className={`relative flex justify-center rounded-lg border-2 border-dashed px-6 py-10 transition ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {file ? (
                  <p className="mt-2 text-sm font-medium text-gray-900">{file.name}</p>
                ) : (
                  <p className="mt-2 text-sm text-gray-600">
                    Drop file here or click to browse
                  </p>
                )}
                <p className="mt-1 text-xs text-gray-500">
                  PDF, JPEG, PNG, TIFF up to 25MB
                </p>
              </div>
              <input
                type="file"
                className="absolute inset-0 cursor-pointer opacity-0"
                accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif"
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </div>

          {/* Organization Type */}
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Organization *
            </label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={organizationType === 'existing'}
                  onChange={() => setOrganizationType('existing')}
                  className="mr-2"
                  disabled={loading}
                />
                <span className="text-sm text-gray-700">Select Existing</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={organizationType === 'new'}
                  onChange={() => setOrganizationType('new')}
                  className="mr-2"
                  disabled={loading}
                />
                <span className="text-sm text-gray-700">Create New</span>
              </label>
            </div>
          </div>

          {/* Organization Select */}
          {organizationType === 'existing' && (
            <div className="mb-6">
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Select Organization
              </label>
              <select
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
                value={organizationId || ''}
                onChange={(e) => setOrganizationId(Number(e.target.value))}
                disabled={loading}
              >
                <option value="">-- Select Organization --</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                    {org.tax_id && ` (${org.tax_id})`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Organization Name Input */}
          {organizationType === 'new' && (
            <div className="mb-6">
              <label className="mb-2 block text-sm font-medium text-gray-700">
                Organization Name
              </label>
              <input
                type="text"
                className="w-full rounded-lg border border-gray-300 px-4 py-2"
                placeholder="Enter organization name"
                value={organizationName}
                onChange={(e) => setOrganizationName(e.target.value)}
                disabled={loading}
              />
            </div>
          )}

          {/* Provider Selection */}
          <div className="mb-6">
            <label className="mb-2 block text-sm font-medium text-gray-700">
              OCR Provider
            </label>
            <select
              className="w-full rounded-lg border border-gray-300 px-4 py-2"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              disabled={loading}
            >
              <option value="ollama_local">🚀 Ollama Local (GPU) - FREE!</option>
              <option value="olmocr">OlmOCR (Fast)</option>
              <option value="marker_deepseek_r1">Marker + DeepSeek R1 (Advanced AI)</option>
            </select>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !file}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg
                  className="mr-2 h-5 w-5 animate-spin"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Processing...
              </span>
            ) : (
              'Upload and Process'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
