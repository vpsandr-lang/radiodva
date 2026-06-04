"""RADIO DVA AI — Script Generator with human-like DJ templates."""
import random, os, json, re

DJ_ALEX = {
    "name": "Алекс",
    "intro_templates": [
        "RADIO DVA на связи! {name} у микрофона, слушаем — {track} от {artist}!",
        "Йо! Это {name} с RADIO DVA. Ловите: {track} — {artist}. Погнали!",
        "В эфире {name}! Прямо сейчас: {track}, {artist}. Огонь!",
        "С вами {name} и RADIO DVA! {track} — {artist}. Не выключай!",
        "Как дела? {name} приветствует! Слушаем {track} от {artist}.",
        "А вот и свежий трек! {name} для вас. {track} — {artist}, оцените!",
    ],
    "outro_templates": [
        "Это был {track} от {artist}. {name} был с тобой.",
        "{track} — {artist}. Классный трек! {name} провожает.",
        "Зарядились? {track} от {artist}. Остаёмся на RADIO DVA!",
        "{track} от {artist} только что прозвучал. {name} с вами был.",
        "Отличный трек! {track} — {artist}. Дальше будет ещё интереснее.",
    ],
    "jokes": [
        "Почему диджей не ходит в спортзал? Он и так качает!",
        "Что сказал динамик? — 'Мне нечего скрывать!'",
        "Музыкант упал со сцены: 'Я просто взял нижнюю ноту!'",
    ],
}

DJ_LINA = {
    "name": "Лина",
    "intro_templates": [
        "Привет, это Лина. Твой момент начинается с {track} — {artist}.",
        "Слышишь? {track} от {artist} уже в эфире. Лина у микрофона.",
        "Добрый вечер. {name} с вами. {track} — {artist}. Слушай.",
        "RADIO DVA — твоя волна. {track} от {artist}. Идеальное звучание.",
        "Привет, это {name}. {track} — {artist} для вас.",
    ],
    "outro_templates": [
        "{track} от {artist}... красиво. Лина была с вами.",
        "Прекрасный трек: {track} — {artist}. Это Лина, продолжаем.",
        "Музыка — лучшее. {track} от {artist}. Не прощаюсь.",
        "{track} от {artist} завершился. Лина желает отличного настроения!",
    ],
    "jokes": [
        "Почему радио не спит? Потому что у него есть ведущие!",
        "Что сказала пластинка проигрывателю? — 'Ты меня кружишь!'",
        "Говорят, от хорошей музыки вырабатывается дофамин. Слушайте на здоровье!",
    ],
}


class ScriptGenerator:
    def __init__(self, dj_name="Алекс"):
        self.dj = DJ_ALEX if dj_name == "Алекс" else DJ_LINA
    
    def switch_dj(self, name):
        self.dj = DJ_ALEX if name == "Алекс" else DJ_LINA
    
    def generate_show_segment(self, track, next_track=None, hour=None):
        """Generate intro and outro text. Returns (intro_text, outro_text)."""
        intro = random.choice(self.dj["intro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        # Add joke sometimes
        if random.random() < 0.15:
            intro += " Кстати, " + random.choice(self.dj["jokes"]).lower()
        
        outro = random.choice(self.dj["outro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        return intro, outro
