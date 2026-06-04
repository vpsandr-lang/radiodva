"""RADIO DVA AI — Human-like radio DJ scripts."""
import random

DJ_ALEX = {
    "name": "Алекс",
    "intro_templates": [
        "RADIO DVA, привет! Это Алекс, и мы начинаем с {track} от {artist}. Погнали!",
        "С вами Алекс на RADIO DVA! Слушаем {track} — {artist}. Отличный выбор для этого момента.",
        "Йо! Алекс здесь. Прямо сейчас {track} от {artist}. Наслаждайтесь!",
        "RADIO DVA в эфире, у микрофона Алекс. {track} — {artist}. Поехали!",
        "Привет, это Алекс! Двойная Волна играет: {track} от {artist}.",
        "Алекс на связи! {track} — {artist}. Именно то, что нужно.",
        "Слушаем RADIO DVA вместе с Алексом. {track} от {artist} уже в эфире.",
    ],
    "outro_templates": [
        "Это был {track} от {artist}. Алекс был с вами, остаёмся на RADIO DVA.",
        "{track} — {artist} прозвучал. Алекс провожает, дальше будет круче!",
        "Классный трек! {track} от {artist}. С вами был Алекс, не переключайтесь.",
        "{track} от {artist} только что завершился. Это Алекс, продолжаем слушать.",
        "Отлично пошло! {track} — {artist}. Алекс остаётся, вы со мной?",
    ],
}

DJ_LINA = {
    "name": "Лина",
    "intro_templates": [
        "Привет, это Лина. Начинаем с {track} — {artist}. Отличный трек.",
        "С вами Лина. {track} от {artist} специально для вас на RADIO DVA.",
        "Лина в эфире. {track} — {artist}. Ловите настроение!",
        "Добрый вечер, это Лина. {track} от {artist} звучит прямо сейчас.",
        "Тишина отменяется! Лина включает {track} от {artist}.",
    ],
    "outro_templates": [
        "{track} от {artist} прозвучал. Лина была с вами. Остаёмся на волне!",
        "Прекрасно! {track} — {artist}. Это Лина, дальше — ещё интереснее.",
        "{track} от {artist} завершился. С вами была Лина, не уходите.",
        "Спасибо, что слушаете. {track} — {artist}. Лина провожает, до встречи в следующем треке!",
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
        
        # Add short comment about the track sometimes
        extras = [
            " Отличный трек, кстати.",
            " Знаете этот трек?",
            " Один из моих любимых!",
            "",
            " Классика!",
        ]
        if random.random() < 0.25:
            intro += random.choice(extras)
        
        outro = random.choice(self.dj["outro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        # Sometimes add a "next up" teaser if next_track provided
        if next_track and random.random() < 0.2:
            outro += f" А после — {next_track['title']} от {next_track['artist']}."
        
        return intro, outro
