'use client'
import axios from 'axios'
import { Fragment, useEffect, useState } from 'react'
import { DetectionResults, SearchedUser } from './lib/types'
import Image from 'next/image'
import { FaCircleXmark, FaMagnifyingGlass } from 'react-icons/fa6'
import { AiOutlineLoading } from 'react-icons/ai'
import Link from 'next/link'
import numeral from 'numeral'
import blueCheck from '@/public/blue_verification_badge.png'
import goldCheck from '@/public/gold_verification_badge.png'

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
    console.log(data)
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
          <span className="font-medium flex items-center gap-1 text-inherit">
            @{user.screen_name}
            {user.verified ? (
              <Image
                src={goldCheck}
                alt="gold check mark"
                height={20}
                width={20}
              />
            ) : (
              user.is_blue_verified && (
                <Image
                  src={blueCheck}
                  alt="blue check mark"
                  height={20}
                  width={20}
                />
              )
            )}{' '}
          </span>
        </button>
      </li>
    )
  })

  return (
    <section className=" w-full max-w-[450px] flex flex-col">
      <div className="flex flex-col mb-4">
        <h2 className="font-extrabold text-3xl">Twitter Bot Detector</h2>
        <h3 className="text-gray-500">
          A machine learning approach to detecting Twitter/X bots.
        </h3>
      </div>

      <div
        className={`flex relative items-center py-3 rounded-lg w-full border bg-gray-50 ${
          isSearchBarFocused ? 'outline outline-twitter' : 'outline-none'
        }`}
      >
        <FaMagnifyingGlass className="text-gray-500 ml-3" />
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
          className="mr-3 text-gray-500 text-lg"
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
                <span className="font-bold flex items-center gap-1 text-lg leading-none">
                  {detectedUser?.name}{' '}
                  {detectedUser.verified ? (
                    <Image
                      src={goldCheck}
                      alt="gold check mark"
                      height={20}
                      width={20}
                    />
                  ) : (
                    detectedUser.is_blue_verified && (
                      <Image
                        src={blueCheck}
                        alt="blue check mark"
                        height={20}
                        width={20}
                      />
                    )
                  )}
                </span>
                <span className="text-gray-500 leading-none">
                  @{detectedUser?.screen_name}
                </span>
              </div>
            </div>
            <div className="flex items-center flex-wrap sm:gap-4 gap-1.5">
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.following_count > 999
                    ? numeral(detectedUser.following_count).format('0.0a')
                    : detectedUser.following_count}
                </span>
                <span className="text-gray-500">Following</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.followers_count > 999
                    ? numeral(detectedUser.followers_count).format('0.0a')
                    : detectedUser.followers_count}
                </span>
                <span className="text-gray-500">Followers</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="font-semibold">
                  {detectedUser.statuses_count > 999
                    ? numeral(detectedUser.statuses_count).format('0.0a')
                    : detectedUser.statuses_count}
                </span>
                <span className="text-gray-500">Posts</span>
              </div>
            </div>
          </Link>
          {loading && (
            <div className="mt-8 flex items-center gap-4">
              <AiOutlineLoading className="animate-spin text-2xl" />
              <p className="text-center text-gray-500 mt-2">
                Performing account analysis...
              </p>
            </div>
          )}
          {detectionResults && !loading && (
            <div className="mt-8 flex flex-col ">
              {!detectionResults.error ? (
                <Fragment>
                  <div className="flex items-center gap-2">
                    <span>Account Status:</span>
                    <span
                      className={`font-bold ${
                        detectionResults.prediction === 'human'
                          ? 'text-green-500'
                          : 'text-red-500'
                      }`}
                    >
                      {detectionResults.prediction.charAt(0).toUpperCase() +
                        detectionResults.prediction.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>Probability:</span>
                    <span
                      className={`font-bold ${
                        detectionResults.prediction === 'human'
                          ? 'text-green-500'
                          : 'text-red-500'
                      }`}
                    >
                      {Math.round(detectionResults.probability * 100)}%
                    </span>
                  </div>
                </Fragment>
              ) : (
                <Fragment>
                  <span className="font-bold text-red-500">
                    {detectionResults.error}
                  </span>
                </Fragment>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  )
}
