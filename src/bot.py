import asyncio
import time
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
from llm import LLM
from mcp_manager import MCPManager

import logging
logger = logging.getLogger(__name__)

llm = LLM()
mcp_manager = MCPManager()


async def reply(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(message.chat.id, action=ChatAction.TYPING)

    user_id = str(message.from_user.id)
    user_text = message.text


    start_ts = time.time()
    response = llm.ask(user_text, session_id=user_id)
    logger.info("User %d asked: %s, response: %s, time: %.2fs", message.from_user.id, user_text, response, time.time() - start_ts)

    if len(response) > 4096:
        response = response[:4096]
    await message.reply_text(response, parse_mode='Markdown')
 

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message = update.effective_message
    chat = update.effective_chat
    me =  await context.bot.get_me()
    logger.info("message_hander:  message=%r, chat=%r", message, chat)
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


async def mcp_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    args = context.args
    if not args:
        servers = mcp_manager.list_servers(user_id)
        if not servers:
            await update.message.reply_text("No MCP servers connected.")
        else:
            lines = [f"{i+1}. {srv['url']}" for i, srv in enumerate(servers)]
            await update.message.reply_text("\n".join(lines))
        return

    if args[0] == "delete" and len(args) > 1:
        try:
            index = int(args[1]) - 1
        except ValueError:
            await update.message.reply_text("Index must be a number.")
            return
        if mcp_manager.delete_server(user_id, index):
            await update.message.reply_text("Deleted MCP server.")
        else:
            await update.message.reply_text("Invalid index.")
        return

    url = args[0]
    mcp_manager.add_server(user_id, url)
    await update.message.reply_text(f"Added MCP server: {url}")


def generate_auth_link(service: str, user_id: str) -> str:
    base = Config.integration_auth_base.rstrip('/')
    return f"{base}/{service}?user_id={user_id}"


async def integration_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Usage: /integration <gmail|calendar>")
        return
    service = context.args[0].lower()
    if service == "gmail":
        url = Config.gmail_mcp_url
    elif service == "calendar":
        url = Config.calendar_mcp_url
    else:
        await update.message.reply_text("Unknown service.")
        return

    mcp_manager.add_server(user_id, url)
    link = generate_auth_link(service, user_id)
    await update.message.reply_text(f"Authenticate here: {link}")


def create_telegram_app(token: str) -> Application:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("mcp", mcp_command))
    application.add_handler(CommandHandler("integration", integration_command))
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
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    coroutine = start_telegram_app(create_telegram_app(token))
    coroutines.append(coroutine)
    await asyncio.gather(*coroutines)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
