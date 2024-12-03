'use client'
import Link from 'next/link'
import { FaTwitter } from 'react-icons/fa'
import { FaFilePdf, FaGithub } from 'react-icons/fa6'

const links = [
  {
    icon: FaGithub,
    href: 'https://github.com/aross2010/twitter-bot-detector',
  },
  {
    icon: FaFilePdf,
    href: '/docs',
  },
] as const

export default function Navbar() {
  const renderedLinks = links.map(({ href, icon: Icon }) => {
    return (
      <li key={href}>
        <Link href={href}>
          <Icon />
        </Link>
      </li>
    )
  })

  return (
    <nav className="h-[70px] w-full flex justify-center border-b bg-white">
      <div className="w-full max-w-[1000px] px-4 flex items-center justify-between">
        <h1 className="text-twitter sm:text-2xl text-xl font-black flex items-center gap-2">
          Twitter Bot Detector <FaTwitter />
        </h1>
        <ul className="flex items-center text-twitter gap-4 sm:text-2xl text-xl">
          {renderedLinks}
        </ul>
      </div>
    </nav>
  )
}
