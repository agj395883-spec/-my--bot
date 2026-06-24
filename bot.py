"""
ربات حرفه‌ای بامزه فارسی
با قابلیت Gemini AI و آنالیز عکس
"""

import logging
import random
import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === تنظیمات محیطی (Render) ===
TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

if not TOKEN or not GEMINI_KEY:
    raise ValueError("❌ TOKEN و GEMINI_KEY باید در Environment Variables تنظیم شوند!")

# تنظیم Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

logging.basicConfig(level=logging.INFO)

# ========================
# دیتابیس جوک‌ها
# ========================
JOKES = [
    "یه نفر رفت دکتر گفت: دکتر همه بهم میگن دروغگو!\nدکتر گفت: باور نمیکنم 😂",
    "چرا برنامه‌نویس‌ها عینک میزنن؟ چون C# میزنن! 🤓",
    "یه بادمجون رفت دکتر گفت: دکتر همه بهم میگن بادمجون!\nدکتر گفت: خب بادمجون! 😅",
    "به استاد گفتم نمره‌ام رو بده!\nگفت: داری!\nگفتم: چند؟\nگفت: داری... داری تجدید میشی 😭",
    "چرا دریا شوره؟ چون ماهی‌ها توش عرق میکنن! 🐟",
    "یه مورچه رفت دکتر گفت: دکتر پام درد میکنه!\nدکتر گفت: کدوم پا؟\nمورچه گفت: یادم نیست! 🐜",
    "به یه نفر گفتم: فرق بین جهل و بی‌سوادی رو میدونی؟\nگفت: نه!\nگفتم: همین! 😂",
    "چرا جن‌ها از مدرسه میترسن؟ چون معلم روحشونو میگیره! 👻",
    "معلم پرسید: ۵ ضربدر ۵ چنده؟\nشاگرد: ۲۵!\nمعلم: آفرین!\nشاگرد: آفرین نداره، درسته! 😂",
    "چرا پرتقال نمیتونه کامپیوتر بازی کنه؟ چون آبش در میاد! 🍊",
]

GREET_REPLIES = [
    "سلام عزیزم! چطوری؟ 😁",
    "اوه اوه کی اومد! سلام 👋",
    "هوی! سلام سلام 🤩",
    "یا علی! سلام داداش 😄",
    "اِ سلام! منتظرت بودم 😏",
]

