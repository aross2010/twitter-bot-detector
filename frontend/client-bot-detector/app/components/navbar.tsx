'use client'
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
]

export default function Navbar() {
  return (
    <nav className="h-[70px] w-full max-w-[1000px] flex items-center justify-between">
      <h1 className="text-twitter text-2xl font-black flex items-center gap-2">
        Twitter Bot Detector <FaTwitter />
      </h1>
      <ul></ul>
    </nav>
  )
}
