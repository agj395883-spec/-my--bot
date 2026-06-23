"""
ربات حرفه‌ای بامزه فارسی
آماده برای Render
"""

import logging
import random
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

# ========================
# توکن از Environment
# ========================
TOKEN = os.environ.get("TOKEN", "توکنت_رو_اینجا_بذار")

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
    "یه گاو رفت کافه گفت: یه قهوه!\nگارسون گفت: اسمت چیه؟\nگاو گفت: گاوم دیگه!\nگارسون نوشت: گاودیگه ☕",
    "مامانم گفت تا اتاقتو جمع نکنی بازی نمیکنی!\nمنم اتاقمو جمع کردم...\nبازی نکردم چون خسته شدم 😂",
    "استاد گفت: فردا امتحان داریم!\nکلاس: اوه!\nاستاد: ولی من آماده‌ام 😎",
    "چرا اسکلت تنها بود؟ چون هیچکی باهاش نبود 💀",
    "معلم پرسید: ۵ ضربدر ۵ چنده؟\nشاگرد: ۲۵!\nمعلم: آفرین!\nشاگرد: آفرین نداره، درسته! 😂",
    "یه نفر رفت آرایشگاه گفت: موهامو کوتاه کن!\nآرایشگر گفت: چقدر؟\nگفت: یه مو! 💈",
    "چرا کامپیوترم آهنگ میخونه؟ چون ویندوز داره! 🎵",
    "یه نفر به دیوار گفت: دیوار!\nدیوار جواب نداد...\nگفت: خب، دیواری دیگه 🧱",
    "چرا پرتقال نمیتونه کامپیوتر بازی کنه؟ چون آبش در میاد! 🍊",
    "استاد: کتابتو بیار!\nمن: نیاوردم!\nاستاد: چرا؟\nمن: چون نخوندم، خجالت کشیدم بیارمش 😅",
    "دو تا صفر داشتن دعوا میکردن!\nیکی گفت: تو هیچی!\naون یکی گفت: خودتی! 0️⃣",
    "چرا ماهی نمیتونه کامپیوتر بازی کنه؟ چون از net میترسه! 🐠",
]

# ========================
# پاسخ‌های چت
# ========================
GREET_REPLIES = [
    "سلام عزیزم! چطوری؟ 😁",
    "اوه اوه کی اومد! سلام 👋",
    "هوی! سلام سلام 🤩",
    "یا علی! سلام داداش 😄",
    "اِ سلام! منتظرت بودم 😏",
    "سلام سلام! خوش اومدی 🎉",
]

HOWRU_REPLIES = [
    "ممنون خوبم! تو چطوری؟ 😊",
    "عالیم! مثل همیشه بی‌نظیر 😎",
    "بد نیستم، ربات هستم دیگه 🤖",
    "الان که تو پیام دادی بهتر شدم 😄",
]

THANKS_REPLIES = [
    "خواهش میکنم! 😊",
    "قابلی نداشت داداش 🙏",
    "هر وقت خواستی بگو! 😎",
    "این حرفا چیه، برادریم 🤝",
]

LOVE_REPLIES = [
    "منم دوستت دارم ولی من ربانم 😂❤️",
    "آخ جون! ولی من با همه اینجام نه فقط تو 😄",
    "مرسی! ولی من قلب ندارم، CPU دارم 🤖❤️",
]

BORED_REPLIES = [
    "حوصلت سر رفته؟ بیا یه بازی کنیم! /guess بزن 🎮",
    "خب یه جوک بگم؟ /joke بزن 😂",
    "بیا معما حل کنیم! /riddle بزن 🧠",
    "بیا تاس بندازیم! /roll بزن 🎲",
]

