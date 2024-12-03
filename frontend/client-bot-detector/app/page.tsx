'use client'
import axios from 'axios'
import { Fragment, useEffect, useState } from 'react'
import { DetectionResults, SearchedUser } from './lib/types'
import Image from 'next/image'
import { FaCircleXmark, FaMagnifyingGlass } from 'react-icons/fa6'
import { FaSearch } from 'react-icons/fa'
import { AiOutlineLoading } from 'react-icons/ai'
import Link from 'next/link'

export default function Home() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchedUser[]>([])
  const [isSearchBarFocused, setIsSearchBarFocused] = useState(false)
  const [isSearchLoading, setIsSearchLoading] = useState(false)
  const [detectionResults, setDetectionResults] = useState<any>(null)
  const [detectedUser, setDetectedUser] = useState<SearchedUser | null>(null)

  useEffect(() => {
    if (username.length < 1) {
      setSearchResults([])
      return
    }

    const getResults = setTimeout(async () => {
      setIsSearchLoading(true)
      const response = await axios.get(
        `http://127.0.0.1:5000/search/${username}`
      )
      setSearchResults(response.data as SearchedUser[])
      setIsSearchLoading(false)
    }, 500)

    return () => clearTimeout(getResults)
  }, [username])

  const getDetectionResults = async (user: SearchedUser) => {
    setLoading(true)
    setDetectedUser(user)
    setUsername('')
    const result = await axios.post('http://127.0.0.1:5000/predict', {
      screen_name: user.screen_name,
    })
    const data = result.data as DetectionResults
    if (data.error) {
      console.error(data.error)
    }
    setDetectionResults(data)
    setLoading(false)
  }

  const renderedResults = searchResults.map((user) => {
    return (
      <li key={user.id}>
        <button
          onClick={() => getDetectionResults(user)}
          className="flex items-center gap-2 py-1 hover:bg-twitter hover:text-gray-50 transition-colors rounded-lg px-2 w-full"
        >
          <Image
            src={user.profile_image}
            alt={user.screen_name}
            width={40}
            height={40}
            className="rounded-full border"
          />
          <span className="font-medium text-inherit">@{user.screen_name}</span>
        </button>
      </li>
    )
  })

  return (
    <section className=" w-full max-w-[450px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-extrabold text-xl">Find a Twitter Account</h2>
      </div>

      <div
        className={`flex relative items-center py-3 rounded-lg w-full border bg-gray-50 ${
          isSearchBarFocused ? 'outline outline-twitter' : 'outline-none'
        }`}
      >
        <FaMagnifyingGlass className="text-gray-400 ml-3" />
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. 'elonmusk'"
          className="px-3 w-full outline-none bg-transparent"
          onFocus={() => setIsSearchBarFocused(true)}
          onBlur={() => setIsSearchBarFocused(false)}
        />
        <button
          className="mr-3 text-gray-400 text-lg"
          onClick={
            !isSearchLoading
              ? () => {
                  setUsername('')
                }
              : () => {}
          }
        >
          {isSearchLoading ? (
            <AiOutlineLoading className="animate-spin" />
          ) : (
            <FaCircleXmark />
          )}
        </button>
        {searchResults.length > 0 && (
          <ul className="absolute overflow-y-auto max-h-64 p-2 mt-0.5 rounded-lg top-[50px] w-full flex flex-col border bg-gray-50">
            {renderedResults}
          </ul>
        )}
      </div>

      {detectedUser && (
        <div className="flex flex-col p-4 mt-6 border rounded-lg">
          <Link href={`https://x.com/${detectedUser.screen_name}`}>
            <div className="flex items-center gap-2 mb-4">
              <Image
                src={detectedUser?.profile_image}
                alt={detectedUser?.screen_name}
                width={55}
                height={55}
                className="rounded-full border"
              />
              <div className="flex flex-col gap-1">
                <span className="font-bold text-lg leading-none">
                  {detectedUser?.name}
                </span>
                <span className="text-gray-400 leading-none">
                  @{detectedUser?.screen_name}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.following_count}
                </span>
                <span className="text-gray-400">Following</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.followers_count}
                </span>
                <span className="text-gray-400">Followers</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.statuses_count}
                </span>
                <span className="text-gray-400">Posts</span>
              </div>
            </div>
          </Link>
        </div>
      )}
    </section>
  )
}
