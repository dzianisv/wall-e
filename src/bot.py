import asyncio
import json
import time
import os
from telegram import Chat, ChatMemberUpdated, Update, Message, MessageEntity
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from config import Config

import logging
logger = logging.getLogger(__name__)

# We won't use the previous Storage class. We'll just store user sessions in Mongo.
# The LLM class itself uses Mongo for memory. We just need to instantiate LLM per user.

_user_llms = {}  # cache LLM instances by user_id

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # same as original
    pass

async def show_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # same as original, if needed
    await update.effective_message.reply_text("This command is optional.")

async def greet_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # same as original
    pass

async def reply(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    user_id = str(message.from_user.id)
    user_text = message.text

    if user_id not in _user_llms:
        _user_llms[user_id] = LLM(user_id=user_id)

    llm_instance = _user_llms[user_id]
    start_ts = time.time()
    response = llm_instance.ask(user_text)
    logger.info("User %d asked: %s, response: %s, time: %.2fs", message.from_user.id, user_text, response, time.time() - start_ts)

    if len(response) > 4096:
        response = response[:4096]
    await message.reply_text(response, parse_mode='Markdown')


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message = update.effective_message
    chat = update.effective_chat
    me =  await context.bot.get_me()

    if chat.type == Chat.PRIVATE:
        await reply(message, context)
    elif chat.type in (Chat.GROUP, Chat.SUPERGROUP):
        # handle mentions
        if message.entities:
            for entity in message.entities:
                entity_text = message.text[entity.offset: entity.offset + entity.length]
                if entity.type == MessageEntity.TEXT_MENTION and entity.user and entity.user.id == me.id:
                   await reply(message, context)
                   return
                elif entity.type == MessageEntity.MENTION and entity_text[1:] == me.username:
                    await reply(message, context)
                    return

        # handle replies to the bot's messages
        if message.reply_to_message is not None and message.reply_to_message.from_user.id == me.id:
            await reply(message, context)


def create_telegram_app(token: str) -> Application:
    application = Application.builder().token(token).build()

    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler("show_chats", show_chats))
    application.add_handler(ChatMemberHandler(greet_chat_members, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.ALL, message_handler))
    return application

async def start_telegram_app(application):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

async def wait_for_termination():
    stop_event = asyncio.Event()
    await stop_event.wait()

async def main():
    coroutines = [wait_for_termination()]
    token = Config.telegram_bot_token
    coroutine = start_telegram_app(create_telegram_app(token))
    coroutines.append(coroutine)
    await asyncio.gather(*coroutines)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
