# XYRO CHEATS BOT (Render Web Service)

> Eslatma: botni faqat qonuniy, ruxsat etilgan game-settings yoki raqamli mahsulotlar uchun ishlating. O'yin qoidalarini buzuvchi cheat/hacklarni tarqatish tavsiya etilmaydi.

## Render deploy
1. ZIPni ochib GitHub repositoryga yuklang.
2. Render -> New -> Web Service -> repository.
3. Build: `pip install -r requirements.txt`
4. Start: `python Bot.py`
5. Environment Variables:
   - `BOT_TOKEN` = BotFather token
   - `ADMIN_IDS` = Telegram admin ID (bir nechta bo'lsa vergul bilan)
   - `PAY_CONTACT` = XVCXHACKS (username, @ belgisiz)
6. Deploy.

## Admin buyruqlari
- `/admin` — yordam
- `/add NAME | PRICE | FEATURES | MEDIA` — mahsulot qo'shish
  - MEDIA: Telegram file_id, rasm uchun; video uchun `video:FILE_ID`; bo'sh media `-`
  - FEATURES ichida yangi qatorlar ishlatish mumkin
- `/promo CODE | AMOUNT` — promo kod
- `/set UID AMOUNT` — balans
- `/status UID alo|yomon|urtacha|mashenik` — profil holati
- `/block UID` va `/unblock UID`
- `/users` — oxirgi 50 foydalanuvchi

## Muhim
Render Free disk doimiy emas: SQLite bazasi restart/deployda yo'qolishi mumkin. Doimiy balans va mahsulotlar uchun Render Persistent Disk yoki PostgreSQL ulash kerak.
