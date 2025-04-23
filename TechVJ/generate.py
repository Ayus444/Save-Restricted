import traceback
from pyrogram.types import Message
from pyrogram import Client, filters
from asyncio.exceptions import TimeoutError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
from config import API_ID, API_HASH
from database.db import db

SESSION_STRING_SIZE = 351

async def ask(client: Client, chat_id: int, text: str, timeout: int = 300):
    await client.send_message(chat_id, text)
    try:
        response: Message = await client.listen(chat_id, timeout=timeout)
        return response
    except TimeoutError:
        await client.send_message(chat_id, "❌ Timeout. Please try again.")
        return None

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["logout"]))
async def logout(client, message):
    user_data = await db.get_session(message.from_user.id)  
    if user_data is None:
        return 
    await db.set_session(message.from_user.id, session=None)  
    await message.reply("**Logout Successfully** ♦")

@Client.on_message(filters.private & ~filters.forwarded & filters.command(["login"]))
async def main(bot: Client, message: Message):
    user_data = await db.get_session(message.from_user.id)
    if user_data is not None:
        await message.reply("**You Are Already Logged In. First /logout Your Old Session. Then Do Login.**")
        return 

    user_id = int(message.from_user.id)

    phone_number_msg = await ask(bot, user_id, "<b>Please send your phone number which includes country code</b>\n<b>Example:</b> <code>+13124562345, +9171828181889</code>")
    if not phone_number_msg or phone_number_msg.text == '/cancel':
        return await bot.send_message(user_id, '<b>Process cancelled!</b>')

    phone_number = phone_number_msg.text
    client = Client(":memory:", API_ID, API_HASH)
    await client.connect()
    await bot.send_message(user_id, "Sending OTP...")

    try:
        code = await client.send_code(phone_number)
        phone_code_msg = await ask(bot, user_id, "Please check for an OTP in official telegram account. If you got it, send OTP here in format: `1 2 3 4 5`\nEnter /cancel to cancel.")
    except PhoneNumberInvalid:
        await bot.send_message(user_id, '`PHONE_NUMBER` **is invalid.**')
        return

    if not phone_code_msg or phone_code_msg.text == '/cancel':
        return await bot.send_message(user_id, '<b>Process cancelled!</b>')

    try:
        phone_code = phone_code_msg.text.replace(" ", "")
        await client.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await bot.send_message(user_id, '**OTP is invalid.**')
        return
    except PhoneCodeExpired:
        await bot.send_message(user_id, '**OTP is expired.**')
        return
    except SessionPasswordNeeded:
        two_step_msg = await ask(bot, user_id, '**Two-step verification enabled. Enter password or /cancel**')
        if not two_step_msg or two_step_msg.text == '/cancel':
            return await bot.send_message(user_id, '<b>Process cancelled!</b>')
        try:
            password = two_step_msg.text
            await client.check_password(password=password)
        except PasswordHashInvalid:
            await bot.send_message(user_id, '**Invalid Password Provided**')
            return

    string_session = await client.export_session_string()
    await client.disconnect()

    if len(string_session) < SESSION_STRING_SIZE:
        return await bot.send_message(user_id, '<b>Invalid session string</b>')

    try:
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            uclient = Client(":memory:", session_string=string_session, api_id=API_ID, api_hash=API_HASH)
            await uclient.connect()
            await db.set_session(message.from_user.id, session=string_session)
    except Exception as e:
        return await bot.send_message(user_id, f"<b>ERROR IN LOGIN:</b> `{e}`")

    await bot.send_message(user_id, "<b>Account Login Successfully.\n\nIf You Get Any Error Related To AUTH KEY Then /logout first and /login again</b>")
