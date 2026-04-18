# 🎬  Video Repurposer

## 🚀 Overview

**Video Repurposer ** is an AI-powered video repurposing tool that converts long-form videos into short, engaging **reels/shorts** automatically.

It uses **Speech AI + Computer Vision** to:

* Identify the most impactful part of a video
* Convert it into a **vertical (9:16) format**
* Add **subtitles**
* Generate a **hook line**

👉 Perfect for content creators, educators, and social media marketing.

---

## 🎯 Problem Statement

Long videos are hard to consume and share. Creators need:

* Short clips
* Highlight moments
* Reel-ready content

Manual editing is time-consuming ❌

👉 **Solution:** Fully automated AI pipeline.

---

## 🧠 Features

* 🎥 Upload video or use video link
* 🧠 AI transcription using Whisper
* 🎯 Smart highlight detection
* 📱 Automatic vertical video (9:16) conversion
* ✍️ Subtitle generation (overlay)
* 🔥 Hook text generation
* ⚡ Fast processing with simple UI

---

## ⚙️ Tech Stack

* **Frontend:** Streamlit
* **AI Model:** OpenAI Whisper
* **Computer Vision:** OpenCV
* **Video Processing:** MoviePy
* **Downloader:** yt-dlp
* **Language:** Python

---

## 🔄 Pipeline

```
Input Video
   ↓
Transcription (Whisper)
   ↓
Highlight Detection
   ↓
Vertical Crop (Computer Vision)
   ↓
Subtitle Overlay (OpenCV)
   ↓
Hook Generation
   ↓
Final Reel Output
```

---

## 🖥️ Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/attentionx-ai.git
cd attentionx-ai
```

### 2. Install dependencies

```
pip install streamlit moviepy==1.0.3 openai-whisper yt-dlp requests opencv-python torch
```

### 3. Install FFmpeg

#### Mac:

```
brew install ffmpeg
```

#### Windows:

* Download FFmpeg
* Add it to system PATH

---

## ▶️ Run the App

```
streamlit run app.py
```

---

## 📸 Usage

1. Upload a video OR paste a video link
2. Click **Fetch Video** (if using link)
3. Click **Process Video 🚀**
4. Get:

   * 🎯 Highlight text
   * 🔥 Hook
   * 🎬 Final reel

---

## ⚠️ Notes

* YouTube links may fail due to platform restrictions
* Direct MP4 links and uploaded videos work best
* Use short videos for faster processing

---

## 🔮 Future Improvements

* 🎯 Multiple clip generation
* 🤖 AI-generated hooks (LLM integration)
* 🌍 Multi-language subtitles
* 😊 Emotion detection
* 🎵 Background music auto-sync

---

## 🏆 Hackathon Value

This project demonstrates:

* End-to-end AI pipeline
* Real-world problem solving
* Integration of AI + Computer Vision
* Automation of content creation

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

> “Turn long videos into viral reels instantly using AI.”
