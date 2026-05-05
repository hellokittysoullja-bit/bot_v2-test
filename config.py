# bot_v2/config.py — все константы и игровой контент
import os

# --- Основные настройки ---
TOKEN = os.getenv("TOKEN")  # в продакшене заменишь на боевой токен, для тестов — тестовый
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
FARM_COOLDOWN_HOURS = 0.5
FARM_MIN, FARM_MAX = 45, 100
HAPPY_HOUR_MULTIPLIER = 2
HAPPY_HOUR_DURATION_MIN = 30
BLUNTS_PER_PAGE = 3

# --- Медали ---
FARM_MEDALS = [
    (1, "🥉 Бронза", 10),
    (10, "🥈 Серебро", 30),
    (50, "🥇 Золото", 80),
    (250, "💎 Платина", 200)
]
CRAFT_MEDALS = [
    (1, "🥉 Бронза", 10),
    (10, "🥈 Серебро", 30),
    (50, "🥇 Золото", 80),
    (250, "💎 Платина", 200)
]
SMOKE_MEDALS = [
    (1, "🥉 Бронза", 10),
    (10, "🥈 Серебро", 30),
    (50, "🥇 Золото", 80),
    (250, "💎 Платина", 200)
]
RITUAL_MEDALS = [
    (1, "🥉 Бронза", 20),
    (10, "🥈 Серебро", 50),
    (50, "🥇 Золото", 120),
    (250, "💎 Платина", 300)
]

# --- Шёпоты ---
WHISPERS = [
    "🩸 Искажение наблюдает за твоими нитями",
    "💠 Кристалл твоей судьбы пульсирует",
    "🩸 Искажение шепчет твоё имя",
    "🌙 «Ночь опустилась на Гильдию. Смотритель пробудился.»"
]

# --- Нейро-статусы ---
NEURO_STATUSES = [
    "Альфа-ритмы нестабильны", "Сенсорная депривация 80%", "Фаза быстрого сна",
    "Нейро-шунт активен", "Предел синаптической проводимости", "Резонанс с Искажением: 12%"
]

# --- Реакции на бланты ---
FUNNY_REACTIONS = [
    "Выглядит как NFT, который никто не купит.", "Даже Бездна от такого закашлялась.",
    "Это не блант, это крик души.", "Искажение занесло это название в чёрный список.",
    "10/10, лучший блант для того чтобы спрятать его подальше.", "Пахнет так, будто его скрутил сам Ктулху.",
    "Этот блант вызывает желание помыть руки.", "С таким названием только в Бездну.",
    "Я бы такое не выкурил, но звучит гордо."
]

# --- Ранги ---
RANKS = [
    ("🪓 Рекрут", 0, 0),
    ("⚔️ Ветеран", 5000, 1500),
    ("🪦 Призрак", 20000, 6000),
    ("🪬 Некромант", 50000, 15000)
]

# --- Достижения ---
ACHIEVEMENTS = [
    {"id": "farm_1", "name": "Первый Шаг", "emoji": "🕯️", "desc": "Совершить 1 фарм очков (АнтиСошл)", "reward": "Титул 🕯️"},
    {"id": "craft_1", "name": "О! Росточек!", "emoji": "🌱", "desc": "Скрутить свой первый блант", "reward": "Титул 🌱"},
    {"id": "smoke_1", "name": "Затяжка", "emoji": "🚬", "desc": "Выкурить свой первый блант", "reward": "Титул 🕶️"},
    {"id": "balance_1000", "name": "О-о-о! Блестяшки!", "emoji": "🍬", "desc": "Накопить 1000 OAC", "reward": "Титул 🍬"},
    {"id": "smoke_10", "name": "Дымный след", "emoji": "💨", "desc": "Выкурить 10 блантов", "reward": ""},
    {"id": "craft_15", "name": "Скрученный", "emoji": "🌿", "desc": "Скрутить 15 блантов", "reward": "+100 OAC"},
    {"id": "ritual_5", "name": "Прислужник тьмы", "emoji": "🕯️", "desc": "Совершить 5 ритуалов", "reward": ""},
    {"id": "craft_50", "name": "Мастер Кручения", "emoji": "🗞️", "desc": "Скрутить 50 Блантов", "reward": "+300 OAC, Рамка 🫧"},
    {"id": "smoke_25", "name": "Вечно Накуренный", "emoji": "🫩", "desc": "Выкурить 25 блантов", "reward": "Титул 🫩"},
    {"id": "lab_first", "name": "Скрытое в тени", "emoji": "📿", "desc": "Найти первый сундук в лабиринте", "reward": "Титул 📿"},
    {"id": "referral_1", "name": "Пожиратель Душ", "emoji": "🩸", "desc": "Привести 1 друга", "reward": "Титул 🩸, Рамка 🩸"},
    {"id": "streak_7", "name": "Семь Шагов", "emoji": "🕊️", "desc": "Заходить 7 дней подряд", "reward": "Титул 🕊️"},
    {"id": "balance_20000", "name": "Груда блестяшек", "emoji": "🪦", "desc": "Накопить 20000 OAC", "reward": "Фон ⚰️"},
    {"id": "lab_chest_3", "name": "Ооо! Костяшки!!", "emoji": "🦴", "desc": "Открыть 3 сундука", "reward": "Титул 🦴"},
    {"id": "rank_phantom", "name": "Призрачный Гончий", "emoji": "👻", "desc": "Достигнуть ранга Призрак", "reward": "Титул 👻"},
    {"id": "balance_50000", "name": "Повелитель Мёртвых", "emoji": "🩸", "desc": "Накопить 50 000 OAC", "reward": "+10 000 OAC, Рамка 🩸, Фон 💀"},
    {"id": "check_10", "name": "Всевидящий", "emoji": "👁️", "desc": "Проверить 10 блантов", "reward": "Фон 👁️"},
    {"id": "lab_death_5", "name": "Похоронен заживо", "emoji": "🪦", "desc": "Умереть в Лабиринте 5 раз", "reward": "Титул 🪦"},
    {"id": "lab_chest_10", "name": "Костяной ключ", "emoji": "🗝️", "desc": "Открыть 10 сундуков", "reward": "Титул 🗝️"},
    {"id": "craft_250", "name": "Поклонник Плантеры", "emoji": "🌿", "desc": "Скрутить 250 обычных блантов", "reward": "Титул 🌿"},
    {"id": "alchemy_15", "name": "Алхимик", "emoji": "🔮", "desc": "15 раз воспользоваться магией", "reward": "Титул 🔮"},
    {"id": "lunar_lord", "name": "Лунный лорд", "emoji": "🌀", "desc": "Выполнить все остальные достижения", "reward": "Уникальный фон 🌀"}
]
ACHIEVEMENTS_DICT = {a["id"]: a for a in ACHIEVEMENTS}

