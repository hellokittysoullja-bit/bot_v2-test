# bot_v2/safe_send.py — надёжная отправка сообщений

import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.error import BadRequest

logger = logging.getLogger(__name__)


async def safe_reply(
    update: Update,
    context,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML"
):
    """
    Отправить новое сообщение в тот же чат. Если HTML упал — шлём простой текст.
    Всегда находит chat_id (из колбэка или обычного сообщения).
    """
    chat_id = _get_chat_id(update)
    if not chat_id:
        return

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    except Exception:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"safe_reply failed completely: {e}")


async def safe_edit(
    query,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML"
):
    """
    Пытается отредактировать исходное сообщение колбэка.
    Если нельзя — отправляет новое сообщение в чат.
    """
    if query.message is None:
        # Просроченный колбэк, отправляем новое
        try:
            await query.answer()
            await query.from_user.send_message(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"safe_edit fallback failed: {e}")
        return

    try:
        await query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except BadRequest as e:
        err_msg = str(e).lower()
        if "message is not modified" in err_msg:
            return  # всё ок, текст тот же
        if "message can't be edited" in err_msg or "message to edit not found" in err_msg:
            # не можем редактировать — шлём новое
            try:
                await query.message.reply_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            except Exception:
                await query.from_user.send_message(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        else:
            logger.warning(f"safe_edit BadRequest: {e}")
    except Exception:
        # полный провал — отправляем новое в чат
        try:
            await query.message.chat.send_message(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception:
            try:
                await query.from_user.send_message(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
            except Exception as e:
                logger.error(f"safe_edit completely failed: {e}")


def _get_chat_id(update: Update) -> int | None:
    """Вытащить chat_id из апдейта (колбэк или сообщение)."""
    if update.callback_query:
        if update.callback_query.message:
            return update.callback_query.message.chat_id
        if update.effective_chat:
            return update.effective_chat.id
        return None
    if update.effective_chat:
        return update.effective_chat.id
    return None
