"""RADIO DVA AI — Configuration"""

# Radio branding
STATION_NAME = "RADIO DVA"
STATION_TAGLINE = "Двойная Волна — 50/50 Россия и Мир"

# AI settings (optional - built-in templates work without these)
OPENAI_API_KEY = ""  # Set your OpenAI key for smarter DJ scripts
OPENAI_MODEL = "gpt-4o"

# DJ personalities (used by scripting engine)
DJ_ALEX = {
    "name": "Алекс",
    "style": "энергичный, харизматичный, с чувством юмора",
}

DJ_LINA = {
    "name": "Лина",
    "style": "плавная, загадочная, с лёгкой иронией",
}

# Music settings
TRACK_DURATION_SEC = 10  # Demo duration (set to ~180 for real tracks)
DJ_INTRO_SEC = 4
DJ_OUTRO_SEC = 3

# Paths
TRACKS_DIR = "/root/Radio/ai_dj/tracks"