# --- Лабиринт ---
LABYRINTH_ROOMS = [
    {
        "name": "👁️ Зал Наблюдателя",
        "desc": "📿 <i>Сотни глаз смотрят на тебя с потолка.</i> <b>Они ждут тебя.</b>",
        "options": [
            {"text": "⚔️ Уничтожить смотрящих (20 OAC)", "cost_oac": 20, "risk": 0.6, "reward_oac": (10,50), "fail": "life"},
            {"text": "🕯️ Отвести взгляд (1 блант)", "cost_blunt": 1, "risk": 0.8, "reward_fragment": True, "fail": "none"},
            {"text": "🏃 Бежать", "cost_none": True, "risk": 1.0, "reward_escape": True, "fail": "none"}
        ]
    },
    {
        "name": "⚗️ Алтарь Теней",
        "desc": "Густая кровь капает с алтаря. Тени шепчут о силе.",
        "options": [
            {"text": "🩸 Пожертвовать OAC (30 OAC)", "cost_oac": 30, "risk": 0.7, "reward_oac": (40,100), "fail": "life"},
            {"text": "📜 Прочесть руны (1 блант)", "cost_blunt": 1, "risk": 0.9, "reward_title": "Посвящённый", "fail": "none"},
            {"text": "🏃 Бежать", "cost_none": True, "risk": 1.0, "reward_escape": True, "fail": "none"}
        ]
    },
    {
        "name": "🌀 Водоворот Хаоса",
        "desc": "Воздух дрожит, затягивая в воронку. Прямо в центре — мерцающий сгусток.",
        "options": [
            {"text": "🌀 Схватить сгусток (25 OAC)", "cost_oac": 25, "risk": 0.5, "reward_dust": True, "fail": "life_big"},
            {"text": "🚪 Обойти (1 блант)", "cost_blunt": 1, "risk": 0.95, "reward_none": True, "fail": "life"},
            {"text": "🏃 Бежать", "cost_none": True, "risk": 1.0, "reward_escape": True, "fail": "none"}
        ]
    },
    {
        "name": "☠️ Склеп Короля",
        "desc": "Груды костей, трон из черепов. С них свисают драгоценные камни.",
        "options": [
            {"text": "💎 Сорвать камень (20 OAC)", "cost_oac": 20, "risk": 0.8, "reward_oac": (20,80), "fail": "life"},
            {"text": "🕯️ Зажечь свечу (1 блант)", "cost_blunt": 1, "risk": 1.0, "reward_dust": True, "fail": "none"},
            {"text": "🏃 Бежать", "cost_none": True, "risk": 1.0, "reward_escape": True, "fail": "none"}
        ]
    }
]

# --- Картинки блантов (file_id) ---
BLUNT_IMAGES = {
    "common": "AgACAgIAAxkBAAIRu2n5Hi5JOKJANQjkJhqNgW8zcXfLAAKVFGsbxM_JS3cfFnraoo4lAQADAgADeQADOwQ",
    "rare": "AgACAgIAAxkBAAIRvWn5HpzDS9213DAVEDp5K6AEbco_AAKWFGsbxM_JS2MGaxcgGQ2jAQADAgADeQADOwQ",
    "epic": "AgACAgIAAxkBAAIRv2n5Hp89jxsNz8V4uZUDwE1xtC07AAKXFGsbxM_JS6170Njn8cLjAQADAgADeQADOwQ",
    "legendary": "AgACAgIAAxkBAAIRwWn5HqFzbds_ThN4Pogn9c-VdjsaAAKYFGsbxM_JS6GsI_So0AHxAQADAgADeQADOwQ"
}