SMART_REPLIES = [
    "آره جانم؟ 😏",
    "بله بله، گوش میدم 👂",
    "اوهوم... ادامه بده 🤔",
    "جالبه! ولی من باهوش‌ترم 😎",
    "هممم، مطمئنی؟ 🧐",
    "بابا دست بردار 😂",
    "اوکی اوکی، فهمیدم 🙄",
    "واقعاً؟! جالبه 🤔",
    "خب خب، بعدش چی؟ 😄",
    "نه بابا! جدی میگی؟ 😲",
    "باشه، قبول کردم 👍",
]

INSULT_REPLIES = [
    "اینو به آینه بگو 😂",
    "مامانت اینو بدونه؟ 😅",
    "وای چقدر باهوشی 🙄",
    "ممنون، تو هم همینطور 😘",
    "حداقل من ربات هستم، تو چی هستی؟ 😄",
]

# ========================
# منو
# ========================
def main_menu():
    keyboard = [
        [KeyboardButton("😂 جوک"), KeyboardButton("🎮 بازی‌ها")],
        [KeyboardButton("🎲 تاس"), KeyboardButton("🪙 شیر یا خط")],
        [KeyboardButton("📊 آمار من"), KeyboardButton("📋 راهنما")],
        [KeyboardButton("🔮 فال"), KeyboardButton("💡 سوال تصادفی")],
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

    await update.message.reply_text(
        f"سلام {name}! 👋\n\n"
        "من ربات بامزه‌ات هستم 🤖\n"
        "میتونیم باهم حرف بزنیم، بازی کنیم و کلی چیز دیگه!\n\n"
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
        "😂 *جوک و سرگرمی*\n"
        "/joke — جوک تصادفی\n"
        "/flip — شیر یا خط\n"
        "/roll — تاس بنداز\n"
        "/fal — فال بگیر\n"
        "/question — سوال تصادفی\n\n"
        "━━━━━━━━━━━━━━\n"
        "🎮 *بازی‌ها*\n"
        "/guess — بازی حدس عدد\n"
        "/rps — سنگ کاغذ قیچی\n"
        "/riddle — معما\n\n"
        "━━━━━━━━━━━━━━\n"
        "👮 *مدیریت گپ (ادمین)*\n"
        "/ban — بن کردن\n"
        "/mute — میوت کردن\n"
        "/unmute — آنمیوت\n"
        "/warn — اخطار دادن\n"
        "/rules — قوانین گپ\n\n"
        "━━━━━━━━━━━━━━\n"
        "📊 *اطلاعات*\n"
        "/stats — آمار من\n\n"
        "یا فقط باهام حرف بزن! 😄"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=main_menu())

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
        "🔮 یه فرصت طلایی جلوته!",
        "🔮 امروز با یه آدم جالب آشنا میشی",
        "🔮 همه چیز درست میشه، صبور باش 🌟",
    ]
    await update.message.reply_text(random.choice(fals))

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        "💡 اگه یه روز وقت آزاد داشتی چیکار میکردی؟",
        "💡 کدوم ابرقدرت رو انتخاب میکردی؟ پرواز یا نامرئی شدن؟",
        "💡 آخرین باری که واقعاً خندیدی کِی بود؟",
        "💡 اگه جزیره خلوت بودی چه ۳ چیزی میبردی؟",
        "💡 گربه یا سگ؟ چرا؟",
        "💡 اگه ۱۰۰ میلیون داشتی اول چیکار میکردی؟",
    ]
    await update.message.reply_text(random.choice(questions))

