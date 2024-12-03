import type { Metadata } from 'next'
import localFont from 'next/font/local'
import './globals.css'
import Navbar from './components/navbar'
import Footer from './components/footer'

const geistSans = localFont({
  src: './fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
})
const geistMono = localFont({
  src: './fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
})

export const metadata: Metadata = {
  title: 'Twitter Bot Detector',
  description: 'Detect Twitter bots with ease.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} flex px-4 tracking-tighter flex-col items-center justify-center bg-gray-50 text-gray-950`}
      >
        <Navbar />
        <main className="mt-24 w-full max-w-[1000px] flex justify-center">
          {children}
        </main>
        {/* <Footer /> */}
      </body>
    </html>
  )
}
