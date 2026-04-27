import streamlit as st
import whisper
import os
import yt_dlp
import time
import cv2
import random
import requests
import json
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Video Repurposer", page_icon="🎬", layout="centered")

st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem; }
    .subtitle { color: #888; font-size: 1rem; margin-bottom: 1.5rem; }
    .reel-header {
        background: #f8f9fa; border-radius: 8px;
        padding: 8px 14px; margin: 1rem 0 0.5rem 0; font-weight: 600;
    }
    .success-msg {
        background: #e6f9f0; border-left: 4px solid #28a745;
        border-radius: 0 8px 8px 0; padding: 10px 14px;
        font-size: 0.9rem; color: #155724;
    }
    .history-card {
        background: #f8f9fa; border-radius: 8px; padding: 10px 14px;
        margin-bottom: 8px; font-size: 0.85rem;
        border-left: 3px solid #4a6cf7;
    }
    .tag-pill {
        display: inline-block; background: #e8f4fd; color: #1a6fa8;
        border-radius: 20px; padding: 2px 10px; font-size: 0.78rem;
        margin: 2px; border: 1px solid #b3d9f5;
    }
    .tour-box {
        background: #f0f4ff; border: 1.5px dashed #4a6cf7;
        border-radius: 10px; padding: 14px 18px; margin-bottom: 1rem;
        font-size: 0.9rem; color: #1a2a6c;
    }
    .step-badge {
        display: inline-block; background: #4a6cf7; color: white;
        border-radius: 50%; width: 20px; height: 20px;
        text-align: center; line-height: 20px; font-size: 12px;
        font-weight: bold; margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)


os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


defaults = {
    "video_path": None,
    "reels": [],
    "video_shown": False,
    "clip_history": [],   
    "tour_done": False,
    "undo_stack": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


if not st.session_state.tour_done:
    st.markdown("""
    <div class="tour-box">
        <strong>👋 Welcome to Video Repurposer!</strong> — Quick guide:<br><br>
        <span class="step-badge">1</span> <b>Upload</b> an MP4 or paste a video URL<br>
        <span class="step-badge">2</span> Pick a <b>platform preset</b> (Reels / Shorts) or set custom length<br>
        <span class="step-badge">3</span> Click <b>Generate Reels</b> to split your video into clips<br>
        <span class="step-badge">4</span> For each clip → <b>Transcribe</b> → <b>Hashtags</b> → <b>Thumbnails</b> → <b>Download</b><br>
        <span class="step-badge">5</span> <b>Trim</b> clips manually · View <b>History</b> in sidebar
    </div>
    """, unsafe_allow_html=True)
    if st.button("✅ Got it! Hide tour"):
        st.session_state.tour_done = True
        st.rerun()
    st.divider()


st.markdown('<div class="main-title">🎬 Video Repurposer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Turn any long video into short clips </div>', unsafe_allow_html=True)
st.divider()


with st.sidebar:
    st.markdown("## 📋 Clip History")
    if not st.session_state.clip_history:
        st.info("No clips yet. Generate reels to see history here.")
    else:
       
        to_delete = None
        for idx, h in enumerate(st.session_state.clip_history):
            st.markdown(
                f'<div class="history-card">'
                f'🎬 <b>Reel {h["reel_num"]}</b> · {h["start"]}s – {h["end"]}s<br>'
                f'📁 {h["filename"]}'
                f'</div>',
                unsafe_allow_html=True
            )
            
            if os.path.exists(h["path"]):
                st.video(h["path"])
            # Delete button for this clip
            if st.button(f"🗑️ Delete Reel {h['reel_num']}", key=f"hist_del_{idx}"):
                to_delete = idx

        if to_delete is not None:
            
            removed = st.session_state.clip_history.pop(to_delete)
        
            st.session_state.reels = [
                r for r in st.session_state.reels
                if r["path"] != removed["path"]
            ]
            st.rerun()

        st.divider()
        if st.button("🗑️ Clear All History"):
            st.session_state.clip_history = []
            st.rerun()

    st.divider()
    st.markdown("## ↩️ Undo")
    if st.session_state.undo_stack:
        last = st.session_state.undo_stack[-1]
        st.caption(f"Last: {last['action']}")
        if st.button("↩️ Undo Last Action"):
            action = st.session_state.undo_stack.pop()
            if action["action"] == "delete_reel":
                st.session_state.reels.insert(action["index"], action["data"])
            elif action["action"] == "trim_reel":
                st.session_state.reels[action["index"]] = action["data"]
            st.rerun()
    else:
        st.caption("Nothing to undo.")


mode = st.radio("Select Input Method", ["📂 Upload a file", "🔗 Paste a link"], horizontal=True)

if mode == "📂 Upload a file":
    file = st.file_uploader("Upload your video (MP4)", type=["mp4"])
    if file:
        path = f"uploads/{int(time.time())}.mp4"
        with st.spinner("Saving uploaded video…"):
            with open(path, "wb") as f:
                f.write(file.read())
        st.session_state.video_path = path
        st.session_state.reels = []
        st.session_state.video_shown = False
        st.success("✅ Video uploaded successfully!")

if mode == "🔗 Paste a link":
    url = st.text_input("Paste a YouTube or social media video URL")
    if st.button("⬇️ Fetch Video"):
        if not url.strip():
            st.error("⚠️ Please enter a valid URL before fetching.")
        else:
            path = f"uploads/{int(time.time())}.mp4"
            try:
                with st.spinner("Downloading video… this may take a moment ⏳"):
                    with yt_dlp.YoutubeDL({'format': 'worst', 'outtmpl': path}) as ydl:
                        ydl.download([url])
                st.session_state.video_path = path
                st.session_state.reels = []
                st.session_state.video_shown = False
                st.success("✅ Video downloaded successfully!")
            except Exception as e:
                st.error(f"❌ Could not download video. Check the URL.\n\nDetails: {e}")

if st.session_state.video_path and not st.session_state.video_shown:
    st.markdown("**Preview:**")
    st.video(st.session_state.video_path)
    st.session_state.video_shown = True

if st.session_state.video_path:
    if st.button("🔄 Start Over / Clear", help="Remove current video and reset"):
        st.session_state.video_path = None
        st.session_state.reels = []
        st.session_state.video_shown = False
        st.rerun()


@st.cache_resource
def load_model():
    return whisper.load_model("base")


RANDOM_CAPTIONS = [
    "You won't believe this 😱", "This changed everything 🔥",
    "Watch till the end! 👀", "Nobody talks about this 🤫",
    "This is going viral 🚀", "POV: You discovered this 💡",
    "Drop everything and watch 🎯", "Real talk — listen up 🎙️",
]
RANDOM_HASHTAGS = [
    "#viral", "#trending", "#reels", "#shorts", "#fyp",
    "#explore", "#content", "#creator", "#video", "#socialmedia",
    "#instagood", "#youtube", "#instagram", "#like", "#share",
]

def call_claude(prompt, max_tokens=300):
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"].strip()
    except Exception:
        pass
    return None

def generate_ai_captions(transcript_text):
    prompt = (
        "You are a social media expert. Based on this transcript, generate exactly 3 short "
        "catchy thumbnail captions for Instagram Reels / YouTube Shorts.\n"
        "Rules: each caption under 8 words, 1 emoji each, curiosity-driven.\n"
        "Return ONLY a valid JSON array of exactly 3 strings, no extra text.\n"
        'Example: ["Caption one 🔥", "Caption two 💡", "Caption three 😱"]\n'
        f"Transcript: {transcript_text[:500]}"
    )
    result = call_claude(prompt, 200)
    if result:
        try:
            # Strip markdown code fences if present
            clean = result.strip().strip("```json").strip("```").strip()
            captions = json.loads(clean)
            if isinstance(captions, list) and len(captions) >= 3:
                return captions[:3], "ai"
        except Exception:
            pass
    return random.sample(RANDOM_CAPTIONS, 3), "random"

def generate_ai_hashtags(transcript_text):
    prompt = (
        "You are a social media expert. Based on this transcript, generate exactly 10 relevant "
        "hashtags for Instagram/YouTube Shorts.\n"
        "Rules: mix popular + niche tags, all start with #.\n"
        "Return ONLY a valid JSON array of 10 strings, no extra text.\n"
        'Example: ["#tag1", "#tag2", "#tag3"]\n'
        f"Transcript: {transcript_text[:500]}"
    )
    result = call_claude(prompt, 200)
    if result:
        try:
            clean = result.strip().strip("```json").strip("```").strip()
            tags = json.loads(clean)
            if isinstance(tags, list) and len(tags) >= 5:
                return tags[:10], "ai"
        except Exception:
            pass
    return random.sample(RANDOM_HASHTAGS, 10), "random"


def split_video(duration, clip_len):
    segments, start = [], 0
    while start < duration:
        segments.append((start, min(start + clip_len, duration)))
        start += clip_len
    return segments

def transcribe_reel(video_path, start, end, language="en"):
    try:
        clip = VideoFileClip(video_path).subclip(start, end)
        audio = f"uploads/temp_{int(time.time())}.wav"
        clip.audio.write_audiofile(audio, verbose=False, logger=None)
        clip.close()
        model = load_model()
        lang = language if language else None
        result = model.transcribe(audio, language=lang, fp16=False)
        return result["text"].strip().capitalize()
    except Exception as e:
        return f"Transcription failed: {e}"

def generate_thumbnail_variant(video_path, start, transcript_text, idx, variant):
    try:
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_MSEC, (start + random.uniform(0, 2)) * 1000)
        ret, frame = cap.read()
        cap.release()
        path = f"outputs/thumb_{idx}_{variant}_{int(time.time())}.jpg"
        if ret:
            words = transcript_text.split() if transcript_text and len(transcript_text) > 10 else []
            if len(words) > 5:
                text = " ".join(words[:5]) + "..."
            elif words:
                text = transcript_text[:40]
            else:
                text = f"Clip {idx + 1}"
            h, w = frame.shape[:2]
            pos = [(50, 80), (50, h - 60), (w // 4, h // 2)][variant % 3]
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
            cv2.rectangle(frame, (pos[0]-8, pos[1]-th-8), (pos[0]+tw+8, pos[1]+8), (0, 0, 0), -1)
            cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.imwrite(path, frame)
        return path
    except Exception:
        return None

def create_reel(video_path, start, end, idx):
    try:
        clip = VideoFileClip(video_path).subclip(start, end)
        output = f"outputs/reel_{idx}_{int(time.time())}.mp4"
        clip.write_videofile(output, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clip.close()
        return output
    except Exception as e:
        st.error(f"❌ Failed to create reel {idx}: {e}")
        return None


if st.session_state.video_path:
    st.divider()
    st.subheader("⚙️ Clip Settings")

    # Platform Presets (TikTok removed)
    st.markdown("**📱 Platform Preset**")
    p1, p2, p3 = st.columns(3)
    with p1:
        if st.button("📸 Instagram Reels\n~45s"):
            st.session_state["preset_len"] = 45
            st.session_state["preset_clips"] = 4
            st.rerun()
    with p2:
        if st.button("▶️ YouTube Shorts\n~60s"):
            st.session_state["preset_len"] = 55
            st.session_state["preset_clips"] = 4
            st.rerun()
    with p3:
        if st.button("🎬 Long Form\n~2 min"):
            st.session_state["preset_len"] = 120
            st.session_state["preset_clips"] = 3
            st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        clip_len = st.slider(
            "Clip Length (seconds)", 10, 180,
            st.session_state.get("preset_len", 60),
            help="45s = Instagram Reels · 60s = YouTube Shorts"
        )
    with col_b:
        max_clips = st.slider(
            "Max Number of Clips", 1, 10,
            st.session_state.get("preset_clips", 4),
            help="How many clips to extract from the video."
        )


    st.markdown("**🌐 Transcription Language**")
    lang_options = {
        "English": "en", "Hindi": "hi", "Spanish": "es",
        "French": "fr", "German": "de", "Arabic": "ar",
        "Portuguese": "pt", "Japanese": "ja", "Auto Detect": None
    }
    selected_lang_name = st.selectbox(
        "Language spoken in the video",
        list(lang_options.keys()), index=0,
        help="Select the language for accurate transcription."
    )
    selected_lang = lang_options[selected_lang_name]

    show_thumb = st.checkbox(
        "📸 Enable Thumbnail Ideas",
        help="Generate thumbnail frames with AI captions for each clip."
    )

    if st.button("🎬 Generate Reels", type="primary"):
        st.session_state.reels = []
        try:
            clip = VideoFileClip(st.session_state.video_path)
            duration = clip.duration
            clip.close()
        except Exception as e:
            st.error(f"❌ Could not read video: {e}")
            st.stop()

        segments = split_video(duration, clip_len)[:max_clips]
        progress = st.progress(0, text="Starting…")

        for i, (start, end) in enumerate(segments):
            progress.progress(
                int((i / len(segments)) * 100),
                text=f"Creating clip {i+1} of {len(segments)}…"
            )
            with st.spinner(f"⏳ Generating Reel {i+1}…"):
                reel_path = create_reel(st.session_state.video_path, start, end, i)
            if reel_path:
                st.session_state.reels.append({
                    "path": reel_path,
                    "start": start,
                    "end": end
                })
                # Save to history (with path for sidebar preview)
                st.session_state.clip_history.append({
                    "reel_num": i + 1,
                    "start": int(start),
                    "end": int(end),
                    "filename": f"reel_{i+1}.mp4",
                    "path": reel_path,
                })

        progress.progress(100, text="✅ All reels generated!")
        st.markdown(
            '<div class="success-msg">🎉 Done! Scroll down to view, transcribe, or download your clips.</div>',
            unsafe_allow_html=True
        )

    
    for i, reel_data in enumerate(st.session_state.reels):

        st.markdown(
            f'<div class="reel-header">🎬 Reel {i+1} &nbsp;·&nbsp; '
            f'{int(reel_data["start"])}s – {int(reel_data["end"])}s</div>',
            unsafe_allow_html=True
        )

       
        with st.expander(f"✂️ Trim Reel {i+1} manually", expanded=False):
            try:
                fc = VideoFileClip(st.session_state.video_path)
                max_dur = fc.duration
                fc.close()
            except Exception:
                max_dur = reel_data["end"]

            tc1, tc2 = st.columns(2)
            with tc1:
                new_start = st.number_input(
                    "Start (sec)", min_value=0.0,
                    max_value=float(reel_data["end"] - 1),
                    value=float(reel_data["start"]),
                    step=0.5, key=f"ts_{i}"
                )
            with tc2:
                new_end = st.number_input(
                    "End (sec)",
                    min_value=float(reel_data["start"] + 1),
                    max_value=float(max_dur),
                    value=float(reel_data["end"]),
                    step=0.5, key=f"te_{i}"
                )
            if st.button("✂️ Apply Trim", key=f"trim_{i}"):
                if new_end <= new_start:
                    st.error("End time must be greater than start time!")
                else:
                    with st.spinner("Trimming…"):
                        st.session_state.undo_stack.append({
                            "action": "trim_reel",
                            "index": i,
                            "data": reel_data.copy()
                        })
                        trimmed = create_reel(
                            st.session_state.video_path, new_start, new_end, f"{i}t"
                        )
                        if trimmed:
                            st.session_state.reels[i]["path"] = trimmed
                            st.session_state.reels[i]["start"] = new_start
                            st.session_state.reels[i]["end"] = new_end
                            st.success("✅ Clip trimmed!")
                            st.rerun()

        st.video(reel_data["path"])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🎧 Transcribe", key=f"t_{i}",
                         help=f"Extract speech ({selected_lang_name})"):
                with st.spinner(f"Transcribing in {selected_lang_name}…"):
                    text = transcribe_reel(
                        st.session_state.video_path,
                        reel_data["start"], reel_data["end"],
                        language=selected_lang
                    )
                st.session_state.reels[i]["text"] = text
                st.rerun()  # Force re-render to show transcript immediately

        with col2:
            if st.button("# Hashtags", key=f"ht_{i}", help="Generate AI hashtags"):
                with st.spinner("Generating hashtags…"):
                    tags, src = generate_ai_hashtags(reel_data.get("text", ""))
                if not reel_data.get("text"):
                    st.info("ℹ️ Transcribe first for more relevant hashtags!")
                st.session_state.reels[i]["hashtags"] = tags
                st.session_state.reels[i]["hashtag_source"] = src
                st.rerun()  # Force re-render

        with col3:
            if show_thumb:
                if st.button("📸 Thumbnails", key=f"th_{i}", help="Generate thumbnail ideas"):
                    with st.spinner("Generating thumbnails…"):
                        thumbs = []
                        for v in range(3):
                            t = generate_thumbnail_variant(
                                st.session_state.video_path,
                                reel_data["start"],
                                reel_data.get("text", ""),
                                i, v
                            )
                            if t:
                                thumbs.append(t)
                    st.session_state.reels[i]["thumbs"] = thumbs
                    if f"captions_{i}" in st.session_state:
                        del st.session_state[f"captions_{i}"]
                    st.rerun()  # Force re-render

        with col4:
            with open(reel_data["path"], "rb") as f:
                st.download_button(
                    "⬇️ Download", f,
                    file_name=f"reel_{i+1}.mp4",
                    key=f"d_{i}", help="Save this clip to your device"
                )

        
        if "text" in reel_data:
            st.markdown("#### 📝 Transcript")
            st.text_area("", reel_data["text"], height=100, key=f"ta_{i}")
            hook = reel_data["text"][:80] + ("…" if len(reel_data["text"]) > 80 else "")
            st.markdown("**💡 Suggested Hook — click to copy:**")
            st.code(hook, language=None)

        
        if "hashtags" in reel_data:
            st.markdown("#### # Hashtags")
            src = reel_data.get("hashtag_source", "random")
            badge = "✨ AI Generated" if src == "ai" else "🎲 Smart Random"
            badge_bg = "#e6f9f0; color:#155724" if src == "ai" else "#fff3cd; color:#856404"
            st.markdown(
                f"<span style='background:{badge_bg}; font-size:0.75rem; "
                f"padding:3px 10px; border-radius:20px; font-weight:600;'>{badge}</span>",
                unsafe_allow_html=True
            )
            tags_html = " ".join(
                [f'<span class="tag-pill">{t}</span>' for t in reel_data["hashtags"]]
            )
            st.markdown(f"<div style='margin-top:8px;'>{tags_html}</div>", unsafe_allow_html=True)
            st.markdown("**Copy all hashtags:**")
            st.code(" ".join(reel_data["hashtags"]), language=None)

            if st.button("🔄 Regenerate Hashtags", key=f"regen_ht_{i}"):
                with st.spinner("Generating…"):
                    tags, src = generate_ai_hashtags(reel_data.get("text", ""))
                st.session_state.reels[i]["hashtags"] = tags
                st.session_state.reels[i]["hashtag_source"] = src
                st.rerun()

       
        if "thumbs" in reel_data:
            st.markdown("#### 📸 Thumbnail Ideas")
            transcript_text = reel_data.get("text", "")
            cap_key = f"captions_{i}"
            src_key = f"cap_src_{i}"

            if cap_key not in st.session_state:
                with st.spinner("🤖 Generating AI captions…"):
                    captions, cap_src = generate_ai_captions(transcript_text)
                st.session_state[cap_key] = captions
                st.session_state[src_key] = cap_src

            captions = st.session_state[cap_key]
            cap_src = st.session_state.get(src_key, "random")
            badge = "✨ AI Generated Captions" if cap_src == "ai" else "🎲 Smart Random Captions"
            badge_bg = "#e6f9f0; color:#155724" if cap_src == "ai" else "#fff3cd; color:#856404"
            st.markdown(
                f"<span style='background:{badge_bg}; font-size:0.75rem; "
                f"padding:3px 10px; border-radius:20px; font-weight:600;'>{badge}</span>",
                unsafe_allow_html=True
            )
            st.markdown("")

            thumb_cols = st.columns(len(reel_data["thumbs"]))
            for j, thumb in enumerate(reel_data["thumbs"]):
                with thumb_cols[j]:
                    st.image(thumb)
                    caption = captions[j] if j < len(captions) else f"Option {j+1}"
                    st.markdown(
                        f"<div style='background:#f0f4ff; border-radius:8px; padding:8px 10px;"
                        f"font-size:0.82rem; color:#1a1a2e; text-align:center; margin-top:6px;"
                        f"border:1px solid #c5d0f5; line-height:1.5;'>"
                        f"<b>Caption {j+1}</b><br>{caption}</div>",
                        unsafe_allow_html=True
                    )

            if st.button("🔄 Regenerate Captions", key=f"regen_cap_{i}"):
                del st.session_state[cap_key]
                st.rerun()

     
        if st.button(f"🗑️ Delete Reel {i+1}", key=f"del_{i}"):
            st.session_state.undo_stack.append({
                "action": "delete_reel",
                "index": i,
                "data": st.session_state.reels[i]
            })
            st.session_state.reels.pop(i)
            st.rerun()

        st.divider()


st.markdown(
    "<div style='text-align:center; color:#aaa; font-size:0.8rem; margin-top:2rem;'>"
    "Video Repurposer · Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)