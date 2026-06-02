# 🎧 RADIO DVA — AI-Powered Online Radio Station

**50/50 Russian & World hits — 24/7 Live with Virtual DJs**

## 🌟 Features

- **AI DJs**: Алекс (energetic) & Лина (smooth) — switch every 3 tracks
- **50/50 Music**: Equal rotation of Russian and World top hits
- **Live Streaming**: Direct audio streaming via HTTP (no Icecast needed)
- **Web Player**: Beautiful UI with vinyl animation, chat, track history
- **Chat**: Real-time listener chat
- **PWA**: Installable as mobile app
- **SEO-optimized**: Schema.org, Open Graph, sitemap, Yandex/Google verification
- **Ad Platform**: Dedicated advertising landing page with pricing

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────────────┐
│   Browser    │────▶│  API Server (:5050)  │
│  (HTML5 +    │     │                      │
│   React)     │     │  ┌────────────────┐  │
└──────────────┘     │  │  Static Files   │  │
                     │  │  (HTML/CSS/JS)  │  │
                     │  ├────────────────┤  │
                     │  │  API Endpoints  │  │
                     │  │  /api/now-playing│  │
                     │  │  /api/stream    │  │
                     │  │  /api/chat      │  │
                     │  ├────────────────┤  │
                     │  │  AI DJ Engine   │  │
                     │  │  (Background    │  │
                     │  │   Thread)       │  │
                     │  └────────────────┘  │
                     └──────────────────────┘
```

## 🚀 Quick Start

### Local Development
```bash
# Run the station
python3 run.py

# Open in browser
open http://localhost:5050
```

### Deploy to Render
```bash
./deploy.sh rnd_PuauSTOlQmzQEsaNnxgshFSHtzJk
```

## 📡 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/stream` | Live audio stream (MP3, chunked) |
| `/api/now-playing` | Current track & DJ info |
| `/api/stats` | Listener stats & uptime |
| `/api/hosts` | DJ profiles & on-air status |
| `/api/messages` | Chat messages |
| `/api/health` | Health check |

## 💰 Monetization

See [MONETIZATION.md](MONETIZATION.md) for:
- Audio ad pricing (from 5,000₽/week)
- Banner placement (from 3,000₽/week)
- Sponsorship packages
- Financial projections
- Sales channels

## 🛠️ Tech Stack

- **Backend**: Python (http.server, threading)
- **Streaming**: Chunked HTTP transfer encoding
- **Audio**: LAME MP3 encoding, WAV mixing
- **TTS**: Internal speech synthesis
- **Frontend**: HTML5, CSS3, Vanilla JS
- **Deployment**: Docker, Render.com

## 📁 Project Structure

```
├── api/              # API server + streaming
│   ├── server.py     # HTTP server (API + static files)
│   ├── stream_buffer.py  # Thread-safe audio buffer
│   └── broadcaster.py    # AI DJ background engine
├── ai_dj/            # AI DJ engine
│   ├── music.py      # Track scheduler (50/50)
│   ├── scripts.py    # DJ script templates
│   ├── tts.py        # Text-to-speech synthesis
│   └── mixer.py      # Audio mixing & encoding
├── css/              # Styles
├── js/               # Frontend
├── admin/            # Admin panel
├── pwa/              # Progressive Web App
├── assets/           # Icons & images
├── run.py            # Entry point
├── Dockerfile        # Container
└── render.yaml       # Render config
```

## 🎯 Roadmap

- [x] Core streaming engine
- [x] AI DJ with banter
- [x] Web player UI
- [x] PWA support
- [x] Monetization page
- [ ] Real TTS (ElevenLabs/OpenAI)
- [ ] Real music licensing
- [ ] Listener analytics
- [ ] Mobile apps
