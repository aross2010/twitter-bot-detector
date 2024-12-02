'use client'
import axios from 'axios'
import { useState } from 'react'

export default function Home() {
  const [username, setUsername] = useState('')

  const handleChange = async (username: string) => {
    setUsername(username)
    const response = await axios.get('http://127.0.0.1:5000/test')
    console.log(response)
  }

  return (
    <section>
      <h1>Twitter Bot Detector</h1>
      <input
        type="text"
        placeholder="Enter a Twitter username"
        onChange={(e) => handleChange(e.target.value)}
      />
    </section>
  )
}
