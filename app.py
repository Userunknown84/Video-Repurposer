import streamlit as st
import whisper
import os
import yt_dlp
import time
import cv2
import random
from moviepy.editor import VideoFileClip

st.set_page_config(layout="centered")
st.title("🎬 AttentionX AI - Final Stable")

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

if "video_path" not in st.session_state:
    st.session_state.video_path = None

if "reels" not in st.session_state:
    st.session_state.reels = []

if "video_shown" not in st.session_state:
    st.session_state.video_shown = False


mode = st.radio("Select Input", ["Upload", "Link"])

# Upload
if mode == "Upload":
    file = st.file_uploader("Upload Video", type=["mp4"])
    if file:
        path = f"uploads/{int(time.time())}.mp4"
        with open(path, "wb") as f:
            f.write(file.read())

        st.session_state.video_path = path
        st.session_state.reels = []
        st.session_state.video_shown = False

# Link
if mode == "Link":
    url = st.text_input("Paste URL")
    if st.button("Fetch Video"):
        path = f"uploads/{int(time.time())}.mp4"
        with yt_dlp.YoutubeDL({'format': 'worst', 'outtmpl': path}) as ydl:
            ydl.download([url])

        st.session_state.video_path = path
        st.session_state.reels = []
        st.session_state.video_shown = False

if st.session_state.video_path and not st.session_state.video_shown:
    st.video(st.session_state.video_path)
    st.session_state.video_shown = True


@st.cache_resource
def load_model():
    return whisper.load_model("base")


def split_video(duration, clip_len):
    segments = []
    start = 0
    while start < duration:
        end = min(start + clip_len, duration)
        segments.append((start, end))
        start = end
    return segments


def transcribe_reel(video_path, start, end):
    clip = VideoFileClip(video_path).subclip(start, end)
    audio = f"uploads/temp_{int(time.time())}.wav"

    clip.audio.write_audiofile(audio, verbose=False, logger=None)
    clip.close()

    model = load_model()

    result = model.transcribe(audio, language="en", fp16=False)
    return result["text"].strip().capitalize()


def generate_thumbnail_variant(video_path, start, idx, variant):
    cap = cv2.VideoCapture(video_path)

    cap.set(cv2.CAP_PROP_POS_MSEC, (start + random.uniform(0, 2)) * 1000)
    ret, frame = cap.read()
    cap.release()

    path = f"outputs/thumb_{idx}_{variant}.jpg"

    if ret:
        texts = ["🔥 VIRAL", "🚀 TRENDING", "😲 MUST WATCH"]
        text = random.choice(texts)

        h, w = frame.shape[:2]
        pos = random.choice([(50,80), (50,h-50), (w//4,h//2)])

        cv2.putText(frame, text, pos,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5, (255,255,255), 3)

        cv2.imwrite(path, frame)

    return path


def create_reel(video_path, start, end, idx):
    clip = VideoFileClip(video_path).subclip(start, end)

    output = f"outputs/reel_{idx}_{int(time.time())}.mp4"

    clip.write_videofile(
        output,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return output


if st.session_state.video_path:

    st.subheader("⚙️ Controls")

    clip_len = st.slider("Clip Length (sec)", 20, 120, 60)
    max_clips = st.slider("Max Clips", 1, 8, 4)
    show_thumb = st.checkbox("📸 Enable Thumbnail Ideas")

    
    if st.button("🎬 Generate Reels"):

        st.session_state.reels = []

        clip = VideoFileClip(st.session_state.video_path)
        duration = clip.duration
        clip.close()

        segments = split_video(duration, clip_len)[:max_clips]

        for i, (start, end) in enumerate(segments):

            reel_path = create_reel(
                st.session_state.video_path,
                start,
                end,
                i
            )

            st.session_state.reels.append({
                "path": reel_path,
                "start": start,
                "end": end
            })

    
    for i, reel_data in enumerate(st.session_state.reels):

        st.markdown(f"### 🎬 Reel {i+1}")
        st.video(reel_data["path"])

        transcript_box = st.empty()
        thumb_box = st.empty()

        col1, col2, col3 = st.columns(3)

        # TRANSCRIBE
        with col1:
            if st.button("🎧 Transcribe", key=f"t_{i}"):

                text = transcribe_reel(
                    st.session_state.video_path,
                    reel_data["start"],
                    reel_data["end"]
                )

                st.session_state.reels[i]["text"] = text

        # THUMBNAIL
        with col2:
            if show_thumb:
                if st.button("📸 Ideas", key=f"th_{i}"):

                    thumbs = []
                    for v in range(3):
                        thumbs.append(
                            generate_thumbnail_variant(
                                st.session_state.video_path,
                                reel_data["start"],
                                i,
                                v
                            )
                        )

                    st.session_state.reels[i]["thumbs"] = thumbs

        # DOWNLOAD
        with col3:
            with open(reel_data["path"], "rb") as f:
                st.download_button(
                    "⬇️ Download",
                    f,
                    file_name=f"reel_{i+1}.mp4",
                    key=f"d_{i}"
                )

        # SHOW TRANSCRIPT
        if "text" in reel_data:
            with transcript_box:
                st.markdown("#### 📝 Transcript")
                st.text_area("", reel_data["text"], height=150)

                st.markdown("#### 🔥 Hook")
                st.write("🔥 " + reel_data["text"][:80])

        # SHOW THUMBS
        if "thumbs" in reel_data:
            with thumb_box:
                st.markdown("#### 📸 Thumbnail Ideas")
                cols = st.columns(len(reel_data["thumbs"]))
                for j, thumb in enumerate(reel_data["thumbs"]):
                    with cols[j]:
                        st.image(thumb)

        st.divider()