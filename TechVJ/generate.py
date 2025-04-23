from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid,
    PhoneCodeExpired, SessionPasswordNeeded, PasswordHashInvalid
)
import os, random, string
from config import API_ID, API_HASH
from database.db import db  # make sure this handles `get_session`, `set_session`, `remove_session`
from asyncio.exceptions import TimeoutError


def generate_filename(user_id):
    return f"session_{user_id}"


def cleanup_files(user_id):
    base = generate_filename(user_id)
    for ext in [".session", ".session-journal"]:
        path = base + ext
        if os.path.exists(path):
            os.remove(path)


@Client.on_message(filters.command("logout") & filters.private)
async def logout_handler(client, message):
    user_id = message.chat.id
    await db.remove_session(user_id)
    cleanup_files(user_id)
    await message.reply("✅ You have been logged out and session data cleared.")


@Client.on_message(filters.command("login") & filters.private)
async def login_handler(bot, message):
    user_id = message.chat.id

    # Step 1: Ask for phone number
    number_msg = await bot.ask(user_id, "Please enter your phone number (e.g. +11234567890):", filters=filters.text)
    if number_msg.text.strip() == "/cancel":
        return await message.reply("❌ Login cancelled.")

    phone_number = number_msg.text.strip()

    client = Client(generate_filename(user_id), API_ID, API_HASH)

    try:
        await client.connect()
        sent_code = await client.send_code(phone_number)
    except ApiIdInvalid:
        return await message.reply("❌ Invalid API credentials. Please check config.")
    except PhoneNumberInvalid:
        return await message.reply("❌ Invalid phone number format.")
    except Exception as e:
        return await message.reply(f"❌ Error sending OTP: {e}")

    # Step 2: Ask for OTP
    try:
        otp_msg = await bot.ask(
            user_id,
            "Enter the OTP received in your Telegram app.\nSend like: `1 2 3 4 5`",
            filters=filters.text,
            timeout=600
        )
    except TimeoutError:
        return await message.reply("⏰ OTP timeout. Please try again.")

    if otp_msg.text.strip() == "/cancel":
        return await message.reply("❌ Login cancelled.")

    code = otp_msg.text.replace(" ", "")

    # Step 3: Try signing in
    try:
        await client.sign_in(phone_number, sent_code.phone_code_hash, code)
    except PhoneCodeInvalid:
        return await message.reply("❌ Incorrect OTP.")
    except PhoneCodeExpired:
        return await message.reply("❌ OTP expired.")
    except SessionPasswordNeeded:
        try:
            pw_msg = await bot.ask(user_id, "2FA enabled. Enter your password:", filters=filters.text, timeout=300)
            await client.check_password(pw_msg.text)
        except PasswordHashInvalid:
            return await message.reply("❌ Incorrect password.")
        except TimeoutError:
            return await message.reply("⏰ 2FA timeout. Please try again.")

    # Step 4: Export and save session
    session_string = await client.export_session_string()
    await db.set_session(user_id, session_string)
    await client.disconnect()

    await message.reply("✅ Login successful. You can now use the bot's features.")
