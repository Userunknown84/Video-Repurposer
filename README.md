# 🎬 Video Repurposer

## 🚀 Overview

**Video Repurposer** is an AI-powered video repurposing tool that transforms long-form videos into short, engaging **reels/shorts** automatically.

It combines **Speech AI + Computer Vision + Human-Computer Interaction (HCI)** to deliver a fast, interactive, and user-friendly experience.

👉 Built for content creators, students, marketers, and educators.

---

##Deployment Link: https://video-repurposer.onrender.com/


## 🎯 Problem Statement

Long videos are difficult to:

- consume quickly
- share on social media
- convert into engaging content

Manual editing is:

- time-consuming ❌
- skill-dependent ❌

👉 **Solution:** A fully automated AI-powered system that generates reel-ready content instantly.

---

## 🧠 Key Features

### 🎥 Input Options
- Upload MP4 video directly
- Paste video URL (YouTube / direct link)

### 🎬 Reel Generation
- Automatic video splitting (user-defined duration)
- Platform presets: Instagram Reels, YouTube Shorts, Long Form
- Multiple reels from a single video

### 🧠 AI Capabilities
- 🎧 Reel-wise transcription (Whisper — on demand)
- 🔥 Hook generation from transcript
- 🤖 AI-generated thumbnail captions (Claude API)
- # AI-generated hashtags (Claude API with smart random fallback)
- 🌐 Multi-language transcription (English, Hindi, Spanish, French, German, Arabic, Portuguese, Japanese, Auto)

### 📸 Thumbnail Intelligence
- Generate 3 thumbnail frame options per reel
- AI-generated captions below each thumbnail
- Regenerate captions with one click

### ✂️ Manual Clip Trimmer
- Set custom start/end time for any reel
- Undo trim with one click

### 🧩 HCI Enhancements
- 📋 Clip History (sidebar) — view, preview, and delete past clips
- ↩️ Undo last action (delete or trim)
- 🗺️ Onboarding tour for first-time users
- User-controlled actions (no forced processing)
- Preview-first design
- Stable playback with no UI flicker
- Clean, centered layout

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Speech AI | OpenAI Whisper |
| Caption & Hashtag AI | Claude API (Anthropic) |
| Computer Vision | OpenCV |
| Video Processing | MoviePy |
| Video Downloader | yt-dlp |
| Language | Python 3.10+ |

---

## 🔄 System Pipeline

```
Input Video (Upload / URL)
        ↓
Video Segmentation (User-controlled length & count)
        ↓
Reel Creation (MoviePy)
        ↓
Optional: Transcription (Whisper)
        ↓
Optional: AI Hashtags (Claude API)
        ↓
Optional: Thumbnail Ideas + AI Captions (OpenCV + Claude API)
        ↓
Download Reel / Copy Caption / Copy Hashtags
```

---

## 🖥️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Userunknown84/Video-Repurposer
cd Video-Repurposer
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Mac:**
```bash
brew install ffmpeg
```

**Windows:**
- Download from https://ffmpeg.org/download.html
- Add `ffmpeg` to your system PATH

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 📸 Usage

1. Open the app in your browser
2. Upload a video **or** paste a URL
3. Choose a **platform preset** (Reels / Shorts / Long Form) or set custom length
4. Select **transcription language**
5. Click **🎬 Generate Reels**
6. For each reel:
   - 🎧 **Transcribe** → get transcript + suggested hook
   - **# Hashtags** → get 10 AI-generated hashtags (copy with one click)
   - 📸 **Thumbnails** → get 3 thumbnail frames with AI captions
   - ✂️ **Trim** → manually adjust start/end time
   - ⬇️ **Download** the clip
7. View all clips in **📋 Clip History** (sidebar)

---

## ⚠️ Notes

- YouTube downloads may fail due to platform restrictions — direct MP4 links work best
- Whisper runs on CPU → transcription may take 30–60 seconds per clip
- Claude API requires an active Anthropic API key set in the environment
- Processing time depends on video length and hardware


---

## 🔮 Future Improvements

- 🎯 Viral clip scoring (ML-based engagement prediction)
- 😊 Emotion detection for clip selection
- 🎵 Auto background music sync
- 📊 Timeline-based visual clip selector
- 📱 Vertical (9:16) auto-crop for mobile formats
- 🌍 Subtitle overlay on exported reels

---

## 👨‍💻 Author

**Aditya Sharma**



---

## 💡 Tagline

> "Turn long videos into viral reels with AI — faster, smarter, and easier."
