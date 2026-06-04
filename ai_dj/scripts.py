"""RADIO DVA AI — Script Generator with human-like DJ templates."""
import random, os, json, re

# ===== ALEX (male, energetic) =====
DJ_ALEX = {
    "name": "Алекс",
    "intro_templates": [
        "RADIO DVA на связи! {name} у микрофона, и мы начинаем мощный отрезок. Слушаем — {track} от {artist}!",
        "Йо! Это {name} с RADIO DVA. Ловите трек: {track} — {artist}. Погнали!",
        "В эфире {name}! Двойная волна заряжает. Прямо сейчас: {track}, {artist}. Огонь!",
        "С вами {name} и RADIO DVA! Очередной хит в нашей коллекции: {track} — {artist}. Не выключай!",
        "Как дела, слушатели? {name} приветствует! Слушаем {track} от {artist}. Лучшее из лучшего!",
        "А вот и свежий трек! {name} для вас постарался. {track} — {artist}, оцените!",
    ],
    "outro_templates": [
        "Это был {track} от {artist}. Как тебе? Пиши в чат! {name} был с тобой.",
        "{track} — {artist}. Классный трек, правда? {name} провожает, но мы ещё вернёмся!",
        "Зарядились? {track} — {artist}. Это {name}, остаёмся на RADIO DVA!",
        "Музыка продолжается! {track} от {artist} только что прозвучал. {name} с вами был.",
        "Отличный трек! {track} — {artist}. Не переключайся — дальше будет ещё интереснее.",
    ],
    "mid_templates": [
        "Знаете, что говорят? Музыка лечит. А мы сегодня лечим хитами!",
        "Кстати, мой любимый факт: этот трек взорвал чарты в 20 странах. А теперь он играет у нас!",
        "Настроение — огонь! И погода за окном не важна, у нас своя атмосфера.",
        "Говорят, лучшая музыка — та, что играет прямо сейчас. А у нас она играет!",
        "Слышали новость? RADIO DVA — это единственное радио, где играют только хиты. Без шуток!",
    ],
    "jokes": [
        "Почему диджей не ходит в спортзал? Потому что он и так качает!",
        "Что сказал динамик, когда его спросили про громкость? — 'Мне нечего скрывать!'",
        "Музыкант упал со сцены и сказал: 'Я просто решил взять нижнюю ноту!'",
    ],
    "time_greetings": {
        "morning": "Доброе утро! Просыпаемся с RADIO DVA!",
        "afternoon": "Добрый день! RADIO DVA продолжает вещание.",
        "evening": "Добрый вечер! RADIO DVA с вами до самой ночи.",
        "night": "Ночной эфир! RADIO DVA не спит — играет лучшее.",
    },
    "genre_specific": {
        "rus": "Русская музыка — это душа! Оцените этот трек.",
        "world": "Мировые хиты звучат на RADIO DVA. Ловите!",
        "hiphop": "Хип-хоп волна на RADIO DVA! Бит качает.",
        "classical": "Классика — это вечно. Окунитесь в атмосферу.",
        "jazz": "Джаз и блюз для души. Расслабьтесь и слушайте.",
    }
}

# ===== LINA (female, smooth) =====
DJ_LINA = {
    "name": "Лина",
    "intro_templates": [
        "Привет, это Лина. Твой момент на RADIO DVA начинается с {track} — {artist}. Наслаждайся.",
        "Тише... слышишь? {track} от {artist} уже в эфире. Лина у микрофона.",
        "Добрый вечер. {name} с вами. В эфире {track} — {artist}. Выдохни и слушай.",
        "RADIO DVA — твоя волна. {track} от {artist}. Идеальное звучание.",
        "Привет, это {name}. Хочешь отличную музыку? Она уже здесь: {track} — {artist}.",
        "Мягко входим в музыкальный блок. {track} от {artist} для вас. Лина в эфире.",
    ],
    "outro_templates": [
        "{track} от {artist}... красиво, правда? Лина была с вами. Оставайтесь на волне.",
        "Прекрасный трек: {track} — {artist}. Это Лина, и мы продолжаем.",
        "Музыка — лучшее, что есть. {track} от {artist} тому подтверждение. Не прощаюсь.",
        "{track} от {artist} только что завершился. Лина желает вам отличного настроения!",
        "Трек улетел в историю! {track} — {artist}. С вами была {name}, до встречи!",
    ],
    "mid_templates": [
        "Знаете, музыка — это единственный язык, который понимают все. И мы на нём говорим!",
        "Сегодня отличный день, чтобы слушать RADIO DVA. Я права?",
        "Говорят, от хорошей музыки вырабатывается дофамин. Так что слушайте на здоровье!",
        "Хотите секрет? Лучшие треки играют именно на RADIO DVA.",
    ],
    "time_greetings": {
        "morning": "Доброе утро! Лина помогает вам проснуться.",
        "afternoon": "Добрый день! Как дела? Лина скрасит ваш день.",
        "evening": "Вечер в самом разгаре. Лина с вами.",
        "night": "Ночь. Тишина. И только RADIO DVA играет для вас.",
    },
    "genre_specific": {
        "rus": "Русский хит — всегда в самое сердце.",
        "world": "Мировой бестселлер. Как он вам?",
        "hiphop": "Хип-хоп на RADIO DVA. Чувствуете энергию?",
        "classical": "Классика — это магия. Просто слушайте.",
        "jazz": "Джаз и блюз. Душевно и тепло.",
    }
}


class ScriptGenerator:
    def __init__(self, dj_name="Алекс"):
        self.dj = DJ_ALEX if dj_name == "Алекс" else DJ_LINA
    
    def switch_dj(self, name):
        self.dj = DJ_ALEX if name == "Алекс" else DJ_LINA
    
    def generate_show_segment(self, track, next_track=None, hour=None):
        """Generate intro and outro text. Returns (intro_text, outro_text)."""
        # Time greeting (25% chance)
        if hour is not None and random.random() < 0.25:
            if 5 <= hour < 12:
                greeting = self.dj["time_greetings"]["morning"]
            elif 12 <= hour < 18:
                greeting = self.dj["time_greetings"]["afternoon"]
            elif 18 <= hour < 23:
                greeting = self.dj["time_greetings"]["evening"]
            else:
                greeting = self.dj["time_greetings"]["night"]
        else:
            greeting = ""
        
        # Genre-specific intro (30% chance)
        genre = track.get("genre", "world")
        genre_line = ""
        if random.random() < 0.3:
            genre_line = self.dj["genre_specific"].get(genre, "")
        
        # Build intro
        intro = random.choice(self.dj["intro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        if greeting:
            if random.random() < 0.5:
                intro = greeting + " " + intro
            else:
                intro = intro + " " + greeting
        
        if genre_line and random.random() < 0.5:
            intro = intro + " " + genre_line
        
        # Add joke/banter (15% chance)
        if random.random() < 0.15:
            intro += " Кстати, " + random.choice(self.dj["jokes"]).lower()
        
        # Add mid-segment comment (10% chance)
        if random.random() < 0.10:
            intro += " " + random.choice(self.dj["mid_templates"]).format(name=self.dj["name"])
        
        # Build outro
        outro = random.choice(self.dj["outro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        return intro, outro