# ========================
# منو
# ========================
def main_menu():
    keyboard = [
        [KeyboardButton("😂 جوک"), KeyboardButton("🎮 بازی‌ها")],
        [KeyboardButton("🎲 تاس"), KeyboardButton("🪙 شیر یا خط")],
        [KeyboardButton("📊 آمار من"), KeyboardButton("📋 راهنما")],
        [KeyboardButton("🔮 فال"), KeyboardButton("🤖 چت با AI")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def games_menu():
    keyboard = [
        [KeyboardButton("🔢 بازی عدد"), KeyboardButton("✂️ سنگ کاغذ قیچی")],
        [KeyboardButton("🧠 معما"), KeyboardButton("🔤 کلمه بازی")],
        [KeyboardButton("🏠 برگشت به منو")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ========================
# /start
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "دوست"
    context.user_data["message_count"] = 0
    context.user_data["game"] = None
    context.user_data["ai_mode"] = False

    await update.message.reply_text(
        f"سلام {name}! 👋\n\n"
        "من ربات بامزه + هوش مصنوعی هستم 🤖✨\n"
        "میتونی باهام حرف بزنی، بازی کنی، یا عکس بفرستی تا آنالیز کنم!\n\n"
        "از منوی پایین شروع کن 👇",
        reply_markup=main_menu()
    )


# ========================
# /help
# ========================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 *راهنمای کامل ربات*\n\n"
        "━━━━━━━━━━━━━━\n"
        "🤖 *هوش مصنوعی*\n"
        "/ai — روشن/خاموش کردن AI\n"
        "🖼️ عکس بفرست — آنالیز میکنم!\n\n"
        "━━━━━━━━━━━━━━\n"
        "😂 *جوک و سرگرمی*\n"
        "/joke — جوک تصادفی\n"
        "/flip — شیر یا خط\n"
        "/roll — تاس بنداز\n"
        "/fal — فال بگیر\n\n"
        "━━━━━━━━━━━━━━\n"
        "🎮 *بازی‌ها*\n"
        "/guess — حدس عدد\n"
        "/rps — سنگ کاغذ قیچی\n"
        "/riddle — معما\n\n"
        "━━━━━━━━━━━━━━\n"
        "👮 *مدیریت گپ (ادمین)*\n"
        "/ban /mute /unmute /warn\n\n"
        "یا فقط باهام حرف بزن! 😄"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=main_menu())


# ========================
# تغییر حالت AI
# ========================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = context.user_data.get("ai_mode", False)
    context.user_data["ai_mode"] = not current

    if not current:
        await update.message.reply_text(
            "🤖 حالت AI روشن شد!\n"
            "الان هر چی بنویسی Gemini جواب میده 😄\n"
            "برای خاموش کردن /ai بزن"
        )
    else:
        await update.message.reply_text("🔴 حالت AI خاموش شد!", reply_markup=main_menu())


# ========================
# پردازش عکس با Gemini
# ========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 داری عکست رو آنالیز میکنم...")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_bytes = await file.download_as_bytearray()

        import PIL.Image
        import io
        img = PIL.Image.open(io.BytesIO(file_bytes))

        caption = update.message.caption or "این عکس رو برام توضیح بده به فارسی"

        response = model.generate_content([caption, img])
        await update.message.reply_text(f"🖼️ *آنالیز عکس:*\n\n{response.text}", parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text("😅 نتونستم عکس رو آنالیز کنم! دوباره امتحان کن.")


# ========================
# چت با Gemini
# ========================
async def chat_with_gemini(update: Update, text: str):
    try:
        prompt = f"""تو یه ربات تلگرام بامزه فارسی هستی. 
جواب‌هات باید:
- فارسی باشه
- کوتاه و جذاب باشه (حداکثر 3-4 جمله)
- بامزه و دوستانه باشه
- از ایموجی استفاده کنی

سوال/پیام کاربر: {text}"""

        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("😅 یه مشکلی پیش اومد! دوباره امتحان کن.")


# ========================
# دستورات ساده
# ========================
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(JOKES))

async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["🪙 شیر!", "🪙 خط!"]))

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    num = random.randint(1, 6)
    faces = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
    await update.message.reply_text(f"🎲 تاس انداختم: {faces[num-1]}")

async def fal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fals = [
        "🔮 امروز یه خبر خوب میشنوی!",
        "🔮 یکی داره بهت فکر میکنه 😏",
        "🔮 این هفته پول بهت میرسه 💰",
        "🔮 یه سفر کوتاه در راهه ✈️",
        "🔮 همه چیز درست میشه، صبور باش 🌟",
    ]
    await update.message.reply_text(random.choice(fals))

async def guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    context.user_data["game"] = "guess"
    context.user_data["guess_number"] = number
    context.user_data["guess_tries"] = 0
    await update.message.reply_text("🔢 یه عدد بین ۱ تا ۱۰۰ انتخاب کردم! حدس بزن 🤔")

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["game"] = "rps"
    await update.message.reply_text("✂️ انتخاب کن:\n🪨 سنگ\n📄 کاغذ\n✂️ قیچی")

async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    riddles = [
        ("هر چی بیشتر ازش بگیری بزرگتر میشه. چیه؟", "گودال"),
        ("صبح ۴ تا پا، ظهر ۲ تا پا، شب ۳ تا پا. چیه؟", "انسان"),
        ("دندون داره ولی نمیتونه بخوره. چیه؟", "شانه"),
        ("بدون اینکه حرکت کنه همیشه دوئه. چیه؟", "ساعت"),
        ("چی هست که همیشه جلوته ولی نمیتونی ببینیش؟", "آینده"),
    ]
    r = random.choice(riddles)
    context.user_data["game"] = "riddle"
    context.user_data["riddle_answer"] = r[1]
    await update.message.reply_text(f"🧠 *معما:*\n\n{r[0]}\n\nجواب بده! (بنویس: جواب)", parse_mode="Markdown")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = context.user_data.get("message_count", 0)
    wins = context.user_data.get("wins", 0)
    await update.message.reply_text(
        f"📊 *آمار تو*\n\n👤 {user.first_name}\n💬 پیام‌ها: {count}\n🏆 برد: {wins}",
        parse_mode="Markdown"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 قوانین:\n1️⃣ احترام\n2️⃣ اسپم ممنوع\n3️⃣ تبلیغ ممنوع\n\nتخلف = بن! 🔨")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن!")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(user.id)
        await update.message.reply_text(f"🔨 {user.first_name} بن شد!")
    except:
        await update.message.reply_text("نشد! ادمینم؟")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن!")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(user.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 {user.first_name} میوت شد!")
    except:
        await update.message.reply_text("نشد! ادمینم؟")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن!")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(
            user.id, ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        )
        await update.message.reply_text(f"🔊 {user.first_name} آنمیوت شد!")
    except:
        await update.message.reply_text("نشد! ادمینم؟")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن!")
        return
    user = update.message.reply_to_message.from_user
    warns = context.bot_data.get(f"warn_{user.id}", 0) + 1
    context.bot_data[f"warn_{user.id}"] = warns
    if warns >= 3:
        try:
            await update.effective_chat.ban_member(user.id)
            context.bot_data[f"warn_{user.id}"] = 0
            await update.message.reply_text(f"🚫 {user.first_name} بن شد!")
        except:
            pass
    else:
        await update.message.reply_text(f"⚠️ {user.first_name} اخطار {warns}/3!")