async def guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 100)
    context.user_data["game"] = "guess"
    context.user_data["guess_number"] = number
    context.user_data["guess_tries"] = 0
    await update.message.reply_text(
        "🔢 *بازی حدس عدد!*\n\nیه عدد بین ۱ تا ۱۰۰ انتخاب کردم!\nحدس بزن چنده؟ 🤔",
        parse_mode="Markdown"
    )

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["game"] = "rps"
    await update.message.reply_text(
        "✂️ *سنگ کاغذ قیچی!*\n\nانتخاب کن:\n🪨 سنگ\n📄 کاغذ\n✂️ قیچی",
        parse_mode="Markdown"
    )

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
    await update.message.reply_text(
        f"🧠 *معما:*\n\n{r[0]}\n\nجواب بده! (بنویس: جواب)",
        parse_mode="Markdown"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    count = context.user_data.get("message_count", 0)
    wins = context.user_data.get("wins", 0)
    await update.message.reply_text(
        f"📊 *آمار تو*\n\n"
        f"👤 نام: {user.first_name}\n"
        f"🆔 آیدی: `{user.id}`\n"
        f"💬 پیام‌ها: {count}\n"
        f"🏆 برد بازی: {wins}",
        parse_mode="Markdown"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *قوانین گپ:*\n\n"
        "1️⃣ به هم احترام بذارید\n"
        "2️⃣ اسپم ممنوع\n"
        "3️⃣ تبلیغ ممنوع\n"
        "4️⃣ محتوای نامناسب ممنوع\n\n"
        "تخلف = اخطار ← بن! 🔨",
        parse_mode="Markdown"
    )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن! 😤")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.ban_member(user.id)
        await update.message.reply_text(f"🔨 {user.first_name} بن شد! خداحافظ 👋")
    except:
        await update.message.reply_text("نتونستم! ادمینم؟ 🤔")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن! 🤫")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(user.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 {user.first_name} میوت شد! 🤫")
    except:
        await update.message.reply_text("نشد! ادمینم؟ 🤔")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("روی پیام کسی ریپلای بزن!")
        return
    user = update.message.reply_to_message.from_user
    try:
        await update.effective_chat.restrict_member(
            user.id,
            ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
        )
        await update.message.reply_text(f"🔊 {user.first_name} آنمیوت شد! 😄")
    except:
        await update.message.reply_text("نشد! ادمینم؟ 🤔")

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
            await update.message.reply_text(f"🚫 {user.first_name} ۳ اخطار گرفت و بن شد! 🔨")
        except:
            await update.message.reply_text("نتونستم بنش کنم!")
    else:
        await update.message.reply_text(f"⚠️ {user.first_name} اخطار {warns}/3 گرفت! 😤")

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
                await update.message.reply_text(f"🎉 آفرین! درسته! عدد {target} بود!\nدر {tries} تلاش! 🏆")
            elif num < target:
                await update.message.reply_text(f"⬆️ بزرگتر! (تلاش {tries})")
            else:
                await update.message.reply_text(f"⬇️ کوچیکتر! (تلاش {tries})")
            return True

    elif game == "rps":
        choices_map = {"سنگ": "🪨", "کاغذ": "📄", "قیچی": "✂️"}
        wins_map = {"سنگ": "قیچی", "کاغذ": "سنگ", "قیچی": "کاغذ"}
        user_choice = None
        for key in choices_map:
            if key in text:
                user_choice = key
                break
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
            await update.message.reply_text(
                f"تو: {choices_map[user_choice]}\nمن: {choices_map[bot_choice]}\n\n{result}\n\nدوباره؟ /rps"
            )
            return True

    elif game == "riddle":
        answer = context.user_data.get("riddle_answer", "")
        if "جواب" in text:
            context.user_data["game"] = None
            await update.message.reply_text(f"جواب: {answer} 🧠\n\nمعمای دیگه؟ /riddle")
            return True
        elif answer.lower() in text:
            context.user_data["game"] = None
            context.user_data["wins"] = context.user_data.get("wins", 0) + 1
            await update.message.reply_text(f"🎉 آفرین! درسته! جواب {answer} بود!\n\nمعمای دیگه؟ /riddle")
            return True

    elif game == "word":
        last_char = text[-1]
        word_list = {
            "الف": "الفبا", "ب": "برگ", "پ": "پرنده", "ت": "تابستان",
            "ج": "جنگل", "چ": "چشمه", "ح": "حیوان", "خ": "خورشید",
            "د": "دریا", "ر": "رنگین‌کمان", "ز": "زمین", "س": "ستاره",
            "ش": "شاپرک", "ع": "عقاب", "ف": "فصل", "ق": "قله",
            "ک": "کوه", "گ": "گل", "ل": "لاله", "م": "مهتاب",
            "ن": "نسیم", "و": "وطن", "ه": "هوا", "ی": "یاس",
        }
        bot_word = word_list.get(last_char, None)
        if bot_word:
            await update.message.reply_text(f"🔤 {bot_word}\n\nحالا تو! (با '{bot_word[-1]}' شروع کن)")
        else:
            await update.message.reply_text("نمیدونم! 😅 تو برنده شدی! 🏆")
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

    # ================
    # پارسا چند؟ 😄
    # ================
    if (
        update.message.reply_to_message and
        "پارسا" in text_lower
    ):
        await update.message.reply_text(
            f"پارسا؟ 🤔\n"
            f"پارسا الان *{random.randint(1, 100)}* تاست! 😂",
            parse_mode="Markdown"
        )
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
    elif text == "💡 سوال تصادفی":
        await question(update, context)
    elif text == "🎮 بازی‌ها":
        await update.message.reply_text("کدوم بازی؟ 🎮", reply_markup=games_menu())
    elif text == "🔢 بازی عدد":
        await guess_game(update, context)
    elif text == "✂️ سنگ کاغذ قیچی":
        await rps_game(update, context)
    elif text == "🧠 معما":
        await riddle(update, context)
    elif text == "🔤 کلمه بازی":
        await update.message.reply_text("بازی کلمه! یه کلمه بگو، من با آخرین حرفش جواب میدم 😄\nشروع کن:")
        context.user_data["game"] = "word"
    elif text == "🏠 برگشت به منو":
        await update.message.reply_text("برگشتیم! 😄", reply_markup=main_menu())

    # چت هوشمند
    elif any(g in text_lower for g in ["سلام", "هی", "درود", "hello", "hi"]):
        await update.message.reply_text(random.choice(GREET_REPLIES))
    elif any(g in text_lower for g in ["خوبی", "چطوری", "حالت"]):
        await update.message.reply_text(random.choice(HOWRU_REPLIES))
    elif any(g in text_lower for g in ["ممنون", "مرسی", "دستت درد نکنه"]):
        await update.message.reply_text(random.choice(THANKS_REPLIES))
    elif any(g in text_lower for g in ["دوست دارم", "عاشقتم"]):
        await update.message.reply_text(random.choice(LOVE_REPLIES))
    elif any(g in text_lower for g in ["حوصله", "بیکارم", "خسته"]):
        await update.message.reply_text(random.choice(BORED_REPLIES))
    elif any(g in text_lower for g in ["احمق", "خر", "گاو", "ببو"]):
        await update.message.reply_text(random.choice(INSULT_REPLIES))
    elif any(g in text_lower for g in ["خداحافظ", "بای", "bye", "شب بخیر"]):
        await update.message.reply_text(f"خداحافظ {user_name}! زود برگرد 👋")
    elif any(g in text_lower for g in ["جوک", "بخند"]):
        await joke(update, context)
    elif any(g in text_lower for g in ["فال", "آینده"]):
        await fal(update, context)
    elif "t.me/" in text_lower or ("http" in text_lower and update.effective_chat.type != "private"):
        await update.message.reply_text("🚫 لینک ممنوعه توی این گپ!")
    elif random.random() < 0.2:
        await update.message.reply_text(random.choice(SMART_REPLIES))

# ========================
# تابع اصلی
# ========================
def main():
    print("🤖 ربات داره روشن میشه...")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("flip", flip))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("fal", fal))
    app.add_handler(CommandHandler("question", question))
    app.add_handler(CommandHandler("guess", guess_game))
    app.add_handler(CommandHandler("rps", rps_game))
    app.add_handler(CommandHandler("riddle", riddle))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ آماده‌ست! 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()