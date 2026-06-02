"""RADIO DVA AI — Configuration"""

# Stream settings
ICECAST_HOST = "localhost"
ICECAST_PORT = 8888
ICECAST_MOUNT = "/radio.mp3"
ICECAST_SOURCE_PASS = "hackme"

# Radio branding
STATION_NAME = "RADIO DVA"
STATION_TAGLINE = "Двойная Волна — 50/50 Россия и Мир"

# AI settings
OPENAI_API_KEY = "sk-your-key-here"  # Replace with your key
OPENAI_MODEL = "gpt-4o"  # or gpt-3.5-turbo for cheaper

# DJ personalities
DJ_HOST = {
    "name": "Алекс",
    "voice": "ru-RU-DariyaNeural",  # Microsoft TTS voice
    "style": "энергичный, харизматичный, с чувством юмора",
    "catchphrases": [
        "С вами RADIO DVA — двойная волна позитива!",
        "Это Алекс, ваш ведущий, и я заряжен по полной!",
        "Двойная порция хорошей музыки — только здесь!",
    ]
}

DJ_CO_HOST = {
    "name": "Лина",
    "voice": "ru-RU-SvetlanaNeural",
    "style": "плавная, загадочная, с лёгкой иронией",
    "catchphrases": [
        "Привет, это Лина, оставайся с нами.",
        "Тёплый вечер на RADIO DVA — музыка для души.",
    ]
}

# Music settings
TRACK_DURATION_SEC = 10  # Demo: short tracks. Set to ~180 for real
DJ_INTRO_SEC = 4         # How long DJ talks before track
DJ_OUTRO_SEC = 3         # How long DJ talks after track

# Paths
TRACKS_DIR = "/root/Radio/ai_dj/tracks"
