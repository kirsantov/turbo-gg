import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 to-purple-700 text-white">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        <div className="container relative mx-auto px-6 py-24">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl">
              Invoice OCR Platform
            </h1>
            <p className="mb-8 text-xl text-blue-100 md:text-2xl">
              Automate invoice processing with AI-powered OCR technology
            </p>
            <p className="mb-12 text-lg text-blue-50">
              Upload scanned invoices and let our advanced OCR system extract structured data instantly.
              Support for multiple providers including OlmOCR and Marker + DeepSeek R1.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/dashboard"
                className="rounded-lg bg-white px-8 py-4 text-lg font-semibold text-blue-600 shadow-lg transition hover:bg-blue-50"
              >
                Go to Dashboard
              </Link>
              <Link
                href="/login"
                className="rounded-lg border-2 border-white px-8 py-4 text-lg font-semibold text-white transition hover:bg-white hover:text-blue-600"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white py-20">
        <div className="container mx-auto px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900">
              Powerful Features
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Everything you need to streamline your invoice processing workflow
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-blue-100">
                <svg
                  className="h-8 w-8 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Easy Upload
              </h3>
              <p className="text-gray-600">
                Drag and drop or select PDF, JPEG, PNG, or TIFF files up to 25MB.
                Simple and intuitive interface.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-purple-100">
                <svg
                  className="h-8 w-8 text-purple-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                AI-Powered OCR
              </h3>
              <p className="text-gray-600">
                Choose between OlmOCR for speed or Marker + DeepSeek R1 for advanced AI processing.
                High accuracy data extraction.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-green-100">
                <svg
                  className="h-8 w-8 text-green-600"
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
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Structured Data
              </h3>
              <p className="text-gray-600">
                Automatically extract invoice numbers, dates, amounts, supplier/buyer details,
                and line items in structured format.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-yellow-100">
                <svg
                  className="h-8 w-8 text-yellow-600"
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
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Organization Management
              </h3>
              <p className="text-gray-600">
                Group invoices by organization. Create new organizations or select existing ones
                during upload.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-red-100">
                <svg
                  className="h-8 w-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                  />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Advanced Filtering
              </h3>
              <p className="text-gray-600">
                Filter invoices by organization, OCR provider, date range, or search by
                invoice number and company names.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="rounded-xl border border-gray-200 p-8 shadow-sm transition hover:shadow-md">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-indigo-100">
                <svg
                  className="h-8 w-8 text-indigo-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
              </div>
              <h3 className="mb-3 text-xl font-semibold text-gray-900">
                Export Data
              </h3>
              <p className="text-gray-600">
                Export invoice data to CSV, access via REST API, or use the admin panel
                for bulk operations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-gray-50 py-20">
        <div className="container mx-auto px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900">
              How It Works
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-gray-600">
              Get started in three simple steps
            </p>
          </div>

          <div className="grid gap-12 md:grid-cols-3">
            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-600 text-3xl font-bold text-white">
                  1
                </div>
              </div>
              <h3 className="mb-3 text-2xl font-semibold text-gray-900">
                Upload Invoice
              </h3>
              <p className="text-gray-600">
                Select your invoice file (PDF or image) and choose the organization
              </p>
            </div>

            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-purple-600 text-3xl font-bold text-white">
                  2
                </div>
              </div>
              <h3 className="mb-3 text-2xl font-semibold text-gray-900">
                OCR Processing
              </h3>
              <p className="text-gray-600">
                Our AI extracts all invoice data automatically in seconds
              </p>
            </div>

            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="flex h-20 w-20 items-center justify-center rounded-full bg-green-600 text-3xl font-bold text-white">
                  3
                </div>
              </div>
              <h3 className="mb-3 text-2xl font-semibold text-gray-900">
                Review & Export
              </h3>
              <p className="text-gray-600">
                View structured data, make edits if needed, and export to your system
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-20 text-white">
        <div className="container mx-auto px-6 text-center">
          <h2 className="mb-4 text-4xl font-bold">
            Ready to Automate Your Invoices?
          </h2>
          <p className="mb-8 text-xl text-blue-50">
            Start processing invoices with AI-powered OCR today
          </p>
          <Link
            href="/dashboard"
            className="inline-block rounded-lg bg-white px-10 py-4 text-lg font-semibold text-blue-600 shadow-lg transition hover:bg-blue-50"
          >
            Get Started Now
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 py-12 text-gray-300">
        <div className="container mx-auto px-6">
          <div className="grid gap-8 md:grid-cols-3">
            <div>
              <h3 className="mb-4 text-xl font-semibold text-white">
                Invoice OCR
              </h3>
              <p className="text-gray-400">
                AI-powered invoice processing for modern businesses
              </p>
            </div>
            <div>
              <h4 className="mb-4 font-semibold text-white">Quick Links</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/dashboard" className="hover:text-white">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <Link href="/login" className="hover:text-white">
                    Sign In
                  </Link>
                </li>
                <li>
                  <Link href="/register" className="hover:text-white">
                    Register
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 font-semibold text-white">Support</h4>
              <ul className="space-y-2">
                <li>
                  <a
                    href="http://localhost:8000/api/docs/"
                    className="hover:text-white"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    API Documentation
                  </a>
                </li>
                <li>
                  <a
                    href="http://localhost:8000/admin/"
                    className="hover:text-white"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Admin Panel
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-8 border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Invoice OCR Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
