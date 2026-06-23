import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

class QuotaExceededError(Exception):
    """Custom exception raised when the YouTube API quota is exceeded."""
    pass

def is_demo_mode():
    """Checks if the application should run in demo mode (using mock data)."""
    return not API_KEY or API_KEY == "your_key_here"

def get_youtube_client():
    """Initializes and returns a YouTube API client."""
    if is_demo_mode():
        raise ValueError("YouTube API key is missing or not configured in the .env file. Running in Demo Mode.")
    return build("youtube", "v3", developerKey=API_KEY)

# Mock Data for Demo Mode
MOCK_CHANNELS = [
    {
        "channel_id": "UCBJycsmduvYELgTrujCgOPg",
        "title": "Marques Brownlee (Demo)",
        "thumbnail": "https://yt3.googleusercontent.com/lkH37D7g6_45IDCl9HsRz0wM0CgGTOAxDsRKxoNs2RUXtiIPtA9B__lhJIpTYphcoN55fLwqEA=s160-c-k-c0x00ffffff-no-rj",
        "subscriber_count": 18900000
    },
    {
        "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
        "title": "MrBeast (Demo)",
        "thumbnail": "https://yt3.googleusercontent.com/cr2-QOebm91hM6h62p9Vn3Hl8qK92d8jVn4o9bF4R1g48rR3YQ_Eux_Lq0p7-eFzE7qgq9hU_w=s160-c-k-c0x00ffffff-no-rj",
        "subscriber_count": 285000000
    },
    {
        "channel_id": "UCq-Fj5jknLsUf-MWSy4_brA",
        "title": "T-Series (Demo)",
        "thumbnail": "https://yt3.googleusercontent.com/y1F4Eiyi5RvR_Z6sP5t3X8h7XnQxK4N9c9w5n7-eFzE7qgq9hU_w=s160-c-k-c0x00ffffff-no-rj",
        "subscriber_count": 268000000
    }
]

MOCK_DETAILS = {
    "UCBJycsmduvYELgTrujCgOPg": {
        "profile": {
            "title": "Marques Brownlee (Demo)",
            "thumbnail": "https://yt3.googleusercontent.com/lkH37D7g6_45IDCl9HsRz0wM0CgGTOAxDsRKxoNs2RUXtiIPtA9B__lhJIpTYphcoN55fLwqEA=s160-c-k-c0x00ffffff-no-rj",
            "country": "US",
            "description": "MKBHD: Quality Tech Videos | Novelist | Professional Ultimate Frisbee player.",
            "subscriber_count": 18900000,
            "total_views": 4350000000,
            "video_count": 1640
        },
        "video_titles": [
            ("iPhone 18 Pro Review: The Truth!", 4200000, 280000, 18000, 2),
            ("The Future of EVs (2026)", 3100000, 190000, 12000, 6),
            ("My Everyday Tech: MKBHD Desk Setup", 5200000, 390000, 22000, 12),
            ("Apple Vision Pro 2: 6 Months Later", 2800000, 150000, 9500, 18),
            ("Reviewing the Worst Tech of the Year", 6100000, 480000, 35000, 25),
            ("We Built a Tech Lab!", 3800000, 250000, 14000, 32),
            ("Is This AI Smartphone Actually Good?", 2900000, 140000, 8000, 40),
            ("The Ultimate 2026 Camera Comparison", 4800000, 320000, 19000, 48),
            ("Smartwatches are Getting Boring...", 1800000, 98000, 6200, 55)
        ]
    },
    "UCX6OQ3DkcsbYNE6H8uQQuVA": {
        "profile": {
            "title": "MrBeast (Demo)",
            "thumbnail": "https://yt3.googleusercontent.com/cr2-QOebm91hM6h62p9Vn3Hl8qK92d8jVn4o9bF4R1g48rR3YQ_Eux_Lq0p7-eFzE7qgq9hU_w=s160-c-k-c0x00ffffff-no-rj",
            "country": "US",
            "description": "I want to make the world a better place before I die.",
            "subscriber_count": 285000000,
            "total_views": 51200000000,
            "video_count": 800
        },
        "video_titles": [
            ("Surviving 100 Days In A Red Circle", 145000000, 8200000, 450000, 4),
            ("I Bought The World's Most Expensive Private Island", 189000000, 9500000, 520000, 10),
            ("$1 vs $100,000,000 House!", 210000000, 11000000, 680000, 20),
            ("Ages 1 to 100 Fight For $500,000", 167000000, 7800000, 390000, 28),
            ("Last To Leave Rollercoaster Wins $100k", 125000000, 6100000, 280000, 35),
            ("I Filled My Friend's House With Slime", 110000000, 5500000, 240000, 45),
            ("Would You Sit In This Room For $10k A Minute?", 198000000, 10200000, 610000, 56)
        ]
    },
    "UCq-Fj5jknLsUf-MWSy4_brA": {
        "profile": {
            "title": "T-Series (Demo)",
            "thumbnail": "https://yt3.googleusercontent.com/y1F4Eiyi5RvR_Z6sP5t3X8h7XnQxK4N9c9w5n7-eFzE7qgq9hU_w=s160-c-k-c0x00ffffff-no-rj",
            "country": "IN",
            "description": "India's largest Music Label & Movie Studio, believes in bringing world close together through its Music.",
            "subscriber_count": 268000000,
            "total_views": 258000000000,
            "video_count": 21000
        },
        "video_titles": [
            ("New Hindi Pop Song Hit 2026", 12000000, 450000, 15000, 1),
            ("Romantic Bollywood Track (Official Video)", 18000000, 680000, 22000, 3),
            ("Party Anthem of the Year", 25000000, 980000, 31000, 8),
            ("Sufi Love Melody 2026", 8500000, 320000, 9800, 14),
            ("Classical Fusion Dance Beats", 6200000, 210000, 7400, 21),
            ("Teaser: Mega Budget Movie Song", 14000000, 550000, 18000, 27),
            ("Lofi Chill Mix - Rainy Days", 4300000, 180000, 6100, 35),
            ("Retro Remix Vol 5", 9800000, 390000, 11000, 44),
            ("Devotional Morning Bhajans", 3100000, 120000, 4200, 52)
        ]
    }
}

