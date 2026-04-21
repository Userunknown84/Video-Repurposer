# 🎬 Video Repurposer

## 🚀 Overview

**Video Repurposer* is an AI-powered  repurposing tool that transforms long-form videos into short, engaging **reels/shorts** automatically.

It combines **Speech AI + Computer Vision + Human-Computer Interaction (HCI)** to deliver a fast, interactive, and user-friendly experience.

👉 Built for content creators, students, marketers, and educators.

---

## 🎯 Problem Statement

Long videos are difficult to:

* consume quickly
* share on social media
* convert into engaging content

Manual editing is:

* time-consuming ❌
* skill-dependent ❌

👉 **Solution:** A fully automated AI-powered system that generates reel-ready content instantly.

---

## 🧠 Key Features

### 🎥 Input Options

* Upload video
* Paste video link (YouTube / direct)

### 🎬 Reel Generation

* Automatic video splitting (user-defined duration)
* No duplicate segments (sequential clips)
* Multiple reels from a single video

### 🧠 AI Capabilities

* 🎧 Reel-wise transcription (on demand)
* ✍️ Clean English subtitles (Whisper)
* 🔥 Hook generation for engagement

### 📱 Video Optimization

* Vertical (9:16) conversion
* Face-centered smart cropping (Computer Vision)
* Subtitle overlay

### 📸 Thumbnail Intelligence

* Generate **multiple thumbnail ideas**
* Different styles, positions, and frames
* Helps users choose best visual

### 🧩 HCI Enhancements

* User-controlled actions (no forced processing)
* Preview-first design (video → then actions)
* Clean, centered UI layout
* Optional features (transcribe, thumbnails)
* Stable playback (no UI flicker)

---

## ⚙️ Tech Stack

* **Frontend/UI:** Streamlit
* **Speech AI:** OpenAI Whisper
* **Computer Vision:** OpenCV
* **Video Processing:** MoviePy
* **Downloader:** yt-dlp
* **Language:** Python

---

## 🔄 System Pipeline

```
Input Video
   ↓
Optional Transcription (Whisper)
   ↓
Video Segmentation (User-controlled)
   ↓
Face Detection & Smart Crop
   ↓
Subtitle Generation
   ↓
Thumbnail Variations
   ↓
Reel Output
```

---

## 🖥️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Userunknown84/Video-Repurposer
cd attentionx-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

#### Mac

```bash
brew install ffmpeg
```

#### Windows

* Download FFmpeg
* Add it to system PATH

---

## ▶️ Run the App

```bash
streamlit run app.py
```

---

## 📸 Usage

1. Upload video OR paste link
2. Click **Fetch Video** (for links)
3. Click **Generate Reels 🎬**
4. For each reel:

   * 🎧 Transcribe (optional)
   * 📸 Generate Thumbnail Ideas
   * ⬇️ Download

---

## ⚠️ Notes

* YouTube downloads may fail due to platform restrictions
* Direct MP4 links work best
* Processing time depends on video length
* Whisper runs on CPU → may take time

---

## 🌐 Deployment

🔗 **Live App:** *[https://video-repurposer.onrender.com/]*

---

## 🔮 Future Improvements

* 🤖 AI-powered hook generation (LLM-based)
* 🎯 Viral clip scoring (ML-based)
* 🌍 Multi-language subtitles
* 😊 Emotion detection
* 🎵 Auto background music sync
* 📊 Timeline-based clip selection

---

## 👨‍💻 Author

**Aditya Sharma**

---

## ⭐ Acknowledgements

* OpenAI Whisper
* OpenCV
* MoviePy
* Streamlit

---

## 💡 Tagline

> “Turn long videos into viral reels with AI — faster, smarter, and easier.”
