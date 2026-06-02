"""RADIO DVA AI — Script Generator (template-based with optional LLM)."""
import random, os, json, re

DJ_ALEX = {
    "name": "Алекс",
    "intro_templates": [
        "А это RADIO DVA! С вами {name}, и мы только начинаем. Сейчас — {track} от {artist}. Поехали!",
        "Йо! {name} на связи. Двойная волна уже здесь: {track} — {artist}. Врубаем!",
        "Привет-привет! {name} у микрофона. Ловите: {track} от {artist}. Это мощно.",
        "С вами {name} и RADIO DVA. Прямо сейчас — {track}, {artist}. Не переключайся!",
        "Двойная порция отличной музыки! {name} с вами, и сейчас — {track} — {artist}.",
    ],
    "outro_templates": [
        "Это был {track} — {artist}. Ну как тебе? {name} был с тобой, оставайся на волне!",
        "{track} от {artist} — отличный трек, согласен? С вами был {name}, не переключайся!",
        "Классный трек, да? {track} — {artist}. Это {name}, остаёмся на RADIO DVA!",
        "Заряд энергии получен? {track} — {artist}. {name} провожает тебя дальше!",
    ],
    "mid_templates": [
        "Как настроение? {name} напоминает: ты крут! А мы продолжаем.",
        "Знаешь, что делает день лучше? Отличная музыка. И она уже здесь!",
        "Погода за окном... да какая разница? У нас своя атмосфера!",
    ],
    "jokes": [
        "Почему музыканты не играют в карты? Потому что у них краплёные колоды!",
        "Что сказал диджей, когда упал? — 'Я просто сделал битдаун!'",
        "Отличный трек чтобы поднять настроение — говорю вам как профессионал!",
    ]
}

DJ_LINA = {
    "name": "Лина",
    "intro_templates": [
        "Привет, это Лина. Твой вечер на RADIO DVA начинается с {track} — {artist}. Наслаждайся.",
        "Тише... слышишь? Это играет {track}. {artist} для тебя. Лина у микрофона.",
        "Добрый вечер. {name} с тобой. В эфире — {track}, {artist}. Просто выдохни и слушай.",
        "RADIO DVA, двойная волна. {track} от {artist}. Идеальный момент.",
    ],
    "outro_templates": [
        "{track} от {artist}... что-то в этом есть. Лина была с тобой. Оставайся на волне.",
        "Красиво звучало, да? {track} — {artist}. Это Лина, и мы продолжаем.",
        "Музыка — лучшее лекарство. {track} от {artist} тому подтверждение. Не прощаюсь.",
    ],
    "jokes": [
        "Слышали анекдот про радио? Каждый день одно и то же... Шучу!",
        "Лучшая музыка — та, что играет сейчас. А у нас она всегда лучшая!",
    ]
}

class ScriptGenerator:
    def __init__(self, dj_name="Алекс"):
        self.dj = DJ_ALEX if dj_name == "Алекс" else DJ_LINA
    
    def switch_dj(self, name):
        self.dj = DJ_ALEX if name == "Алекс" else DJ_LINA
    
    def generate_show_segment(self, track, next_track=None, hour=None):
        intro = random.choice(self.dj["intro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        # Add joke sometimes
        if random.random() < 0.2:
            intro += " Кстати, " + random.choice(self.dj["jokes"]).lower()
        
        outro = random.choice(self.dj["outro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        return intro, outro
    
    def generate_mid(self):
        return random.choice(self.dj["mid_templates"]).format(name=self.dj["name"])
