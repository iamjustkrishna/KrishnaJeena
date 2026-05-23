import os
import json
import requests
from google import genai
from googleapiclient.discovery import build

# 1. Initialize API Clients
GEMINI_KEY = os.getenv("GEMINI_API_KEY_AI")
YOUTUBE_KEY = os.getenv("YOUTUBE_API_KEY")

if not GEMINI_KEY or not YOUTUBE_KEY:
    raise ValueError("Missing environment variables: Ensure GEMINI_API_KEY_AI and YOUTUBE_KEY are set.")

gemini_client = genai.Client(api_key=GEMINI_KEY)
youtube_client = build('youtube', 'v3', developerKey=YOUTUBE_KEY)

weeks = [
    {"num": 1, "topic": "Understanding AI", "context": "Fundamentals and core concepts"},
    {"num": 2, "topic": "Building AI Apps", "context": "Practical implementation and coding"},
    {"num": 3, "topic": "AI Agents", "context": "Advanced autonomous systems"},
    {"num": 4, "topic": "Launch & Monetize", "context": "Deployment and business models"}
]

all_videos = []

def get_real_youtube_video(query):
    """Searches YouTube and returns the first verified matching video."""
    try:
        search_response = youtube_client.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=1,
            safeSearch="moderate"
        ).execute()

        items = search_response.get("items", [])
        if not items:
            print(f"  ⚠ No YouTube video found for: {query}")
            return None

        video = items[0]
        video_id = video["id"]["videoId"]
        snippet = video["snippet"]

        return {
            "video_title": snippet["title"],
            "title": snippet["title"],
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
            "description": snippet["description"],
            "is_active": True
        }
    except Exception as e:
        print(f"  ✗ YouTube Search Failed for query '{query}': {e}")
        return None

# 2. Generate and Verify Curriculum
for week in weeks:
    print(f"\n🧠 Curating Week {week['num']}: {week['topic']}...")
    
    # Prompt Gemini for exact search queries instead of guessing links
    prompt = f"""You are an expert AI curriculum builder. For week {week['num']}: "{week['topic']}" 
Context: {week['context']}

Generate a list of the 4-5 best YouTube video search queries to locate top-tier, accurate tutorials on this topic.
Include specific channels (e.g., '3Blue1Brown', 'Andrej Karpathy', 'freeCodeCamp') or exact terms to ensure top quality.

Return ONLY a JSON list of strings (no markdown, no extra text):
[
  "Query 1",
  "Query 2",
  "Query 3",
  "Query 4"
]"""

    response = gemini_client.models.generate_content(
        model="gemini-3.5-flash", 
        contents=prompt
    )

    try:
        # Access response text using response.text
        queries = json.loads(response.text)
        print(f"  ✓ Gemini generated {len(queries)} search queries.")
        
        # Verify queries against YouTube Data API
        week_videos_count = 0
        for i, query in enumerate(queries):
            print(f"  🔍 Searching YouTube for: \"{query}\"...")
            video_data = get_real_youtube_video(query)
            
            if video_data:
                video_data.update({
                    "week_number": week['num'],
                    "tier_required": "foundational",
                    "sort_order": i
                })
                all_videos.append(video_data)
                week_videos_count += 1
                
        print(f"  ✓ Week {week['num']} Complete: {week_videos_count} verified videos added.")
        
    except json.JSONDecodeError:
        print(f"  ✗ Week {week['num']}: Failed to parse Gemini response: {response.text[:100]}")

# 3. Save output locally
os.makedirs("aibuilder", exist_ok=True)
with open("aibuilder/videos.json", "w") as f:
    json.dump({"videos": all_videos}, f, indent=2)
    print(f"\n🎉 Successfully saved {len(all_videos)} verified videos to aibuilder/videos.json")

# 4. Trigger website sync
sync_url = "https://www.aibuilder.space/api/learning/curated"
payload = {
    "action": "sync-github",
    "github_json_url": "https://raw.githubusercontent.com/iamjustkrishna/KrishnaJeena/refs/heads/main/aibuilder/videos.json"
}

try:
    sync_response = requests.post(sync_url, json=payload)
    print(f"📡 API Sync status: {sync_response.status_code}")
except Exception as e:
    print(f"✗ API Sync Failed: {e}")
