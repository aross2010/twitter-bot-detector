export type SearchedUser = {
  id: string
  screen_name: string
  profile_image: string
  name: string
  is_blue_verified: boolean
  verified: boolean
  followers_count: number
  following_count: number
  statuses_count: number
}

export type DetectionResults = {
  prediction: 'bot' | 'human' | 'invalid'
  probability: number
  top_features: {
    'Account Age': number
    'Followers Count': number
    'Followers Gained Per Day': number
  }
  error?: string
}
