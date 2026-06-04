"""RADIO DVA AI — Warm, polite and friendly radio DJ scripts."""
import random

# ============================================================
# Алекс — Warm, energetic but polite. Smiles through the voice.
# ============================================================
DJ_ALEX = {
    "name": "Алекс",
    "intro_templates": [
        "Добрый день, дорогие слушатели! С вами Алекс, и мы начинаем с замечательного трека {track} от {artist}. Приятного прослушивания!",
        "Приветствую всех, кто сейчас с нами! Это Алекс, и для вас звучит {track} — {artist}. Улыбнитесь вместе с нами!",
        "Рад вас слышать, друзья! Алекс на связи. Прямо сейчас — {track} от {artist}. Отличный трек, правда?",
        "Всем привет! С огромным удовольствием включаю для вас {track} от {artist}. Алекс у микрофона, наслаждайтесь!",
        "Доброго времени суток! С вами Алекс. Давайте послушаем {track} — {artist}. Прекрасный выбор, не находите?",
        "Как ваше настроение? Надеюсь, отличное! Алекс с вами, и мы слушаем {track} от {artist}. Ловите момент!",
    ],
    "outro_templates": [
        "Как же красиво звучал {track} от {artist}. Спасибо, что были с нами. Алекс провожает, но не прощается!",
        "Замечательный трек, правда? {track} — {artist}. Это был Алекс, оставайтесь с нами на RADIO DVA!",
        "{track} от {artist} только что завершился. Спасибо, что слушаете. Алекс был с вами, улыбнитесь!",
        "Какая прекрасная песня! {track} — {artist}. Алекс благодарит за компанию. До встречи в следующем треке!",
        "Надеюсь, вам понравилось! {track} от {artist} прозвучал. С вами был Алекс, остаёмся на волне добра!",
    ],
}

# ============================================================
# Лина — Soft, tender, very polite. Gentle smile in voice.
# ============================================================
DJ_LINA = {
    "name": "Лина",
    "intro_templates": [
        "Здравствуйте, дорогие! С вами Лина. Пусть этот день будет тёплым, а мы начинаем с {track} от {artist}. С любовью для вас!",
        "Привет, милые слушатели! Лина у микрофона. Для вас звучит {track} — {artist}. Улыбнитесь этому дню!",
        "Добрый день, мои хорошие! Это Лина. Давайте вместе послушаем {track} от {artist}. Пусть музыка согревает!",
        "Как я рада вас слышать! Лина с вами. {track} — {artist}. Нежное звучание для прекрасного настроения!",
        "Всем привет! С вами Лина. {track} от {artist} уже звучит. Закрывайте глаза и наслаждайтесь моментом!",
    ],
    "outro_templates": [
        "{track} от {artist} — просто прелесть, согласны? Лина желает вам улыбок и тепла. До встречи!",
        "Какой чудесный трек был! {track} — {artist}. Лина благодарит вас за внимание. Будьте счастливы!",
        "Спасибо, что слушаете, мои дорогие. {track} от {artist} прозвучал для вас. Лина улыбается и остаётся с вами!",
        "Прекрасный трек завершился. {track} — {artist}. Это была Лина. Пусть ваш день будет таким же светлым!",
        "С вами была Лина. {track} от {artist} только что играл для вас. Улыбнитесь, мир прекрасен!",
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
        
        # Add a gentle compliment about the track sometimes
        gentle_comments = [
            " Обожаю этот трек!",
            " Такая красивая песня!",
            " Ну очень душевно!",
            "",
            " Сердце радуется!",
            " Просто великолепно!",
        ]
        if random.random() < 0.3:
            intro += random.choice(gentle_comments)
        
        outro = random.choice(self.dj["outro_templates"]).format(
            name=self.dj["name"], track=track["title"], artist=track["artist"])
        
        # Sometimes add a warm wish
        wishes = [
            " Хорошего настроения!",
            " Берегите себя!",
            " Улыбайтесь чаще!",
            "",
            " До скорой встречи!",
        ]
        if random.random() < 0.25:
            outro += random.choice(wishes)
        
        return intro, outro
