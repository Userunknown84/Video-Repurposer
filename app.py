import streamlit as st
import whisper
import os
import requests
import yt_dlp
import cv2
from moviepy.editor import VideoFileClip

st.title("🎬 Video Repurposer")
st.markdown("### 🎯 Turn long videos into viral reels instantly")

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# session state
if "video_path" not in st.session_state:
    st.session_state.video_path = None

uploaded_file = st.file_uploader("Upload video", type=["mp4", "mov"])
video_url = st.text_input("Paste video link (YouTube / direct mp4)")



@st.cache_resource
def load_model():
    return whisper.load_model("base")

def save_video(file):
    path = os.path.join("uploads", file.name)
    with open(path, "wb") as f:
        f.write(file.read())
    return path

def download_youtube_video(url):
    output_path = "uploads/youtube_video.%(ext)s"

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'extractor_args': {
            'youtube': {'player_client': ['android']}
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "uploads/youtube_video.mp4"
    except:
        return None

def download_direct_video(url):
    output_path = "uploads/direct_video.mp4"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, stream=True, headers=headers)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return output_path
    except:
        return None

def transcribe(video_path):
    model = load_model()
    result = model.transcribe(video_path)
    return result['segments']

def score_segment(seg):
    return (seg['end'] - seg['start']) + len(seg['text'].split()) * 0.5

# 🔥 FINAL REEL CREATION (NO ERRORS)
def create_reel(video_path, start, end, text):
    clip = VideoFileClip(video_path).subclip(start, end)

    # vertical crop
    w, h = clip.size
    new_w = int(h * 9 / 16)
    x_center = w // 2
    x1 = max(0, x_center - new_w // 2)
    x2 = x1 + new_w
    clip = clip.crop(x1=x1, x2=x2)

    temp_path = "outputs/temp.mp4"
    output_path = "outputs/final_reel.mp4"

    clip.write_videofile(temp_path, audio=True)

    cap = cv2.VideoCapture(temp_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    subtitle = text[:80]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # black box for subtitle
        cv2.rectangle(frame, (0, height-100), (width, height), (0, 0, 0), -1)

        # white text
        cv2.putText(
            frame,
            subtitle,
            (30, height-40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        out.write(frame)

    cap.release()
    out.release()

    return output_path

def generate_hook(text):
    return "🔥 " + text.strip().capitalize()



if uploaded_file:
    st.session_state.video_path = save_video(uploaded_file)
    st.video(st.session_state.video_path)

if video_url:
    if st.button("Fetch Video 🔗"):
        st.write("Downloading...")

        path = None
        if "youtube.com" in video_url or "youtu.be" in video_url:
            path = download_youtube_video(video_url)
            if path is None:
                st.error("YouTube blocked. Upload video instead.")
        else:
            path = download_direct_video(video_url)

        if path:
            st.session_state.video_path = path
            st.success("Video Ready ✅")
            st.video(path)


if st.session_state.video_path:
    if st.button("Process Video 🚀"):

        video_path = st.session_state.video_path

        st.write("🧠 Transcribing...")
        segments = transcribe(video_path)

        best_segment = max(segments, key=score_segment)

        start = best_segment['start']
        end = best_segment['end']
        text = best_segment['text']

        st.info(text)

        st.write("🎬 Creating Reel...")
        output_video = create_reel(video_path, start, end, text)

        hook = generate_hook(text)

        st.success("Done ✅")

        st.subheader("🔥 Hook")
        st.write(hook)

        st.subheader("🎬 Final Reel")
        st.video(output_video)