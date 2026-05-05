# bot_v2/database.py — надёжный слой работы с PostgreSQL/Neon

import json, logging, random, hashlib
from datetime import datetime, date
from cachetools import TTLCache
import asyncpg

from config import (
    FUNNY_REACTIONS, BLUNT_IMAGES, ACHIEVEMENTS, ACHIEVEMENTS_DICT,
    RANKS
)

logger = logging.getLogger(__name__)

db_pool = None

# Защищённый кэш игроков (60 секунд)
player_cache = TTLCache(maxsize=1000, ttl=60)

# ------------------------------------------------------------
# Инициализация и таблицы
# ------------------------------------------------------------
async def init_db(database_url: str):
    global db_pool
    db_pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10, command_timeout=10)
    async with db_pool.acquire() as conn:
        await _create_tables(conn)
    logger.info("Database pool created and tables verified.")

async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()

async def _create_tables(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance BIGINT DEFAULT 0,
            blunts BIGINT DEFAULT 0,
            guild TEXT DEFAULT NULL,
            last_farm TIMESTAMP,
            last_ritual TIMESTAMP,
            last_daily TIMESTAMP,
            titles TEXT DEFAULT '',
            last_farm_date DATE,
            passive_level INTEGER DEFAULT 0,
            passive_collected TIMESTAMP,
            karma INTEGER DEFAULT 0,
            inhaled INTEGER DEFAULT 0,
            smoke_count BIGINT DEFAULT 0,
            farm_count BIGINT DEFAULT 0,
            craft_count BIGINT DEFAULT 0,
            ritual_count BIGINT DEFAULT 0,
            referral_count BIGINT DEFAULT 0,
            last_berserk TIMESTAMP,
            inventory JSONB DEFAULT '[]',
            invited_by BIGINT DEFAULT NULL,
            profile_skins JSONB DEFAULT '{}',
            login_streak INTEGER DEFAULT 0,
            last_login_date DATE,
            oath TEXT DEFAULT '',
            keys BIGINT DEFAULT 0,
            check_count BIGINT DEFAULT 0,
            m_essence BIGINT DEFAULT 0,
            lab_chests BIGINT DEFAULT 0,
            lab_deaths BIGINT DEFAULT 0,
            alchemy_count BIGINT DEFAULT 0,
            last_lab_attempt TIMESTAMP,
            donated BIGINT DEFAULT 0
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS achievements_awarded (
            user_id BIGINT,
            ach_id TEXT,
            awarded_at TIMESTAMP,
            PRIMARY KEY (user_id, ach_id)
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS guild_weekly (
            guild TEXT PRIMARY KEY,
            total_farmed BIGINT DEFAULT 0,
            total_donated BIGINT DEFAULT 0,
            week_start DATE,
            war_active BOOLEAN DEFAULT FALSE
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS nft_registry (
            serial SERIAL PRIMARY KEY,
            blunt_id TEXT UNIQUE,
            created_by BIGINT,
            rarity TEXT DEFAULT 'common',
            rare_number TEXT UNIQUE,
            created_at TIMESTAMP
        );
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS crystals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            description TEXT,
            amount_rub INTEGER,
            daily_oas INTEGER,
            total_earned BIGINT DEFAULT 0,
            start_date TIMESTAMP,
            cancelled INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0
        );
    """)

# ------------------------------------------------------------
# Работа с кэшем
# ------------------------------------------------------------
def invalidate_cache(user_id: int):
    player_cache.pop(user_id, None)

# ------------------------------------------------------------
# Главная функция получения игрока
# ------------------------------------------------------------
async def get_player(user_id: int) -> dict | None:
    """Безопасно достаёт игрока из кэша или БД, нормализуя JSONB поля."""
    if user_id in player_cache:
        return player_cache[user_id]

    if db_pool is None:
        return None

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM players WHERE user_id=$1", user_id)

    if not row:
        return None

    p = dict(row)

    # Нормализация inventory (JSONB -> список)
    raw_inv = p.get("inventory")
    if isinstance(raw_inv, str):
        try:
            p["inventory"] = json.loads(raw_inv)
        except (json.JSONDecodeError, TypeError):
            p["inventory"] = []
    elif isinstance(raw_inv, list):
        p["inventory"] = raw_inv
    else:
        p["inventory"] = []

    # Нормализация profile_skins (JSONB -> словарь)
    raw_skins = p.get("profile_skins")
    if isinstance(raw_skins, str):
        try:
            p["profile_skins"] = json.loads(raw_skins)
        except (json.JSONDecodeError, TypeError):
            p["profile_skins"] = {}
    elif isinstance(raw_skins, dict):
        p["profile_skins"] = raw_skins
    else:
        p["profile_skins"] = {}

    player_cache[user_id] = p
    return p

# ------------------------------------------------------------
# Обновление баланса
# ------------------------------------------------------------
async def add_balance(user_id: int, username: str, amount: int):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # Гарантируем, что игрок существует
            await conn.execute("""
                INSERT INTO players(user_id, username, balance, blunts)
                VALUES($1, $2, 0, 0)
                ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
            """, user_id, username)
            await conn.execute("UPDATE players SET balance = balance + $1 WHERE user_id = $2", amount, user_id)
    invalidate_cache(user_id)

async def add_blunts(user_id: int, username: str, amount: int):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO players(user_id, username, balance, blunts)
                VALUES($1, $2, 0, 0)
                ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
            """, user_id, username)
            await conn.execute("UPDATE players SET blunts = blunts + $1 WHERE user_id = $2", amount, user_id)
    invalidate_cache(user_id)

async def add_essence(user_id: int, amount: int):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("""
                INSERT INTO players(user_id, username, balance, blunts)
                VALUES($1, '', 0, 0)
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)
            await conn.execute("UPDATE players SET m_essence = m_essence + $1 WHERE user_id = $2", amount, user_id)
    invalidate_cache(user_id)

# ------------------------------------------------------------
# Счётчики
# ------------------------------------------------------------
ALLOWED_COUNTERS = {"farm_count","craft_count","smoke_count","ritual_count",
                    "referral_count","check_count","lab_chests","lab_deaths","alchemy_count"}

async def increment_counter(user_id: int, field: str):
    if field not in ALLOWED_COUNTERS:
        return
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(f"UPDATE players SET {field} = COALESCE({field}, 0) + 1 WHERE user_id = $1", user_id)
    invalidate_cache(user_id)

# ------------------------------------------------------------
# Таймстемпы
# ------------------------------------------------------------
async def update_last_farm(user_id: int):
    now = datetime.now()
    today = date.today()
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET last_farm=$1, last_farm_date=$2 WHERE user_id=$3", now, today, user_id)
    invalidate_cache(user_id)

async def update_last_ritual(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET last_ritual=NOW() WHERE user_id=$1", user_id)
    invalidate_cache(user_id)

async def update_last_daily(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET last_daily=NOW() WHERE user_id=$1", user_id)
    invalidate_cache(user_id)

async def update_last_berserk(user_id: int):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET last_berserk=NOW() WHERE user_id=$1", user_id)
    invalidate_cache(user_id)

# ------------------------------------------------------------
# Титулы, гильдии, скины
# ------------------------------------------------------------
async def add_title(user_id: int, emoji: str):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("SELECT titles FROM players WHERE user_id=$1", user_id)
        titles = row["titles"] if row else ""
        if emoji not in titles:
            titles = (titles + " " + emoji).strip()
            await conn.execute("UPDATE players SET titles=$1 WHERE user_id=$2", titles, user_id)
    invalidate_cache(user_id)

async def set_guild(user_id: int, guild: str):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET guild=$1 WHERE user_id=$2", guild, user_id)
    invalidate_cache(user_id)

async def get_guild(user_id: int) -> str | None:
    p = await get_player(user_id)
    return p.get("guild") if p else None

async def unlock_border(user_id: int, emoji: str):
    p = await get_player(user_id)
    if not p: return
    skins = p.get("profile_skins", {})
    borders = skins.get("unlocked_borders", [])
    if emoji not in borders:
        borders.append(emoji)
    skins["unlocked_borders"] = borders
    if not skins.get("active_border"):
        skins["active_border"] = emoji
    await _update_skins(user_id, skins)

async def unlock_bg(user_id: int, emoji: str):
    p = await get_player(user_id)
    if not p: return
    skins = p.get("profile_skins", {})
    backs = skins.get("unlocked_backgrounds", [])
    if emoji not in backs:
        backs.append(emoji)
    skins["unlocked_backgrounds"] = backs
    if not skins.get("active_background"):
        skins["active_background"] = emoji
    await _update_skins(user_id, skins)

async def _update_skins(user_id: int, skins: dict):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE players SET profile_skins=$1 WHERE user_id=$2", json.dumps(skins), user_id)
    invalidate_cache(user_id)

# ------------------------------------------------------------
# Достижения
# ------------------------------------------------------------
async def award_achievement(user_id: int, ach_id: str, username: str, bot=None, chat_id=None):
    ach = ACHIEVEMENTS_DICT.get(ach_id)
    if not ach: return

    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO achievements_awarded(user_id,ach_id,awarded_at) VALUES($1,$2,$3) ON CONFLICT DO NOTHING",
            user_id, ach_id, datetime.now()
        )

    reward = ach.get("reward","")
    # Выдача наград
    if ach_id == "craft_15":
        await add_balance(user_id, username, 100)
        await unlock_border(user_id, "🫧")
    elif ach_id == "craft_50":
        await add_balance(user_id, username, 300)
        await unlock_border(user_id, "🫧")
    elif ach_id == "referral_1":
        await add_title(user_id, "🩸")
        await unlock_border(user_id, "🩸")
    elif ach_id == "balance_20000":
        await unlock_bg(user_id, "⚰️")
    elif ach_id == "balance_50000":
        await add_balance(user_id, username, 10000)
        await unlock_border(user_id, "🩸")
        await unlock_bg(user_id, "💀")
    elif ach_id == "check_10":
        await unlock_bg(user_id, "👁️")
    elif ach_id == "lunar_lord":
        await unlock_bg(user_id, "🌀")

    if "Титул" in reward:
        await add_title(user_id, ach["emoji"])

    # Отправка сообщения
    if bot and chat_id:
        text = f"<b>🕊️ СВИТОК ДОСТИЖЕНИЙ 🏆</b>\n\n<b>🎉 Достижение разблокировано!</b>\n<b>{ach['name']} {ach['emoji']}</b>\n\n<i>📜 Запись добавлена</i>"
        if reward and ach_id != "balance_1000":
            text += f"\n<i>{reward}</i>"
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Failed to send achievement {ach_id} to {user_id}: {e}")

# ------------------------------------------------------------
# Именные бланты (NFT)
# ------------------------------------------------------------
async def create_named_blunt(uid: int, name: str, rarity: str | None = None, conn=None) -> dict:
    if conn is None:
        async with db_pool.acquire() as conn:
            return await _create_named_blunt_inner(uid, name, rarity, conn)
    else:
        return await _create_named_blunt_inner(uid, name, rarity, conn)

async def _create_named_blunt_inner(uid, name, rarity, conn):
    blunt_id = f"blunt_{uid}_{int(datetime.now().timestamp()*1000)}_{random.randint(1000,9999)}"
    await conn.execute("""
        INSERT INTO players(user_id, username, balance, blunts)
        VALUES($1, '', 0, 0)
        ON CONFLICT (user_id) DO NOTHING
    """, uid)

    row = await conn.fetchrow("SELECT inventory FROM players WHERE user_id=$1", uid)
    inv_raw = row["inventory"] if row else None
    inv = json.loads(inv_raw) if isinstance(inv_raw, str) else (inv_raw if isinstance(inv_raw, list) else [])

    if not rarity:
        r = random.random()
        if r < 0.02: rarity = "legendary"
        elif r < 0.11: rarity = "epic"
        elif r < 0.37: rarity = "rare"
        else: rarity = "common"

    async with conn.transaction():
        serial_row = await conn.fetchrow(
            "INSERT INTO nft_registry(blunt_id,created_by,rarity,created_at) VALUES($1,$2,$3,$4) RETURNING serial",
            blunt_id, uid, rarity, datetime.now()
        )
        serial = serial_row["serial"]
        count_row = await conn.fetchrow("SELECT COUNT(*) as cnt FROM nft_registry WHERE rarity=$1", rarity)
        rare_count = count_row["cnt"]
        prefix = {"legendary":"L","epic":"E","rare":"R","common":"C"}.get(rarity,"C")
        rare_number = f"{prefix}-{rare_count:04d}"
        await conn.execute("UPDATE nft_registry SET rare_number=$1 WHERE blunt_id=$2", rare_number, blunt_id)

    hash_hex = hashlib.sha256(f"{name}{serial}{datetime.now().timestamp()}".encode()).hexdigest()[:12].upper()
    short_hash = f"0x{hash_hex[:6]}...{hash_hex[-4:]}"
    reaction = random.choice(FUNNY_REACTIONS)

    item = {
        "id": blunt_id, "serial": serial, "name": name, "type": "named",
        "created_at": datetime.now().isoformat(), "rarity": rarity,
        "rare_number": rare_number, "hash": short_hash, "reaction": reaction,
        "owner_history": [{"user_id": uid, "since": datetime.now().isoformat()}]
    }
    inv.append(item)
    await conn.execute("UPDATE players SET inventory=$1 WHERE user_id=$2", json.dumps(inv), uid)
    invalidate_cache(uid)
    return item

# ------------------------------------------------------------
# Другие вспомогательные функции
# ------------------------------------------------------------
async def get_top(limit=10):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT username, balance, guild FROM players ORDER BY balance DESC LIMIT $1", limit)
    return rows

async def count_guilds():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT guild, COUNT(*) as cnt FROM players WHERE guild IS NOT NULL GROUP BY guild")
    return {"BLACK": next((r["cnt"] for r in rows if r["guild"]=="BLACK"), 0),
            "WHITE": next((r["cnt"] for r in rows if r["guild"]=="WHITE"), 0)}

async def add_war_score(user_id: int, points: int):
    async with db_pool.acquire() as conn:
        war = await conn.fetchrow("SELECT war_active FROM guild_weekly WHERE war_active = TRUE LIMIT 1")
        if not war:
            return
        row = await conn.fetchrow("SELECT guild FROM players WHERE user_id=$1", user_id)
        guild = row["guild"] if row else None
        if guild in ("BLACK", "WHITE"):
            await conn.execute("""
                INSERT INTO guild_weekly (guild, week_start, total_farmed)
                VALUES ($1, CURRENT_DATE, $2)
                ON CONFLICT (guild) DO UPDATE SET total_farmed = guild_weekly.total_farmed + $2
            """, guild, points)

async def get_guild_donated_guilds():
    async with db_pool.acquire() as conn:
        black = await conn.fetchval("SELECT COALESCE(SUM(donated),0) FROM players WHERE guild='BLACK'")
        white = await conn.fetchval("SELECT COALESCE(SUM(donated),0) FROM players WHERE guild='WHITE'")
    return black, white

async def get_weekly_war_stats():
    async with db_pool.acquire() as conn:
        scores = await conn.fetch("SELECT guild, total_farmed FROM guild_weekly")
    return {r["guild"]: r["total_farmed"] for r in scores}