import { AuthProvider } from '@/providers/auth-provider'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { twMerge } from 'tailwind-merge'

import '@frontend/ui/styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Invoice OCR Platform - AI-Powered Invoice Processing',
  description: 'Automate invoice processing with advanced OCR technology. Extract structured data from scanned invoices using OlmOCR and Marker + DeepSeek R1.'
}

export default function RootLayout({
  children
}: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body
        className={twMerge(
          'bg-gray-50 text-sm text-gray-700 antialiased',
          inter.className
        )}
      >
        <AuthProvider>
          <div className="px-6">
            <div className="container mx-auto my-12 max-w-6xl">{children}</div>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}
