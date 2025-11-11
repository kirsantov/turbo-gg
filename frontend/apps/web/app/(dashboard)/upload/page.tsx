export default function UploadPage() {
  return (
    <div>
      <h1 className="mb-6 text-3xl font-bold text-gray-900">Upload Invoice</h1>

      <div className="max-w-2xl rounded-lg border border-gray-200 bg-white p-8 shadow-sm">
        <p className="mb-6 text-gray-600">
          Upload your invoice file for OCR processing. Supported formats: PDF, JPEG, PNG, TIFF (max 25MB)
        </p>

        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Invoice File
          </label>
          <div className="flex justify-center rounded-lg border-2 border-dashed border-gray-300 px-6 py-10">
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
              <p className="mt-2 text-sm text-gray-600">
                Drop file here or click to browse
              </p>
            </div>
          </div>
        </div>

        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Organization
          </label>
          <input
            type="text"
            className="w-full rounded-lg border border-gray-300 px-4 py-2"
            placeholder="Enter organization name"
          />
        </div>

        <div className="mb-6">
          <label className="mb-2 block text-sm font-medium text-gray-700">
            OCR Provider
          </label>
          <select className="w-full rounded-lg border border-gray-300 px-4 py-2">
            <option>OlmOCR</option>
            <option>Marker + DeepSeek R1</option>
          </select>
        </div>

        <button className="w-full rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700">
          Upload and Process
        </button>

        <p className="mt-4 text-center text-sm text-gray-500">
          Note: This is a frontend placeholder. API integration needed.
        </p>
      </div>
    </div>
  )
}
