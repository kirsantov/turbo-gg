// API client for Invoice OCR backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface Organization {
  id: number
  name: string
  tax_id?: string
  address?: string
  created_at: string
  updated_at: string
}

export interface InvoiceLineItem {
  id: number
  description: string
  quantity: string
  unit?: string
  unit_price: string
  tax_rate?: string
  total: string
}

export interface Invoice {
  id: number
  organization: number
  organization_name: string
  number: string
  issue_date: string
  due_date?: string
  supplier_name: string
  supplier_tax_id?: string
  supplier_address?: string
  buyer_name: string
  buyer_tax_id?: string
  buyer_address?: string
  currency: string
  subtotal_amount: string
  vat_amount: string
  total_amount: string
  raw_text?: string
  source_file: string
  provider: string
  provider_payload: any
  line_items: InvoiceLineItem[]
  created_at: string
  updated_at: string
}

export interface OCRResult {
  invoice_id: number
  organization_id: number
  number: string
  issue_date: string
  due_date?: string
  supplier: {
    name: string
    tax_id?: string
    address?: string
  }
  buyer: {
    name: string
    tax_id?: string
    address?: string
  }
  currency: string
  totals: {
    subtotal: string
    vat: string
    total: string
  }
  line_items: Array<{
    description: string
    quantity: string
    unit?: string
    unit_price: string
    tax_rate?: string
    total: string
  }>
  provider_metadata: {
    name: string
    confidence: number
    latency_ms: number
  }
}

export interface InvoicesListResponse {
  count: number
  next?: string
  previous?: string
  results: Invoice[]
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  // Upload and process invoice with OCR
  async uploadInvoice(
    file: File,
    organizationId?: number,
    organizationName?: string,
    provider: string = 'olmocr'
  ): Promise<OCRResult> {
    const formData = new FormData()
    formData.append('file', file)

    if (organizationId) {
      formData.append('organization_id', organizationId.toString())
    } else if (organizationName) {
      formData.append('organization_name', organizationName)
    }

    formData.append('provider', provider)

    const response = await fetch(`${this.baseUrl}/ocr/invoice`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Upload failed' }))
      throw new Error(error.error || `Upload failed: ${response.statusText}`)
    }

    return response.json()
  }

  // Get list of invoices
  async getInvoices(params?: {
    organization?: number
    number?: string
    provider?: string
    issue_date_from?: string
    issue_date_to?: string
    search?: string
    page?: number
  }): Promise<InvoicesListResponse> {
    const searchParams = new URLSearchParams()

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, value.toString())
        }
      })
    }

    const url = `${this.baseUrl}/api/invoices/?${searchParams.toString()}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`Failed to fetch invoices: ${response.statusText}`)
    }

    return response.json()
  }

  // Get single invoice
  async getInvoice(id: number): Promise<Invoice> {
    const response = await fetch(`${this.baseUrl}/api/invoices/${id}/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch invoice: ${response.statusText}`)
    }

    return response.json()
  }

  // Get organizations
  async getOrganizations(params?: {
    search?: string
    page?: number
  }): Promise<{ count: number; results: Organization[] }> {
    const searchParams = new URLSearchParams()

    if (params?.search) {
      searchParams.append('search', params.search)
    }
    if (params?.page) {
      searchParams.append('page', params.page.toString())
    }

    const url = `${this.baseUrl}/api/organizations/?${searchParams.toString()}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`Failed to fetch organizations: ${response.statusText}`)
    }

    return response.json()
  }

  // Get single organization
  async getOrganization(id: number): Promise<Organization> {
    const response = await fetch(`${this.baseUrl}/api/organizations/${id}/`)

    if (!response.ok) {
      throw new Error(`Failed to fetch organization: ${response.statusText}`)
    }

    return response.json()
  }
}

export const apiClient = new ApiClient()
