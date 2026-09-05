import asyncio
import logging
import re
import phonenumbers
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BOT_TOKEN = "8747596897:AAFMQ9vSBn_EHGRI7kjDIdyhfB3BSHsMpOY"
HEADLESS = True

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📱 Create Account", callback_data="create")],
        [InlineKeyboardButton("🔐 Set Password", callback_data="setpassword")],
        [InlineKeyboardButton("🌐 Set Proxy", callback_data="setproxy")],
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("🛑 Cancel", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def validate_phone(phone: str) -> bool:
    try:
        parsed = phonenumbers.parse(phone, None)
        return phonenumbers.is_valid_number(parsed)
    except:
        return False

def create_driver(proxy=None):
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--js-flags=--max_old_space_size=256")
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--window-size=1280,720")

    user_agent = ("Mozilla/5.0 (Linux; Android 12; itel S665L Build/SP1A.210812.016) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36")
    chrome_options.add_argument(f'user-agent={user_agent}')

    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """
    })

    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        'headers': {
            'Origin': 'https://limited.facebook.com',
            'Referer': 'https://limited.facebook.com/reg/?is_two_steps_login=0&cid=103&wtsid=rdr_0uAGfMb5qwNS6wBA6&refsrc=deprecated&_rdr'
        }
    })

    return driver

async def create_facebook_account(phone, password, proxy, update, context):
    driver = create_driver(proxy)
    context.user_data['driver'] = driver
    context.user_data['status'] = 'running'

    try:
        reg_url = "https://limited.facebook.com/reg/?is_two_steps_login=0&cid=103&wtsid=rdr_0uAGfMb5qwNS6wBA6&refsrc=deprecated&_rdr"
        driver.get(reg_url)
        await update.effective_message.reply_text("🌐 পেজ লোড হচ্ছে...", reply_markup=get_main_keyboard())

        await asyncio.sleep(2)
        first = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='firstname']")))
        last = driver.find_element(By.CSS_SELECTOR, "input[name='lastname']")
        first.send_keys("Rahim")
        last.send_keys("Mia")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        await update.effective_message.reply_text("✅ নাম দেওয়া হয়েছে।", reply_markup=get_main_keyboard())

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='birthday_day']")))
            driver.find_element(By.CSS_SELECTOR, "select[name='birthday_day']").send_keys("24")
            driver.find_element(By.CSS_SELECTOR, "select[name='birthday_month']").send_keys("6")
            driver.find_element(By.CSS_SELECTOR, "select[name='birthday_year']").send_keys("2006")
            await asyncio.sleep(1)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            await update.effective_message.reply_text("🎂 জন্মদিন দেওয়া হয়েছে।", reply_markup=get_main_keyboard())
        except:
            pass

        try:
            age = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='age_step_input']")))
            age.send_keys("20")
            await asyncio.sleep(1)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            await update.effective_message.reply_text("🔢 বয়স দেওয়া হয়েছে।", reply_markup=get_main_keyboard())
        except:
            pass

        try:
            ok = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'OK')]")))
            ok.click()
            await update.effective_message.reply_text("✅ OK ক্লিক করা হয়েছে।", reply_markup=get_main_keyboard())
        except:
            pass

        phone_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='reg_email__']")))
        phone_input.clear()
        phone_input.send_keys(phone)
        await asyncio.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        await update.effective_message.reply_text(f"📱 ফোন {phone} দেওয়া হয়েছে।", reply_markup=get_main_keyboard())

        try:
            gender = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='sex'][value='2']")))
            if not gender.is_selected():
                gender.click()
                await asyncio.sleep(0.5)
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                await update.effective_message.reply_text("♀️ লিঙ্গ সিলেক্ট করা হয়েছে।", reply_markup=get_main_keyboard())
        except:
            pass

        pass_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='reg_passwd__']")))
        pass_input.clear()
        pass_input.send_keys(password)
        await asyncio.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "button[name='submit']").click()
        await update.effective_message.reply_text("🔒 পাসওয়ার্ড সাবমিট করা হয়েছে।", reply_markup=get_main_keyboard())

        await asyncio.sleep(5)
        current_url = driver.current_url
        if "confirm" in current_url or "checkpoint" in current_url:
            await update.effective_message.reply_text("⚠️ অ্যাকাউন্ট তৈরি হয়েছে, কিন্তু ভেরিফিকেশন প্রয়োজন।", reply_markup=get_main_keyboard())
        else:
            cookies = driver.get_cookies()
            uid = next((c['value'] for c in cookies if c['name'] == 'c_user'), None)
            if uid:
                await update.effective_message.reply_text(f"🆔 UID: `{uid}`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())
            await update.effective_message.reply_text("✅ অ্যাকাউন্ট তৈরি সম্পূর্ণ!", reply_markup=get_main_keyboard())

        context.user_data['status'] = 'done'
        return True

    except Exception as e:
        logger.error(f"Creation error: {e}")
        await update.effective_message.reply_text(f"❌ ত্রুটি: {str(e)}", reply_markup=get_main_keyboard())
        context.user_data['status'] = 'error'
        return False
    finally:
        if driver:
            driver.quit()
            context.user_data['driver'] = None
            context.user_data['status'] = 'idle'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Facebook Auto Creator Bot*\n\n"
        "নিচের বাটন ব্যবহার করুন:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_keyboard()
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        await query.message.reply_text(
            "📱 ফোন নম্বর পাঠান (যেমন: +8801917463846)\nবাতিল করতে /cancel",
            reply_markup=get_main_keyboard()
        )
        context.user_data['awaiting_phone'] = True

    elif query.data == "setpassword":
        await query.message.reply_text("🔐 পাসওয়ার্ড পাঠান।\nবাতিল করতে /cancel", reply_markup=get_main_keyboard())
        context.user_data['awaiting_password'] = True

    elif query.data == "setproxy":
        await query.message.reply_text("🌐 প্রক্সি পাঠান (http://user:pass@host:port)\nবাতিল করতে /cancel", reply_markup=get_main_keyboard())
        context.user_data['awaiting_proxy'] = True

    elif query.data == "status":
        phone = context.user_data.get('phone', 'সেট করা হয়নি')
        password = context.user_data.get('password', 'ডিফল্ট: 1234@@##')
        proxy = context.user_data.get('proxy', 'সেট করা নেই')
        await query.message.reply_text(
            f"📊 *স্ট্যাটাস*\n\n📱 ফোন: `{phone}`\n🔐 পাসওয়ার্ড: `{password}`\n🌐 প্রক্সি: `{proxy}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_keyboard()
        )

    elif query.data == "cancel":
        for key in ['awaiting_phone', 'awaiting_password', 'awaiting_proxy']:
            context.user_data.pop(key, None)
        await query.message.reply_text("🛑 বাতিল করা হয়েছে।", reply_markup=get_main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if context.user_data.get('awaiting_phone'):
        if not validate_phone(text):
            await update.message.reply_text("❌ সঠিক ফোন নম্বর দিন।", reply_markup=get_main_keyboard())
            return
        context.user_data['phone'] = text
        context.user_data.pop('awaiting_phone')
        password = context.user_data.get('password', '1234@@##')
        proxy = context.user_data.get('proxy')
        await update.message.reply_text(f"✅ ফোন সেট: `{text}`\n🚀 অ্যাকাউন্ট তৈরি শুরু...", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())
        await create_facebook_account(text, password, proxy, update, context)
        return

    if context.user_data.get('awaiting_password'):
        context.user_data['password'] = text
        context.user_data.pop('awaiting_password')
        await update.message.reply_text(f"✅ পাসওয়ার্ড সেট: `{text}`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())
        return

    if context.user_data.get('awaiting_proxy'):
        context.user_data['proxy'] = text
        context.user_data.pop('awaiting_proxy')
        await update.message.reply_text(f"✅ প্রক্সি সেট: `{text}`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())
        return

    await update.message.reply_text("❓ /start দিয়ে শুরু করুন।", reply_markup=get_main_keyboard())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for key in ['awaiting_phone', 'awaiting_password', 'awaiting_proxy']:
        context.user_data.pop(key, None)
    await update.message.reply_text("🛑 বাতিল করা হয়েছে।", reply_markup=get_main_keyboard())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🚀 বট চালু হয়েছে")
    app.run_polling()

if __name__ == "__main__":
    main()