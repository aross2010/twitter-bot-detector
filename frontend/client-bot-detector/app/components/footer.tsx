'use client'
import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="py-16 w-full flex justify-center border-t bg-white">
      <div className="w-full max-w-[1000px] px-4 flex sm:flex-row flex-col sm:gap-0 gap-6 justify-between items-center">
        <div className="w-full sm:max-w-[325px] text-center">
          <p className="text-sm ">
            Special thanks to the{' '}
            <Link
              className="underline"
              href="https://"
            >
              TwiBot-22
            </Link>{' '}
            team for access to their benchmark dataset. To learn more about our
            project, read our{' '}
            <Link
              href="/docs"
              className="underline"
            >
              research paper
            </Link>{' '}
            or view our{' '}
            <Link
              href="/docs"
              className="underline"
            >
              presentation
            </Link>
            .
          </p>
        </div>
        <div className="flex-col items-center flex">
          <span className="text-sm"> San Jose State University, Fall 2024</span>
          <span className="text-sm">
            {' '}
            CS 166 Information Security <span className="text-gray-400">
              •
            </span>{' '}
            Dr. Chao-Li Tarng{' '}
          </span>
          <span className="text-sm ml-4">
            © {new Date().getFullYear()} Twitter Bot Detector
          </span>
        </div>
      </div>
    </footer>
  )
}