# ========================
# پردازش بازی‌ها
# ========================
async def process_game(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> bool:
    game = context.user_data.get("game")

    if game == "guess":
        if text.isdigit():
            num = int(text)
            target = context.user_data["guess_number"]
            context.user_data["guess_tries"] += 1
            tries = context.user_data["guess_tries"]
            if num == target:
                context.user_data["game"] = None
                context.user_data["wins"] = context.user_data.get("wins", 0) + 1
                await update.message.reply_text(f"🎉 آفرین! {target} بود! در {tries} تلاش! 🏆")
            elif num < target:
                await update.message.reply_text(f"⬆️ بزرگتر! (تلاش {tries})")
            else:
                await update.message.reply_text(f"⬇️ کوچیکتر! (تلاش {tries})")
            return True

    elif game == "rps":
        choices_map = {"سنگ": "🪨", "کاغذ": "📄", "قیچی": "✂️"}
        wins_map = {"سنگ": "قیچی", "کاغذ": "سنگ", "قیچی": "کاغذ"}
        user_choice = next((k for k in choices_map if k in text), None)
        if user_choice:
            bot_choice = random.choice(["سنگ", "کاغذ", "قیچی"])
            if user_choice == bot_choice:
                result = "مساوی! 🤝"
            elif wins_map[user_choice] == bot_choice:
                result = "بردی! 🏆"
                context.user_data["wins"] = context.user_data.get("wins", 0) + 1
            else:
                result = "باختی! 😂"
            context.user_data["game"] = None
            await update.message.reply_text(f"تو: {choices_map[user_choice]}\nمن: {choices_map[bot_choice]}\n\n{result}")
            return True

    elif game == "riddle":
        answer = context.user_data.get("riddle_answer", "")
        if "جواب" in text:
            context.user_data["game"] = None
            await update.message.reply_text(f"جواب: {answer} 🧠")
            return True
        elif answer in text:
            context.user_data["game"] = None
            context.user_data["wins"] = context.user_data.get("wins", 0) + 1
            await update.message.reply_text(f"🎉 آفرین! {answer} بود!")
            return True

    elif game == "word":
        last_char = text[-1]
        word_list = {
            "ب": "برگ", "پ": "پرنده", "ت": "تابستان", "ج": "جنگل",
            "چ": "چشمه", "خ": "خورشید", "د": "دریا", "ر": "رنگین‌کمان",
            "ز": "زمین", "س": "ستاره", "ش": "شاپرک", "ع": "عقاب",
            "ف": "فصل", "ق": "قله", "ک": "کوه", "گ": "گل",
            "ل": "لاله", "م": "مهتاب", "ن": "نسیم", "ه": "هوا", "ی": "یاس",
        }
        bot_word = word_list.get(last_char, None)
        if bot_word:
            await update.message.reply_text(f"🔤 {bot_word}\n(با '{bot_word[-1]}' شروع کن)")
        else:
            await update.message.reply_text("نمیدونم! 😅 تو بردی! 🏆")
            context.user_data["game"] = None
        return True

    return False


# ========================
# پیام‌های متنی
# ========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text_lower = text.lower()
    user_name = update.effective_user.first_name

    context.user_data["message_count"] = context.user_data.get("message_count", 0) + 1

    # پارسا چند؟
    if update.message.reply_to_message and "پارسا" in text_lower:
        await update.message.reply_text(f"پارسا الان *{random.randint(1, 100)}* تاست! 😂", parse_mode="Markdown")
        return

    # حالت AI
    if context.user_data.get("ai_mode"):
        await chat_with_gemini(update, text)
        return

    # بازی‌ها
    if await process_game(update, context, text_lower):
        return

    # دکمه‌های منو
    if text == "😂 جوک":
        await joke(update, context)
    elif text == "🎲 تاس":
        await roll(update, context)
    elif text == "🪙 شیر یا خط":
        await flip(update, context)
    elif text == "📊 آمار من":
        await stats(update, context)
    elif text == "📋 راهنما":
        await help_command(update, context)
    elif text == "🔮 فال":
        await fal(update, context)
    elif text == "🤖 چت با AI":
        context.user_data["ai_mode"] = True
        await update.message.reply_text("🤖 حالت AI روشن شد! هر چی بنویسی Gemini جواب میده 😄\nبرای خاموش کردن /ai بزن")
    elif text == "🎮 بازی‌ها":
        await update.message.reply_text("کدوم بازی؟ 🎮", reply_markup=games_menu())
    elif text == "🔢 بازی عدد":
        await guess_game(update, context)
    elif text == "✂️ سنگ کاغذ قیچی":
        await rps_game(update, context)
    elif text == "🧠 معما":
        await riddle(update, context)
    elif text == "🔤 کلمه بازی":
        await update.message.reply_text("بازی کلمه! یه کلمه بگو 😄")
        context.user_data["game"] = "word"
    elif text == "🏠 برگشت به منو":
        await update.message.reply_text("برگشتیم! 😄", reply_markup=main_menu())

    # چت ساده
    elif any(g in text_lower for g in ["سلام", "هی", "درود", "hello", "hi"]):
        await update.message.reply_text(random.choice(GREET_REPLIES))
    elif any(g in text_lower for g in ["ممنون", "مرسی"]):
        await update.message.reply_text(random.choice(["خواهش میکنم! 😊", "قابلی نداشت 🙏", "هر وقت خواستی! 😎"]))
    elif any(g in text_lower for g in ["خداحافظ", "بای", "bye"]):
        await update.message.reply_text(f"خداحافظ {user_name}! 👋")
    elif "t.me/" in text_lower and update.effective_chat.type != "private":
        await update.message.reply_text("🚫 لینک ممنوع!")
    elif random.random() < 0.15:
        await chat_with_gemini(update, text)


# ========================
# تابع اصلی
# ========================
def main():
    print("🤖 ربات AI داره روشن میشه...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("fal", fal))
    app.add_handler(CommandHandler("guess", guess_game))
    app.add_handler(CommandHandler("rps", rps_game))
    app.add_handler(CommandHandler("riddle", riddle))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ آماده‌ست! 🚀")
    app.run_polling()


if __name__ == "__main__":
    main()
