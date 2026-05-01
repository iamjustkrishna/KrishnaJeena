import os
 import json
 from google.generativeai import GenerativeAI

 # Initialize Gemini
 client = GenerativeAI(api_key=os.getenv("GEMINI_API_KEY"))

 weeks = [
     {"num": 1, "topic": "Understanding AI", "context": "Fundamentals and core concepts"},
     {"num": 2, "topic": "Building AI Apps", "context": "Practical implementation and coding"},
     {"num": 3, "topic": "AI Agents", "context": "Advanced autonomous systems"},
     {"num": 4, "topic": "Launch & Monetize", "context": "Deployment and business models"}
 ]

 all_videos = []

 for week in weeks:
     prompt = f"""You are an AI education curator. For week {week['num']}: "{week['topic']}" 
     Context: {week['context']}
     
     Recommend 4-5 best YouTube videos for learning this topic.
     Return ONLY this JSON format (no markdown, no extra text):
     [
       {{"title": "...", "youtube_url": "https://youtu.be/...", "description": "...", "week_number": {week['num']}, 
"tier_required": "foundational"}}
     ]"""

     response = client.models.generate_content(
         model="gemini-2.5-flash",
         contents=prompt
     )

     try:
         videos = json.loads(response.text)
         all_videos.extend(videos)
         print(f"✓ Week {week['num']}: {len(videos)} videos")
     except json.JSONDecodeError:
         print(f"✗ Week {week['num']}: Failed to parse")

 # Write to videos.json
 with open("videos.json", "w") as f:
     json.dump({"videos": all_videos}, f, indent=2)
     print(f"\n✓ Saved {len(all_videos)} videos to videos.json")

 # Trigger website sync
 import requests
 sync_url = "https://www.aibuilder.space/api/learning/curated"
 payload = {
     "action": "sync-github",
     "github_json_url": "https://raw.githubusercontent.com/iamjustkrishna/KrishnaJeena/refs/heads/main/aibuilder/videos.json"
 }
 response = requests.post(sync_url, json=payload)
 print(f"✓ API Sync: {response.status_code}")