def search_channels(query):
    """
    Searches channels by query, returns top 3 channels.
    """
    if not query:
        return []
        
    if is_demo_mode():
        # Filter mock channels loosely matching query, or return all three if no match
        query_lower = query.lower()
        matched = [ch for ch in MOCK_CHANNELS if query_lower in ch["title"].lower()]
        return matched if matched else MOCK_CHANNELS

    try:
        youtube = get_youtube_client()
        
        # Search for channel IDs
        search_response = youtube.search().list(
            part="snippet",
            type="channel",
            q=query,
            maxResults=3
        ).execute()

        channel_ids = [
            item["id"]["channelId"] 
            for item in search_response.get("items", []) 
            if "channelId" in item["id"]
        ]
        
        if not channel_ids:
            return []

        # Batch get channel details for subscriber counts
        channels_response = youtube.channels().list(
            part="snippet,statistics",
            id=",".join(channel_ids)
        ).execute()

        results = []
        for item in channels_response.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            results.append({
                "channel_id": item["id"],
                "title": snippet.get("title", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "subscriber_count": int(stats.get("subscriberCount", 0))
            })
        return results

    except HttpError as e:
        if e.resp.status == 403:
            raise QuotaExceededError("YouTube API quota exceeded")
        return []
    except ValueError as ve:
        raise ve
    except Exception:
        return []

def get_channel_stats(channel_id):
    """
    Fetches details of a single channel.
    """
    if is_demo_mode():
        if channel_id in MOCK_DETAILS:
            return MOCK_DETAILS[channel_id]["profile"]
        # Fallback dynamic mock profile for un-mocked ID
        return {
            "title": f"Custom Channel ({channel_id[:6]})",
            "thumbnail": "https://yt3.googleusercontent.com/ytc/AIdro5k80S6P779wK78gY86fP2G38V5tPq=s160-c-k-c0x00ffffff-no-rj",
            "country": "IN",
            "description": "Dynamic demo profile because no API key is configured.",
            "subscriber_count": 1250000,
            "total_views": 85000000,
            "video_count": 210
        }

    try:
        youtube = get_youtube_client()
        
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()

        items = response.get("items", [])
        if not items:
            return {}

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        return {
            "title": snippet.get("title", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", snippet.get("thumbnails", {}).get("default", {}).get("url", "")),
            "country": snippet.get("country", "N/A"),
            "description": snippet.get("description", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0))
        }
    except HttpError as e:
        if e.resp.status == 403:
            raise QuotaExceededError("YouTube API quota exceeded")
        return {}
    except ValueError as ve:
        raise ve
    except Exception:
        return {}

def get_recent_videos(channel_id):
    """
    Fetches videos published in the last 60 days.
    """
    if is_demo_mode():
        mock_vids = []
        titles = []
        if channel_id in MOCK_DETAILS:
            titles = MOCK_DETAILS[channel_id]["video_titles"]
        else:
            titles = [
                ("Awesome Demo Video #1", 45000, 2100, 120, 3),
                ("Awesome Demo Video #2", 68000, 3900, 230, 10),
                ("Awesome Demo Video #3", 112000, 8500, 410, 24)
            ]
            
        now = datetime.utcnow()
        for idx, (title, views, likes, comments, days_ago) in enumerate(titles):
            pub_date = (now - timedelta(days=days_ago)).isoformat() + "Z"
            # Assign mock category ID based on creator
            if channel_id == "UCBJycsmduvYELgTrujCgOPg":
                cat_id = "28"  # Tech
            elif channel_id == "UCX6OQ3DkcsbYNE6H8uQQuVA":
                cat_id = "24"  # Entertainment
            else:
                cat_id = "10"  # Music/Entertainment fallback
                
            mock_vids.append({
                "id": f"mock_vid_{channel_id}_{idx}",
                "title": title,
                "thumbnail": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=120&auto=format&fit=crop&q=60",
                "published_at": pub_date,
                "views": views,
                "likes": likes,
                "comments": comments,
                "category_id": cat_id
            })
        return mock_vids

    try:
        youtube = get_youtube_client()
        
        # Calculate 60 days ago date limit
        time_limit = (datetime.utcnow() - timedelta(days=60)).isoformat() + "Z"

        # Search for videos in the channel
        search_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            publishedAfter=time_limit,
            maxResults=50,
            order="date"
        ).execute()

        items = search_response.get("items", [])
        if not items:
            return []

        video_ids = [
            item["id"]["videoId"] 
            for item in items 
            if "videoId" in item["id"]
        ]
        
        if not video_ids:
            return []

        # Batch fetch statistics and snippets for these videos
        videos_response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()

        results = []
        for item in videos_response.get("items", []):
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            results.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", snippet.get("thumbnails", {}).get("default", {}).get("url", "")),
                "published_at": snippet.get("publishedAt", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "category_id": snippet.get("categoryId", "")
            })
        return results

    except HttpError as e:
        if e.resp.status == 403:
            raise QuotaExceededError("YouTube API quota exceeded")
        return []
    except ValueError as ve:
        raise ve
    except Exception:
        return []

