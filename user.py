from dataclasses import dataclass
from typing import List

@dataclass
class User:
    created_at_datetime: str
    name: str
    screen_name: str
    profile_image_url: str
    profile_banner_url: str
    url: str
    location: str
    is_blue_verified: bool
    verified: bool
    possibly_sensitive: bool
    can_dm: bool
    can_media_tag: bool
    want_retweets: bool
    followers_count: int
    fast_followers_count: int
    normal_followers_count: int
    following_count: int
    favourites_count: int
    media_count: int
    statuses_count: int
    withheld_in_countries: List[str]
    translator_type: str