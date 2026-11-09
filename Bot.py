import os, sqlite3, asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN=os.getenv("BOT_TOKEN","")
ADMIN_IDS={int(x) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip().isdigit()}
PAY_CONTACT=os.getenv("PAY_CONTACT","XVCXHACKS")
DB="xyro.db"
bot=Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher()

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,balance INTEGER DEFAULT 0,status TEXT DEFAULT 'alo',blocked INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,price INTEGER,features TEXT,media TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS promos(code TEXT PRIMARY KEY,amount INTEGER,uses INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS usedpromo(user_id INTEGER,code TEXT,UNIQUE(user_id,code))""")
    c.commit(); return c
def user(uid):
    c=db(); c.execute("INSERT OR IGNORE INTO users(id) VALUES(?)",(uid,)); c.commit()
    return c.execute("SELECT * FROM users WHERE id=?",(uid,)).fetchone()
def mainkb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="👤 PROFIL"),KeyboardButton(text="🛒 CHIT OLISH")],[KeyboardButton(text="🎟 PROMOKOD"),KeyboardButton(text="💰 BALANS TOLDIRISH")]],resize_keyboard=True)
def cancelkb(): return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ BEKOR QILISH")]],resize_keyboard=True)
def isadmin(uid): return uid in ADMIN_IDS

@dp.message(CommandStart())
async def start(m:Message):
    u=user(m.from_user.id)
    if u["blocked"]: return await m.answer("⛔ Hisobingiz bloklangan.")
    await m.answer("✨ <b>XYRO CHEATS BOT</b> ga xush kelibsiz!\n\nKerakli bo‘limni tanlang 👇",reply_markup=mainkb())

@dp.message(F.text=="👤 PROFIL")
async def profile(m:Message):
    u=user(m.from_user.id)
    if u["blocked"]: return await m.answer("⛔ Hisobingiz bloklangan.")
    await m.answer(f"👤 <b>PROFIL</b>\n🆔 ID: <code>{u['id']}</code>\n💰 HISOBINGIZDA: <b>{u['balance']:,} SOM</b>\n📊 HISOB HOLATI: <b>{u['status']}</b>")

@dp.message(F.text=="🛒 CHIT OLISH")
async def shop(m:Message):
    u=user(m.from_user.id)
    if u["blocked"]: return await m.answer("⛔ Hisobingiz bloklangan.")
    c=db(); items=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    if not items: return await m.answer("Hozircha mahsulotlar yo‘q.")
    kb=InlineKeyboardBuilder()
    for p in items: kb.button(text=f"{p['name']} — {p['price']:,} SOM",callback_data=f"prod:{p['id']}")
    kb.adjust(1)
    await m.answer("🛍 <b>KERAKLI BO‘LIMNI TANLANG</b>",reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("prod:"))
async def product(cq:CallbackQuery):
    u=user(cq.from_user.id)
    if u["blocked"]: return await cq.answer("Hisob bloklangan",show_alert=True)
    p=db().execute("SELECT * FROM products WHERE id=?",(int(cq.data.split(":")[1]),)).fetchone()
    if not p: return await cq.answer("Mahsulot topilmadi",show_alert=True)
    text=f"📦 <b>{p['name']}</b>\n⚙️ <b>IMKONIYATLARI</b>\n{p['features'] or '—'}\n\n💵 NARXI: <b>{p['price']:,} SOM</b>\n💰 HISOBINGIZDA: <b>{u['balance']:,} SOM</b>"
    kb=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Sotib olish",callback_data=f"buy:{p['id']}")],[InlineKeyboardButton(text="❌ Bekor qilish",callback_data="cancel")]])
    if p["media"]:
        try:
            if p["media"].startswith("video:"): await cq.message.answer_video(p["media"][6:],caption=text,reply_markup=kb)
            else: await cq.message.answer_photo(p["media"],caption=text,reply_markup=kb)
        except: await cq.message.answer(text,reply_markup=kb)
    else: await cq.message.answer(text,reply_markup=kb)
    await cq.answer()

@dp.callback_query(F.data.startswith("buy:"))
async def buy(cq:CallbackQuery):
    uid=cq.from_user.id; u=user(uid); p=db().execute("SELECT * FROM products WHERE id=?",(int(cq.data.split(":")[1]),)).fetchone()
    if u["blocked"]: return await cq.answer("Hisob bloklangan",show_alert=True)
    if not p: return await cq.answer("Mahsulot topilmadi",show_alert=True)
    if u["balance"]<p["price"]: return await cq.answer("⛔ Tanga yetarli emas!",show_alert=True)
    c=db(); c.execute("UPDATE users SET balance=balance-?,status='urtacha' WHERE id=?",(p["price"],uid)); c.commit()
    await cq.message.answer("✅ Xarid qabul qilindi! Admin siz bilan bog‘lanadi.")
    for aid in ADMIN_IDS:
        try: await bot.send_message(aid,f"🛒 Xarid!\nUser: {uid}\nMahsulot: {p['name']}\nNarx: {p['price']} SOM")
        except: pass
    await cq.answer("Xarid muvaffaqiyatli!")

@dp.callback_query(F.data=="cancel")
async def cancel(cq:CallbackQuery):
    await cq.message.answer("Bekor qilindi.",reply_markup=mainkb()); await cq.answer()

@dp.message(F.text=="🎟 PROMOKOD")
async def promo_prompt(m:Message):
    await m.answer("🎟 PROMOKODNI KIRITING:",reply_markup=cancelkb())

@dp.message(F.text=="❌ BEKOR QILISH")
async def cancel_text(m:Message): await m.answer("Bekor qilindi.",reply_markup=mainkb())

@dp.message(F.text=="💰 BALANS TOLDIRISH")
async def balance(m:Message):
    await m.answer(f"💰 Balans toldirish uchun admin bilan bog‘laning:\n👉 @{PAY_CONTACT}",reply_markup=mainkb())

@dp.message(F.text,~F.text.startswith("/"))
async def promo_use(m:Message):
    code=m.text.strip().upper()
    if code=="❌ BEKOR QILISH": return
    u=user(m.from_user.id)
    if u["blocked"]: return await m.answer("⛔ Hisobingiz bloklangan.")
    c=db(); p=c.execute("SELECT * FROM promos WHERE code=?",(code,)).fetchone()
    if not p: return await m.answer("❌ Promokod noto‘g‘ri yoki mavjud emas.",reply_markup=mainkb())
    try:
        c.execute("INSERT INTO usedpromo VALUES(?,?)",(m.from_user.id,code))
        c.execute("UPDATE users SET balance=balance+?,status='urtacha' WHERE id=?",(p["amount"],m.from_user.id)); c.execute("UPDATE promos SET uses=uses+1 WHERE code=?",(code,)); c.commit()
        await m.answer(f"✅ Promokod aktiv!\n💰 +{p['amount']:,} SOM",reply_markup=mainkb())
    except sqlite3.IntegrityError: await m.answer("⚠️ Bu promokoddan oldin foydalangansiz.",reply_markup=mainkb())

@dp.message(Command("admin"))
async def admin_help(m:Message):
    if not isadmin(m.from_user.id): return
    await m.answer("""<b>ADMIN BUYRUQLARI</b>
/add NAME | PRICE | FEATURES | MEDIA
MEDIA: photo file_id yoki video:FILE_ID (yoki -)
/promo CODE | AMOUNT
/set UID AMOUNT
/status UID alo|yomon|urtacha|mashenik
/block UID
/unblock UID
/users""")

@dp.message(Command("add"))
async def add_product(m:Message):
    if not isadmin(m.from_user.id): return
    try:
        _,raw=m.text.split(" ",1); name,price,features,media=[x.strip() for x in raw.split("|",3)]
        media="" if media=="-" else media
        db().execute("INSERT INTO products(name,price,features,media) VALUES(?,?,?,?)",(name,int(price),features,media)); db().commit()
        await m.answer("✅ Mahsulot qo‘shildi.")
    except: await m.answer("Format: /add NAME | PRICE | FEATURES | MEDIA")

@dp.message(Command("promo"))
async def addpromo(m:Message):
    if not isadmin(m.from_user.id): return
    try:
        _,raw=m.text.split(" ",1); code,amount=raw.split("|")
        db().execute("INSERT OR REPLACE INTO promos(code,amount,uses) VALUES(?,?,0)",(code.strip().upper(),int(amount))); db().commit()
        await m.answer("✅ Promo yaratildi.")
    except: await m.answer("Format: /promo CODE | AMOUNT")

@dp.message(Command("set"))
async def setbalance(m:Message):
    if not isadmin(m.from_user.id): return
    try:
        _,uid,amount=m.text.split(); user(int(uid)); db().execute("UPDATE users SET balance=?,status='urtacha' WHERE id=?",(int(amount),int(uid))); db().commit(); await m.answer("Balans yangilandi.")
    except: await m.answer("Format: /set UID AMOUNT")

@dp.message(Command("status"))
async def setstatus(m:Message):
    if not isadmin(m.from_user.id): return
    try:
        _,uid,status=m.text.split(); db().execute("UPDATE users SET status=? WHERE id=?",(status,int(uid))); db().commit(); await m.answer("Holat yangilandi.")
    except: await m.answer("Format: /status UID alo|yomon|urtacha|mashenik")

@dp.message(Command("block"))
async def block(m:Message):
    if not isadmin(m.from_user.id): return
    try: uid=int(m.text.split()[1]); db().execute("UPDATE users SET blocked=1,status='mashenik' WHERE id=?",(uid,)); db().commit(); await m.answer("Bloklandi.")
    except: await m.answer("Format: /block UID")
@dp.message(Command("unblock"))
async def unblock(m:Message):
    if not isadmin(m.from_user.id): return
    try: uid=int(m.text.split()[1]); db().execute("UPDATE users SET blocked=0,status='alo' WHERE id=?",(uid,)); db().commit(); await m.answer("Blokdan chiqarildi.")
    except: await m.answer("Format: /unblock UID")
@dp.message(Command("users"))
async def users(m:Message):
    if not isadmin(m.from_user.id): return
    rows=db().execute("SELECT id,balance,status,blocked FROM users ORDER BY id DESC LIMIT 50").fetchall()
    await m.answer("\n".join(f"{r['id']} | {r['balance']} SOM | {r['status']} | block={r['blocked']}" for r in rows) or "User yo‘q")

async def health(request): return web.Response(text="XYRO BOT ONLINE")
async def webserver():
    app=web.Application(); app.router.add_get("/",health)
    runner=web.AppRunner(app); await runner.setup(); site=web.TCPSite(runner,"0.0.0.0",int(os.getenv("PORT","10000"))); await site.start()
async def main():
    if not TOKEN: raise RuntimeError("BOT_TOKEN env variable missing")
    db(); await webserver(); await dp.start_polling(bot)
if __name__=="__main__": asyncio.run(main())
