import os
import random
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

# ১. পিক্সাবে থেকে ফ্রি ভিডিও ও সাউন্ড খোঁজা এবং ডাউনলোড করা
def download_pixabay_assets():
    api_key = os.environ.get('PIXABAY_API_KEY')
        video_keywords = ['satisfying', 'asmr+slime', 'soap+cutting', 'sand+cutting']
    keyword = random.choice(video_keywords)
    video_url = f"https://pixabay.com{api_key}&q={keyword}&per_page=10"
    
    video_data = requests.get(video_url).json()
    hits = video_data.get('hits', [])
    
    if len(hits) < 3:
        print("পর্যাপ্ত ভিডিও পাওয়া যায়নি।")
        return None, None
        
    chosen_hits = random.sample(hits, 3)
    video_files = []
    
    for i, hit in enumerate(chosen_hits):
        videos_dict = hit.get('videos', {})
        download_url = videos_dict.get('large', {}).get('url') or videos_dict.get('medium', {}).get('url')
        v_data = requests.get(download_url).content
        v_name = f"video_{i}.mp4"
        with open(v_name, 'wb') as f:
            f.write(v_data)
        video_files.append(v_name)
        
        audio_url = f"https://pixabay.com{api_key}&q=nature+relaxing&per_page=5"
    
    audio_data = requests.get(audio_url).json()
    audio_hits = audio_data.get('hits', [])
    
    audio_file = None
    if audio_hits:
        a_download_url = random.choice(audio_hits).get('audio')
        a_data = requests.get(a_download_url).content
        audio_file = "background.mp3"
        with open(audio_file, 'wb') as f:
            f.write(a_data)
            
    return video_files, audio_file

# ২. ভিডিওগুলো জোড়া লাগানো, জুম ও এডিট করা (Reused Content পলিসি এড়াতে)
def edit_and_process_video(video_files, audio_file):
    clips = []
    for file in video_files:
        clip = VideoFileClip(file)
        clip = clip.fx(lambda c: c.resize(1.1))
        clip = clip.speedx(0.95)
        clips.append(clip)
        
    final_video = concatenate_videoclips(clips, method="compose")
    
    if audio_file:
        bg_audio = AudioFileClip(audio_file).volumex(0.5)
        bg_audio = bg_audio.loop(duration=final_video.duration)
        final_video = final_video.set_audio(bg_audio)
        
    output_name = "final_output.mp4"
    final_video.write_videofile(output_name, codec="libx264", audio_codec="aac")
    
    for file in video_files:
        os.remove(file)
    if audio_file:
        os.remove(audio_file)
        
    return output_name

# ৩. ইউটিউবে সম্পূর্ণ অটোমেটিকভাবে ভিডিও আপলোড করা
def upload_to_youtube(video_path):
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN') # এটি কোনো নোটিফিকেশন ছাড়াই অটো কাজ করবে
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://googleapis.com",
        client_id=client_id,
        client_secret=client_secret
    )
    
    youtube = build('youtube', 'v3', credentials=creds)
    
    titles = ["Super Satisfying ASMR Video", "Relaxing Sand Cutting ASMR", "Oddly Satisfying Soap Slime ASMR"]
    body = {
        'snippet': {
            'title': random.choice(titles),
            'description': 'Enjoy this oddly satisfying and relaxing ASMR video! Perfect for sleep and relaxation.',
            'tags': ['ASMR', 'satisfying', 'relaxing', 'soap cutting', 'slime'],
            'categoryId': '24'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"ভিディオ আপলোড হচ্ছে: {int(status.progress() * 100)}%")
            
    print("ভিডিও সফলভাবে আপলোড হয়েছে!")
    os.remove(video_path)

if __name__ == "__main__":
    print("বটের কাজ শুরু হচ্ছে...")
    videos, audio = download_pixabay_assets()
    if videos:
        final_mp4 = edit_and_process_video(videos, audio)
        upload_to_youtube(final_mp4)
  
