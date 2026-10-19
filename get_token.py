import os
from google_auth_oauthlib.flow import InstalledAppFlow

def generate_refresh_token():
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://google.com",
            "token_uri": "https://googleapis.com"
        }
    }
    
    # গুগলের থেকে স্থায়ী চাবি বা রিফ্রেশ টোকেন চাওয়ার সেটআপ
    flow = InstalledAppFlow.from_client_config(
        client_config, 
        scopes=["https://googleapis.com"]
    )
    
    # এটি গিটহাব লগ-এর ভেতর একটি লিংক তৈরি করে দেবে
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    print("\n--- গুরুত্বপূর্ণ ধাপ ---")
    print("নিচের লিংকে গিয়ে আপনার ইউটিউব জিমেইল সিলেক্ট করুন এবং পারমিশন দিন:")
    print(auth_url)
    print("------------------------\n")

if __name__ == "__main__":
    generate_refresh_token()
  
