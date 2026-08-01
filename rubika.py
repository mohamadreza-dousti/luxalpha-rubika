import asyncio
import aiohttp
import json
import hashlib
from database.db import userDB, serviceManagement, general, DBPool
import re
import datetime
import os
import random
from pprint import pprint
from aiohttp import FormData
from dotenv import load_dotenv
from database.db import DBPool
import math
from price.get_price import tether
load_dotenv()

vip_id = os.getenv("VIP_ID")
support_group_id = os.getenv("SUPPORT_GROUP_ID")
photo_group_id = os.getenv("PHOTO_GROUP_ID")

manager = os.getenv("MANAGER")
manager_ch = os.getenv("MANAGER_CH")
me = os.getenv("ME")
me_ch = os.getenv("ME_CH")
manager_users = [manager_ch, manager, me, me_ch]

TOKEN = os.getenv("TOKEN")

file_id_d = os.getenv("FILE_ID_D")
after_buy_pdf = os.getenv("AFTER_BUY_PDF")

file_id_b = os.getenv("FILE_ID_B")
ex_id = os.getenv("EA_ID")

file_id_p = os.getenv("FILE_ID_P")
ex_id_p = os.getenv("EA_ID_P")

file_id_u = os.getenv("FILE_ID_U")

card = os.getenv("CARD_ID")

user_data = {}
URL = f"https://botapi.rubika.ir/v3/{TOKEN}/"

db_pool = DBPool.get_instance()
allUser = userDB(db_pool)
services = serviceManagement(db_pool)
allUser.create_table()
services.create_table_andicator()
services.create_table_license()
services.create_table_services()
services.create_table_trial()
services.create_table_license_pro()
services.create_table_andicator_u()
generall = general(db_pool)
generall.create_table_admin()
generall.create_table_update()

async def check_expirations3(session):
    while True:
        try:
            print("started")
            expired_users = services.get_trial()
            today = datetime.date.today()
            # today = datetime.date(2027, 4, 14)
            print(expired_users)
            for user in expired_users:
                print("in user")
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                pu = services.get_service_u(chat_id)[0]
                user_exp_date = user[1]
                if p == 'trial' or pu == 'trial':
                    print("trial")
                    print(user_exp_date)
                    if user_exp_date and today >= user_exp_date:
                        print("expired")
                        services.set_expiration_notified3(chat_id)
                        services.set_expiration_ban_u(chat_id)
                        if p == 'trial':
                            services.set_service(chat_id=chat_id, service='None')
                        if pu == 'trial':
                            services.set_service_u(chat_id, 'None')
                        msg = "⚠️ مشترک گرامی،اشتراک 3 روزه شما پایان یافته است. برای خرید اشتراک از دستور /خرید استفاده کنید."
                        try:
                            res2 = await send_message(session, chat_id, msg)
                        except:
                            pass
                        res = await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک: trial")
                        print(res)
                        #await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\ntraiding view id 1 : {tid1}\ntraiding view id 2 : {tid2}")
                        try:
                            await ban_user(session, chat_id)
                        except:
                            pass
                        print("finish")
                        await asyncio.sleep(10)

        except:
            pass
        await asyncio.sleep(10800)#10800

async def check_expirations_ban(session):
    while True:
        try:
            expired_users = services.get_expired_users_to_ban()
            
            today = datetime.date.today()
            # today = datetime.date(2027, 9, 11)
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                user_exp_date = user[1]
                if user_exp_date and today >= user_exp_date:
                    services.set_service(chat_id=chat_id, service='None')
                    services.set_expiration_ban(chat_id)
                    try:
                        await ban_user(session, chat_id)
                    except:
                        pass
                    msg = "⚠️ اشتراک شما به پایان رسید.\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
                    try:
                        res2 = await send_message(session, chat_id, msg)
                    except:
                        pass
                    await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}")
                    await asyncio.sleep(15)
        except:
            pass
        await asyncio.sleep(10800)#10800

async def check_expirations(session):
    while True:
        try:
            expired_users = services.get_expired_users_to_notify()
            
            today = datetime.date.today()
            
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service(chat_id)[0]
                user_exp_date = user[1]
                dif = (user_exp_date-today).days
                if user_exp_date and dif <= 3:
                    msg = "⚠️ مشترک گرامی، 3 روز از اشتراک شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
                    try:
                        res2 = await send_message(session, chat_id, msg)
                    except:
                        pass
                    await send_message(session, support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}")
                    services.set_expiration_notified(chat_id)
                    await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

async def check_expirations_ban_u(session):
    while True:
        try:
            expired_users = services.get_expired_users_to_ban_u()
            
            today = datetime.date.today()
            # today = datetime.date(2027, 9, 11)
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service_u(chat_id)[0]
                user_exp_date = user[1]
                if user_exp_date and today >= user_exp_date:
                    services.set_service_u(chat_id=chat_id, service='None')
                    services.set_expiration_ban_u(chat_id)
                    try:
                        await ban_user(session, chat_id)
                    except:
                        pass
                    msg = "⚠️ اشتراک شما به پایان رسید.\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
                    try:
                        res2 = await send_message(session, chat_id, msg)
                    except:
                        pass
                    await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور الترا {p}")
                    await asyncio.sleep(15)
        except:
            pass
        await asyncio.sleep(10800)#10800

async def check_expirations_u(session):
    while True:
        try:
            expired_users = services.get_expired_users_to_notify_u()
            
            today = datetime.date.today()
            
            for user in expired_users:
                chat_id = user[0]
                info = allUser.get_info(chat_id)
                fullname = f"{info[0]} {info[1]}"
                phone = info[2]
                p = services.get_service_u(chat_id)[0]
                user_exp_date = user[1]
                dif = (user_exp_date-today).days
                if user_exp_date and dif <= 3:
                    msg = "⚠️ مشترک گرامی، 3 روز از اشتراک شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
                    try:
                        res2 = await send_message(session, chat_id, msg)
                    except:
                        pass
                    await send_message(session, support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:اندیکاتور {p}")
                    services.set_expiration_notified(chat_id)
                    await asyncio.sleep(10)
        except:
            pass
        await asyncio.sleep(10800)

# async def check_expirations_ban_bot(session):
#     while True:
#         try:
#             expired_users = services.get_expired_users_to_ban_bot()
            
#             today = datetime.date.today()
#             # today = datetime.date(2027, 10, 1)
        
#             for user in expired_users:
#                 chat_id = user[0]
#                 info = allUser.get_info(chat_id)
#                 fullname = f"{info[0]} {info[1]}"
#                 phone = info[2]
#                 p = services.get_service_bot(chat_id)[0]
#                 user_exp_date = user[1]
#                 if p != 'trial' and p != 'None':
#                     if user_exp_date and today >= user_exp_date:
#                         msg = "⚠️ اشتراک لایسنس شما به پایان رسید\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
#                         try:
#                             res2 = await send_message(session, chat_id, msg)
#                         except:
#                             pass
#                         await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:ربات {p}")
#                         services.set_service_bot(chat_id=chat_id, service='None')
#                         services.set_expiration_ban_bot(chat_id)
#                         try:
#                             await ban_user(vip_id, chat_id)
#                         except:
#                             pass
#                     await asyncio.sleep(15)
#         except:
#             pass
#         await asyncio.sleep(10800)

# async def check_expirations_pro(session):
#     while True:
#         try:
#             expired_users = services.get_expired_users_to_notify_bot_pro()
            
#             today = datetime.date.today()
            
#             for user in expired_users:
#                 chat_id = user[0]
#                 info = allUser.get_info(chat_id)
#                 fullname = f"{info[0]} {info[1]}"
#                 phone = info[2]
#                 p = services.get_service_pro(chat_id)[0]
#                 user_exp_date = user[1]
#                 if p != 'trial' and p != 'None':
#                     dif = (user_exp_date-today).days
#                     if user_exp_date and dif <= 3:
#                         msg = "⚠️ مشترک گرامی، 3 روز از اشتراک لایسنس شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
#                         try:
#                             res2 = await send_message(session, chat_id, msg)
#                         except:
#                             pass
#                         await send_message(session, support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:ربات پرو {p}")
#                         services.set_expiration_notified_bot_pro(chat_id)
#                         await asyncio.sleep(15)
#         except:
#                 pass
#         await asyncio.sleep(10800)

# async def check_expirations_ban_pro(session):
#     while True:
#         try:
#             expired_users = services.get_expired_users_to_ban_bot_pro()
            
#             today = datetime.date.today()
#             # today = datetime.date(2027, 10, 1)
        
#             for user in expired_users:
#                 chat_id = user[0]
#                 info = allUser.get_info(chat_id)
#                 fullname = f"{info[0]} {info[1]}"
#                 phone = info[2]
#                 p = services.get_service_pro(chat_id)[0]
#                 user_exp_date = user[1]
#                 if p != 'trial' and p != 'None':
#                     if user_exp_date and today >= user_exp_date:
#                         msg = "⚠️ اشتراک لایسنس شما به پایان رسید\nبرای خرید اشتراک از دستور /خرید استفاده کنید."
#                         try:
#                             res2 = await send_message(session, chat_id, msg)
#                         except:
#                             pass
#                         await send_message(session, support_group_id, f"اشتراک کاربر به پایان رسید:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:ربات پرو {p}")
#                         services.set_service_pro(chat_id=chat_id, service='None')
#                         services.set_expiration_ban_bot_pro(chat_id)
#                         try:
#                             await ban_user(vip_id, chat_id)
#                         except:
#                             pass
#                     await asyncio.sleep(15)
#         except:
#             pass
#         await asyncio.sleep(10800)

# async def check_expirations_bot(session):
#     while True:
#         try:
#             expired_users = services.get_expired_users_to_notify_bot()
            
#             today = datetime.date.today()
            
#             for user in expired_users:
#                 chat_id = user[0]
#                 info = allUser.get_info(chat_id)
#                 fullname = f"{info[0]} {info[1]}"
#                 phone = info[2]
#                 p = services.get_service_bot(chat_id)[0]
#                 user_exp_date = user[1]
#                 if p != 'trial' and p != 'None':
#                     dif = (user_exp_date-today).days
#                     if user_exp_date and dif <= 3:
#                         msg = "⚠️ مشترک گرامی، 3 روز از اشتراک لایسنس شما باقی مانده است. برای تمدید از دستور /تمدید استفاده کنید."
#                         try:
#                             res2 = await send_message(session, chat_id, msg)
#                         except:
#                             pass
#                         await send_message(session, support_group_id, f"سه روز از اشتراک کاربر باقی مانده:\nنام و نام خانوادگی:{fullname}\nشماره تلفن:{phone}\nاشتراک:ربات {p}")
#                         services.set_expiration_notified_bot(chat_id)
#                         await asyncio.sleep(15)
#         except:
#                 pass
#         await asyncio.sleep(10800)


after_buy = """
        فعال‌سازیِ دسترسی شما ✅

        «واریزیِ شما توسطِ تیم فنی تأیید شد. به تیمِ حرفه‌ای LUXalpha خوش آمدید! 💎

        دسترسیِ شما به اندیکاتور در اکانتِ تریدینگ‌ویو فعال شد.

        برای مشاهده و استفاده، کافیست:

        1. واردِ سایتِ TradingView شوید.

        2. از منوی بالا به بخش Indicators بروید.

        3. در تبِ Invite-only scripts، اندیکاتور LUXalpha برای شما ظاهر شده است؛ آن را روی نمودار فعال کنید

        4.توافق‌نامه سلب مسئولیت:

شما می‌پذیرید که اندیکاتورهای LUXalpha و ربات های luxalpha صرفاً ابزارهای کمکی جهت تحلیل بوده و مسئولیت نهایی تمامی معاملات، مدیریت سرمایه و حد ضرر، مستقیماً بر عهده تریدر است. ما هیچ‌گونه تعهدی نسبت به نتایج معاملات شخصی شما نداریم
        
        """

acceptment = """
کاربر گرامی، جهت فعال‌سازی اشتراک ماهانه و دسترسی به ابزارهای معاملاتی، لطفاً موارد زیر را مطالعه کرده و در صورت موافقت، اطلاعات خواسته شده را تکمیل و ارسال نمایید:

۱. توافق‌نامه سلب مسئولیت:

شما می‌پذیرید که اندیکاتورهای LUXalpha صرفاً ابزارهای کمکی جهت تحلیل بوده و مسئولیت نهایی تمامی معاملات، مدیریت سرمایه و حد ضرر، مستقیماً بر عهده تریدر است. ما هیچ‌گونه تعهدی نسبت به نتایج معاملات شخصی شما نداریم.

۲. سیاست ضمانت بازگشت وجه (بسیار مهم):

تیم LUXalpha به عملکرد ابزارهای خود اطمینان کامل دارد. در صورتی که پس از استفاده مستمر و طبق آموزش (در تایم‌فریم و نمادهای تعیین شده) در طول یک ماه تقویمی، برآیند حساب شما با رعایت مدیریت ریسکِ استاندارد (ریسک ۱٪ در هر معامله) منفی باشد، کل مبلغ پرداختی بدون هیچ سوالی به شما عودت داده می‌شود.

(تبصره: برای استفاده از این گارانتی، ارسال تاریخچه تریدها (History) از پنل TradingView الزامی است).

۳. شرایط استرداد:

با توجه به ماهیت فایل‌های دیجیتال و دسترسی آموزشی، استرداد وجه تنها در صورت «ضرری بودن برآیندِ سیستم» امکان‌پذیر است و در موارد دیگر (مثل پشیمانی پس از خرید یا عدم تمایل به استفاده)، وجهی عودت داده نخواهد شد.
                               """

after_start = """به اکوسیستم معاملاتی LUXalpha خوش آمدید. 💎

ما اینجا هستیم تا به شما کمک کنیم با ابزارهایی معامله کنید که بر پایه منطق، استراتژی و دانشِ مهندسی بنا شده‌اند، نه حدس و گمان.


ما اینجا با استفاده از بروزترین متدهای اسمارت‌مانی و اندیکاتورهای اختصاصی خودمون، معاملات رو از حالت شانسی به یک بیزینس دقیق و سودده تبدیل کردیم.


برای اینکه بتونی دسترسی ۳ روزه رایگان رو دریافت کنی و نتایج لایو ما رو ببینی، لطفاً عدد 10 رو همین‌جا برام بفرست."""


after_100 = """لیست ابزارهای اختصاصی LUXalpha 🛠️

ما برای هر سطح از تجربه و هر استراتژی معاملاتی، ابزار اختصاصی خودمان را توسعه داده‌ایم. محصول مورد نظر خود را انتخاب کنید:

۱. اندیکاتور اختصاصی LUXalpha 📉
این ابزار، “دستیارِ چشم‌های شماست.” اگر به تحلیل شخصی علاقه‌مندید و می‌خواهید تصمیم‌گیرنده نهایی باشید، اما به دنبال دقتی در حدِ هوش مصنوعی هستید، این انتخاب برای شماست.

مناسب برای: تریدرهایی که می‌خواهند نقاط ورود و خروج را خودشان تأیید کنند.
مزیت اصلی: شناسایی ترندهای اصلی، فیلتر کردن نویزهای بازار و سیگنال‌دهی با دقت بالا.
هدف: کاهش خطای محاسباتی در تحلیل‌های دستی.
۲. ربات معامله‌گر تمام‌اتوماتیک LUXalpha 🤖
این ابزار، “پایلوتِ خودکارِ شماست.” اگر به دنبال آزادی عمل هستید و می‌خواهید بدون درگیری با استرس و احساساتِ لحظه‌ای، سیستم به‌صورت ۲۴ ساعته برای شما ترید کند، این محصول برای شماست.

مناسب برای: تریدرهایی که به دنبال مدیریت ریسکِ سیستماتیک و اتوماسیون کامل هستند.
مزیت اصلی: ورود و خروج پله‌ای (Partial Take Profit)، مدیریت ریسک هوشمند و عملکرد بدون وقفه.
هدف: حذف کامل خطای انسانی و مدیریت سرمایه بهینه."""

after_10 = """خیلی خوشحالم که برای ارتقای سطح تریدینگت، ما رو انتخاب کردی.

ما اینجا با استفاده از بروزترین متدهای اسمارت‌مانی و اندیکاتورهای اختصاصی خودمون، معاملات رو از حالت شانسی به یک بیزینس دقیق و سودده تبدیل کردیم.

برای اینکه بتونی دسترسی ۳ روزه رایگان رو دریافت کنی و نتایج لایو ما رو ببینی، لطفاً عدد 10 رو همین‌جا برام بفرست."""





questions = """
سوالات متداول:
۱. اندیکاتور روی گوشی (موبایل) نصب میشه؟
پاسخ: اندیکاتورهای ما به‌طور اختصاصی برای پلتفرم TradingView طراحی شده‌اند. شما می‌توانید تریدینگ‌ویو را روی موبایل (اندروید/آیفون) نصب کنید و از اندیکاتور ما استفاده کنید. اما برای تحلیل دقیق‌تر و مدیریت بهتر ترید، استفاده از لپ‌تاپ یا کامپیوتر (نسخه تحت وب تریدینگ‌ویو) پیشنهاد می‌شود.

۲. آیا سود این اندیکاتور تضمین شده است؟
پاسخ: در بازارهای مالی هیچ‌چیز تضمین ۱۰۰٪ ندارد. سیستم LUXalpha یک «ابزار هوشمند تحلیل» است که بر اساس پرایس‌اکشن و اسمارت‌مانی (SMC) به شما نقاط ورود و خروج می‌دهد. وین‌ریت (نرخ برد) ما ۷۰٪ است، اما موفقیت نهایی به «مدیریت سرمایه» خودِ شما بستگی دارد. ما به شما ابزار موفقیت می‌دهیم، نه ضمانت سود بدونِ دانش.

۳. اگر ضرر کنم چی؟ سیستم گارانتی داره؟
پاسخ: ما به قدرت سیستم‌مان ایمان داریم. اگر در طول یک ماه تقویمی، با رعایت «مدیریت ریسک استاندارد» (۱٪ ریسک در هر معامله)، برآیند حساب شما منفی بود، کل مبلغ اشتراک ماهانه شما تمام و کمال استرداد می‌شود. (تأکید: رعایت مدیریت ریسک شرط اصلی این ضمانت است).

۴. برای کار با این اندیکاتور چقدر دانش باید داشته باشم؟
پاسخ: ما برای شما ویدیوهای آموزشی اختصاصی ارسال می‌کنیم که صفر تا صد کار با اندیکاتور را توضیح داده است. برای شروع، آشنایی مقدماتی با نحوه ثبت سفارش (Order) در صرافی یا بروکر کافی است.

۵. از کجا بدونم کلاهبرداری نیست؟
پاسخ: اعتماد شما سرمایه ماست. به همین دلیل ما «تست رایگان ۳ روزه» داریم تا خودتان با چشمان خودتان عملکرد سیستم را در محیط لایو (گروه سیگنال) مشاهده کنید. همچنین دفتر ما در تهران پاسخگوی شماست و فعالیت ما کاملاً رسمی است.

۶. هزینه اشتراک چقدره و چطور باید پرداخت کنم؟
پاسخ: ما پلن‌های مختلفی (پایه، پیشرفته، حرفه‌ای) داریم. قیمت‌ها بسته به نوع پلن و قابلیت‌های اندیکاتور متفاوت است. جهت دریافت قیمت دقیق و شماره کارت/تتر، لطفاً در پیام‌رسان (بله/روبیکا) پیام دهید تا لیست کامل پکیج‌ها برایتان ارسال شود.

۷. میشه اندیکاتور رو روی سیستم خودم داشته باشم؟ (کپی‌برداری)
پاسخ: اندیکاتورهای LUXalpha دارای قفل امنیتی هستند و روی اکانت تریدینگ‌ویوِ شخصی شما فعال می‌شوند. این یعنی شما فقط «مجوز استفاده» دارید و امکان کپی‌برداری یا اشتراک‌گذاری با دیگران به دلیل لایسنس‌های امنیتی وجود ندارد.

۸. بهترین تایم‌فریم و نماد معاملاتی برای این اندیکاتور چیه؟
پاسخ: اندیکاتورهای ما بر اساس سشن معاملاتی نیویورک بهینه‌سازی شده‌اند. به وقت ایران، بهترین زمان برای استفاده از این ابزار و انجام معاملات، بازه زمانی ۱۳:۳۰ الی ۲۲:۰۰ است. ما این بازه زمانی را به مشتریانمان توصیه می‌کنیم، زیرا این کار باعث می‌شود معامله‌گری شما از حالت «شلوغ و پراکنده» خارج شده و با ایجاد یک نظم مشخص، در بهترین زمانِ نقدینگی بازار ترید کنید. جزئیات مربوط به تایم‌فریم‌های اختصاصی نیز در ویدیوی آموزشی که پس از خرید دریافت می‌کنید، به صورت کامل تشریح شده است.

۹.آیا برای استفاده از اندیکاتورهای LUXalpha حتماً باید اکانت پریمیوم (پولی) تریدینگ‌ویو داشته باشم؟

پاسخ: خیر، اصلاً نیازی به تهیه اکانت پریمیوم نیست. اندیکاتورهای ما به‌گونه‌ای بهینه‌سازی شده‌اند که روی نسخه رایگان (Free Plan) تریدینگ‌ویو هم بدون هیچ مشکلی کار می‌کنند. تنها نکته این است که در نسخه رایگان، شما محدود به استفاده از تعداد محدودی اندیکاتور به‌صورت همزمان هستید که سیستم ما با این محدودیت کاملاً سازگار است. بنابراین شما می‌توانید بدون پرداخت هیچ هزینه اضافی به تریدینگ‌ویو، از قدرت کامل ابزارهای ما بهره‌مند شوید
"""

after_register = """بسیار عالی! خوش‌آمدی به جمع تریدرهای هوشمند LUXalpha. 🚀
اگر میخوای تست 3 روزه رو دریافت کنی کافیه به من پیام بدی تا دسترسی رو 3 روز رایگان بهت بدم
    @luxalpha
    
اگر هم قصد خرید لایسنس رو داری از قسمت پایین اندیکاتوری که مد نظرته رو انتخاب کن و خریدت رو کامل کن
هر سوالی داشتی من کنارتم😉"""

keyboard_admin = {
    "rows": [
        {
        "buttons":
        [
            {
                "id": "brdcast",
                "type": "Simple",
                "button_text": "ارسال پیام گروهی"
            }
        ]
        }
    ],
        "resize_keyboard": True
}

keyboard_service = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "اندیکاتور لوکس الفا الترا",
                    "type": "Simple",
                    "button_text": "اندیکاتور لوکس الفا الترا مخصوص طلا📊📈"
                },
            ]
        },
        {
            "buttons": [
                {
                    "id": "اندیکاتور",
                    "type": "Simple",
                    "button_text": "اندیکاتور لوکس الفا📊📈"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

keyboard_service1 = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "اندیکاتور لوکس الفا الترا",
                    "type": "Simple",
                    "button_text": "اندیکاتور لوکس الفا الترا مخصوص طلا📊📈"
                },
            ]
        },
        {
            "buttons": [
                {
                    "id": "اندیکاتور",
                    "type": "Simple",
                    "button_text": "اندیکاتور لوکس الفا📊📈"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "req",
                    "type": "Simple",
                    "button_text": "درخواست عضویت در گروه VIP"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

learn_keyboard = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "la1",
                    "type": "Simple",
                    "button_text": "دریافت اموزش اندیکاتور لوکس الفا📚"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "req",
                    "type": "Simple",
                    "button_text": "درخواست عضویت در گروه VIP"
                }
            ]
        },
        {
            'buttons': [
                {
                    "id": "lu1",
                    "type": "Simple",
                    "button_text": "دریافت اموزش  اندیکاتور لوکس الفا الترا📚"
                }
            ]
        }
    ],
    "resize_keyboard":True      
}

keyboard_learn_an = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "la",
                    "type": "Simple",
                    "button_text": "دریافت اموزش اندیکاتور لوکس الفا📚"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "ca",
                    "type": "Simple",
                    "button_text": "ادامه خرید اندیکاتور لوکس الفا🛒"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

keyboard_learn_anu = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "lau",
                    "type": "Simple",
                    "button_text": "دریافت اموزش اندیکاتور لوکس الفا الترا مخصوص طلا📚"
                },
            ]
        },
        {
            "buttons": [
                {
                    "id": "cau",
                    "type": "Simple",
                    "button_text": "ادامه خرید اندیکاتور لوکس الفا الترا مخصوص طلا🛒"
                }
            ]
        }
    ],
    "resize_keyboard":True
}


# keyboard_learn_ea = {
#     "rows": [
#         {
#             "buttons": [
#                     {
#                         "id": "le",
#                         "type": "Simple",
#                         "button_text": "دریافت اموزش ربات📚"
#                     },
#                     {
#                         "id": "ce",
#                         "type": "Simple",
#                         "button_text": "ادامه خرید ربات🛒"
#                     }
#                 ]
#         }
#     ],
#     "resize_keyboard":True
# }

# keyboard_learn_eap = {
#     "rows": [
#         {
#             "buttons": [
#                     {
#                         "id": "lep",
#                         "type": "Simple",
#                         "button_text": "دریافت اموزش ربات📚"
#                     },
#                     {
#                         "id": "cep",
#                         "type": "Simple",
#                         "button_text": "ادامه خرید ربات پرو🛒"
#                     }
#                 ]
#         }
#     ],
#     "resize_keyboard":True
# }

keyboard_service_re = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "اندیکاتور",
                    "type": "Simple",
                    "button_text": "تمدید اندیکاتور لوکس الفا📊📈"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "اندیکاتور الترا",
                    "type": "Simple",
                    "button_text": "تمدید اندیکاتور لوکس الفا الترا مخصوص طلا📊📈"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

keyboard_support = {
    "rows": [
        {
            "buttons": [
                    {
                        "id": "10",
                        "type": "Simple",
                        "button_text": "گزینه 1"
                    },
                    {
                        "id": "20",
                        "type": "Simple",
                        "button_text": "گزینه 2"
                    }
                ]
        }
    ],
    "resize_keyboard":True
}

keyboard_plan = {
        "rows": [
            {
                "buttons": [
                    {
                        "id": "1",
                        "type": "Simple",
                        "button_text": "یک ماهه"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "2",
                        "type": "Simple",
                        "button_text": "سه ماهه"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "3",
                        "type": "Simple",
                        "button_text": "شش ماهه"
                    }
                ]
            }
        ],
        "resize_keyboard":True
    }

keyboard_plan_au = {
        "rows": [
            {
                "buttons": [
                    {
                        "id": "1u",
                        "type": "Simple",
                        "button_text": "یک ماهه الترا"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "2u",
                        "type": "Simple",
                        "button_text": "سه ماهه الترا"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "3u",
                        "type": "Simple",
                        "button_text": "شش ماهه الترا"
                    }
                ]
            }
        ],
        "resize_keyboard":True
    }

# keyboard_plan_b = {
#         "rows": [
#             {
#                 "buttons": [
#                     {
#                         "id": "1b",
#                         "type": "Simple",
#                         "button_text": "بات یک ماهه"
#                     }
#                 ]
#             },
#             {
#                 "buttons": [
#                     {
#                         "id": "2b",
#                         "type": "Simple",
#                         "button_text": "بات سه ماهه"
#                     }
#                 ]
#             },
#             {
#                 "buttons": [
#                     {
#                         "id": "3b",
#                         "type": "Simple",
#                         "button_text": "بات شش ماهه"
#                     }
#                 ]
#             }
#         ],
#         "resize_keyboard":True
#     }

# keyboard_plan_bp = {
#         "rows": [
#             {
#                 "buttons": [
#                     {
#                         "id": "1bp",
#                         "type": "Simple",
#                         "button_text": "بات پرو یک ماهه"
#                     }
#                 ]
#             },
#             {
#                 "buttons": [
#                     {
#                         "id": "2bp",
#                         "type": "Simple",
#                         "button_text": "بات پرو سه ماهه"
#                     }
#                 ]
#             },
#             {
#                 "buttons": [
#                     {
#                         "id": "3bp",
#                         "type": "Simple",
#                         "button_text": "بات پرو شش ماهه"
#                     }
#                 ]
#             }
#         ],
#         "resize_keyboard":True
#     }

keyboard_wallet = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "1",
                    "type": "Simple",
                    "button_text": "bep20"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "2",
                    "type": "Simple",
                    "button_text": "trc20"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

keyboard_pay = {
    'rows': [
        {
            'buttons':[
                {
                    'id': 'ri',
                    'type': 'Simple',
                    'button_text': 'ریالی'
                },
                {
                    'id': 'di',
                    'type': 'Simple',
                    'button_text': 'ارز دیجیتال'
                }
            ]
        }
    ],
    'resize_keyboard':True
}

keyboard_filter = {
        "rows": [
            {
                "buttons": [
                    {
                        "id": "a",
                        "type": "Simple",
                        "button_text": "کاربران فعال"
                    },
                    {
                        "id": "t",
                        "type": "Simple",
                        "button_text": "کاربران تستی"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "1m",
                        "type": "Simple",
                        "button_text": "کاربران یک ماهه"
                    },
                    {
                        "id": "3m",
                        "type": "Simple",
                        "button_text": "کاربران سه ماهه"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "6m",
                        "type": "Simple",
                        "button_text": "کاربران شش ماهه"
                    },
                    {
                        "id": "3m",
                        "type": "Simple",
                        "button_text": "کاربران یک ماهه الترا"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "6m",
                        "type": "Simple",
                        "button_text": "کاربران سه ماهه الترا"
                    },
                    {
                        "id": "3m",
                        "type": "Simple",
                        "button_text": "کاربران یک شش الترا"
                    }
                ]
            },
            {
                "buttons": [
                    {
                        "id": "da",
                        "type": "Simple",
                        "button_text": "کاربران بدون اشتراک"
                    }
                ]
            }
        ],
        "resize_keyboard":True
}

keyboard_help = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "h1",
                    "type": "Simple",
                    "button_text": "/خرید"
                },
                {
                    "id": "h2",
                    "type": "Simple",
                    "button_text": "/ویرایش"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "h3",
                    "type": "Simple",
                    "button_text": "/پروفایل"
                },
                {
                    "id": "h4",
                    "type": "Simple",
                    "button_text": "/پشتیبانی"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "h5",
                    "type": "Simple",
                    "button_text": "/سوالات متداول"
                },
                {
                    "id": "h6",
                    "type": "Simple",
                    "button_text": "/عکس"
                },
                {
                    "id": "h7",
                    "type": "Simple",
                    "button_text": "/تمدید"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "h8",
                    "type": "Simple",
                    "button_text": "/مدیر"
                },
                {
                    "id": "h9",
                    "type": "Simple",
                    "button_text": "/ادمین"
                },
                {
                    "id": "h10",
                    "type": "Simple",
                    "button_text": "10"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

keyboard_manager = {
    "rows": [
        {
            "buttons": [
                {
                    "id": "a",
                    "type": "Simple",
                    "button_text": "امار کاربران"
                },
                {
                    "id": "t",
                    "type": "Simple",
                    "button_text": "دریافت چت ایدی"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "1m",
                    "type": "Simple",
                    "button_text": "افزودن ادمین"
                },
                {
                    "id": "3m",
                    "type": "Simple",
                    "button_text": "حذف ادمین"
                }
            ]
        },
        {
            "buttons": [
                {
                    "id": "exn",
                    "type": "Simple",
                    "button_text": "خروجی کاربران"
                },
                {
                    "id": "ex",
                    "type": "Simple",
                    "button_text": "خروجی کاربران جدید"
                }
            ]
        }
    ],
    "resize_keyboard":True
}

load_dotenv()

file_path  = "C:/Users/mohamadreza/desktop/luxalpha/lab.jpg"

import aiohttp
import asyncio

class RubikaUploader:

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

async def up_doc(session):
    data = {
        "type": "File",
    }
    url = f'{URL}requestSendFile'
    response =await session.post(url, json=data)
    data = await response.json()
    data = data.get("data", {})
    u = data.get("upload_url", "")
    form = FormData()
    with open("users.txt", 'rb') as f:
        form.add_field('file', f, filename='users.txt')
        fid = await session.post(u, data=form)
    fid = await fid.json()
    return fid['data']['file_id']

async def up_docc(session):
    data = {
        "type": "Image",
    }
    url = f'{URL}requestSendFile'
    response =await session.post(url, json=data)
    print(response.text)
    data = await response.json()
    data = data.get("data", {})
    u = data.get("upload_url", "")
    return u

async def upload_image(session, upload_url, path):
    form = FormData()

    with open(path, "rb") as f:
        form.add_field(
            name="file",          # خیلی مهم: دقیقاً file
            value=f,
            filename=path.split("/")[-1],
            content_type="image/jpeg"
        )

        async with session.post(upload_url, data=form) as resp:
            text = await resp.text()
            print("STATUS:", resp.status)
            print("RESPONSE:", text)

            return await resp.json()

async def create_license(chat_id, counter):
    chat_id = str(chat_id) + str(counter)
    chat_id = str(chat_id).encode('utf-8')
    c = hashlib.sha256(chat_id)
    c = c.hexdigest()[:21].upper()
    c = 'MT5LUXALPHA'+str(c)
    return c


async def broadcast_message(session, user_ids, text):
    for chat_id in user_ids:
        try:
            await send_message(session, chat_id, text)
            await asyncio.sleep(random.uniform(2.0, 4.8))
        except Exception as e:
            print(f"{chat_id}: {e}")
            await asyncio.sleep(10)

async def edit_caption(session, chat_id, message_id, caption):
    payload = {
        "chat_id":chat_id,
        "message_id":message_id,
        "caption":caption
    }
    await session.post(URL + "editMessageCaption", json=payload)

async def edit_text(session, msg_id, text):
    data = {
        "chat_id": support_group_id,
        "message_id": msg_id,
        "text": text
    }
    await session.post(URL+"editMessageText", json=data)


async def edit_text2(session, msg_id, text):
    data = {
        "chat_id": photo_group_id,
        "message_id": msg_id,
        "text": text
    }
    await session.post(URL+"editMessageText", json=data)

async def edit_text3(session, msg_id, text):
    data = {
        "chat_id": manager_ch,
        "message_id": msg_id,
        "text": text
    }
    await session.post(URL+"editMessageText", json=data)



async def send_keyboard(session, chat_id, text, rep):
    url = f"{URL}sendMessage"
    
    payload = {
        "chat_id": str(chat_id),
        "text": text,
        "reply_markup": rep
    }
    await session.post(url, json=payload)

async def code(chat_id):
    chat_id = str(chat_id).encode('utf-8')
    c = hashlib.sha256(chat_id)
    return c.hexdigest()[:6].upper()

async def delete_message(session, chat_id, message_id):
    await session.post(URL + "deleteMessage", json={
        "chat_id": chat_id,
        "message_id": message_id
    })

async def send_message(session, chat_id, text):
    response = await session.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text,
    })
    return response

async def send_message_keyboard(session, chat_id, text, rep):
    response = await session.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "chat_keypad": rep,
        "chat_keypad_type": "New"
    })

async def remove_keyboard(session, chat_id, text):
    response = await session.post(URL + "sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "chat_keypad_type": "Remove"
    })

async def get_photo_url(session):
    data = {
        "type": "Image",
    }
    url = f'{URL}requestSendFile'
    response = await session.post(url, json=data)
    data = await response.json()
    data = data.get("data", {})
    u = data.get("upload_url", "")

async def send_photo(session, chat_id, id, caption="LUXalpha"):
    payload = {
        "chat_id": str(chat_id),
        "file_id": id,
        "text": caption
    }
    res = await session.post(URL + "sendFile", json=payload)
    print(await res.json())

async def send_film(session, chat_id, file_id):
    payload = {
        "chat_id": str(chat_id),
        "file_id": file_id
    }
    res = await session.post(URL + "sendFile", json=payload)
    res = await res.json()
    return res

async def send_file(session, chat_id, file_id):
    payload = {
        "chat_id": str(chat_id),
        "file_id": file_id
    }
    res = await session.post(URL + "sendFile", json=payload)

async def forward_photo(session, fro, id, to):
    data = {
        "from_chat_id": fro,
        "message_id": id,
        "to_chat_id": to
    }
    res = await session.post(URL+"forwardMessage", json=data)
    print(await res.json())
    print(await res.text()) 

async def ban_user(session, user_id):
    data = {
        "chat_id": vip_id,
        "user_id": user_id,
    }
    response = await session.post(URL+"banChatMember", json=data)
    await asyncio.sleep(1)

async def edit_message(session, group_id, m_id, text, rep):
    pay = {
        "chat_id": group_id,
        "message_id":m_id,
        "text": text, 
        "reply_markup":rep
    }
    await session.post(URL+"editMessageText", json=pay)

async def handle_message(session, update):
    chat_id = update["chat_id"]
    message = update['new_message']
    text = str(message.get('text', ''))
    user_id = message['sender_id']
    chat_type = message['sender_type']

    if text == "/start" and chat_type == 'User':
        await send_message_keyboard(session, chat_id, after_start, keyboard_help)
    
    # elif text == "100":
    #     await send_message_keyboard(session, chat_id, after_100, keyboard_help)
    #     await send_message_keyboard(session, chat_id, after_10, keyboard_help)
        
    elif text == "10" and chat_type == 'User':
        exist = allUser.check_user(chat_id)
        if exist:
            try:
                date = services.get_date_3(chat_id)[0]
            except Exception as e:
                date = None
            res = await send_message(session, chat_id, f"""شما در طرح سه روزه عضو شده اید.\nتاریخ پایان:{date}""")
            print(res)
        else:
            await send_message(session, chat_id, "نام خود را وارد کنید:")
            user_data[chat_id] = {"step":"GET_NAME", "command":"10"}

#     elif text == "ربات پرو🤖💹":
#         await send_message_keyboard(session, chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
# """, keyboard_learn_eap)
#     elif text == "دریافت اموزش ربات📚":
#         await send_message_keyboard(session, chat_id, "برای مشاهده اموزش روی لینک زیر کلیک کنید\nhttps://aparat.com/v/mvatez2", keyboard_learn_eap)
#     elif text == "ادامه خرید ربات پرو🛒":
#         k = allUser.check_user(chat_id)
#         try:
#             ser = services.get_service_pro(chat_id)[0]
#         except:
#             ser = "None"
#         if not k:
#             await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
#         elif ser != "None" and ser != "trial" and ser != None:
#             await send_message(session, chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
#         else:
#             await send_photo(session, chat_id, file_id_p, "LUXALPHA PRO BOTS")
#             await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_bp)
#             user_data[chat_id] = {"step":"plbp"}

#     elif text == "ربات🤖💹":
#         await send_message_keyboard(session, chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
# """, keyboard_learn_ea)
#     elif text == "دریافت اموزش ربات📚":
#         await send_message_keyboard(session, chat_id, "برای مشاهده اموزش روی لینک زیر کلیک کنید\nhttps://aparat.com/v/mvatez2", keyboard_learn_ea)
#     elif text == "ادامه خرید ربات🛒":
#         k = allUser.check_user(chat_id)
#         try:
#             ser = services.get_service_bot(chat_id)[0]
#         except:
#             ser = "None"
#         if not k:
#             await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
#         elif ser != "None" and ser != "trial" and ser != None:
#             await send_message(session, chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
#         else:
#             await send_photo(session, chat_id, file_id_b, "LUXALPHA BOTS")
#             await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_b)
#             user_data[chat_id] = {"step":"plb"}
    
    elif text == "اندیکاتور لوکس الفا📊📈":
        await send_message_keyboard(session, chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
""", keyboard_learn_an)
    elif text == "دریافت اموزش اندیکاتور لوکس الفا📚":
        await send_message_keyboard(session, chat_id, "برای مشاهده اموزش روی لینک زیر کلیک کنید\nhttps://aparat.com/v/lzp1996", keyboard_learn_an)
    elif text == "ادامه خرید اندیکاتور لوکس الفا🛒":
        k = allUser.check_user(chat_id)
        try:
            ser = services.get_service(chat_id)[0]
        except:
            ser = "None"
        if not k:
            await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
        elif ser != "None" and ser != "trial" and ser != None:
            await send_message(session, chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
        else:
            user_data[chat_id] = {"step":"pl"}
            await send_photo(session, chat_id, file_id_d)
            await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan)
######################################################coin
    elif text == "اندیکاتور لوکس الفا الترا مخصوص طلا📊📈":
        await send_message_keyboard(session, chat_id, """📚 لطفاً قبل از هر خرید یا استفاده، حتماً آموزش‌ها را مشاهده کنید تا بتوانید بهترین نتیجه را بگیرید و بدون مشکل از خدمات استفاده کنید.
""", keyboard_learn_anu)
    elif text == "دریافت اموزش اندیکاتور لوکس الفا الترا مخصوص طلا📚":
        await send_message_keyboard(session, chat_id, "غیرفعال", keyboard_learn_anu)
    elif text == "ادامه خرید اندیکاتور لوکس الفا الترا مخصوص طلا🛒":
        k = allUser.check_user(chat_id)
        try:
            ser = services.get_service_u(chat_id)[0]
        except:
            ser = "None"
        if not k:
            await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
        elif ser != "None" and ser != "trial" and ser != None:
            await send_message(session, chat_id, "شما اشتراک فعال دارید.برای تمدید از دستور /تمدید استفاده کنید.")
        else:
            user_data[chat_id] = {"step":"plu"}
            await send_photo(session, chat_id, file_id_u)
            await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_au)
#####################################################coin

    elif chat_id in user_data and user_data[chat_id]["step"] == "GET_TID" and chat_type == 'User':
        user_data[chat_id]["tid"] = text
        user_data[chat_id]["tid2"] = "allTimeFull"
        services.set_ids(chat_id, user_data[chat_id]["tid"], user_data[chat_id]["tid2"])
        del user_data[chat_id]
        await send_message(session, chat_id, "دریافت شد.")
        plann = services.get_temp(chat_id)[0]
        ids = services.get_ids(chat_id)
        try:
            serv = services.get_service(chat_id)[0]
        except:
            serv = 'None'
        if serv == "None" or serv == [] or not serv or serv == "trial":
            await send_message(session, manager_ch, f"activate service for user:\n\ntrading view id => {ids[0]}\nplan={plann}\n{chat_id}")
            services.set_service(service=plann, chat_id=chat_id)
            services.set_date_buy(chat_id, plann)
        else:
            await send_message(session, manager_ch, f"renewal service for user:\n\ntrading view id => {ids[0]}\nplan={plann}\n{chat_id}")
            services.set_service(service=plann, chat_id=chat_id)
            services.set_date(chat_id, plann)

    elif chat_id in user_data and user_data[chat_id]["step"] == "GET_TIDU" and chat_type == 'User':
        user_data[chat_id]["tid"] = text
        user_data[chat_id]["tid2"] = "allTimeFull"
        services.set_ids_u(chat_id, user_data[chat_id]["tid"], user_data[chat_id]["tid2"])
        del user_data[chat_id]
        await send_message(session, chat_id, "دریافت شد.")
        plann = services.get_temp_u(chat_id)[0]
        ids = services.get_ids_u(chat_id)
        try:
            serv = services.get_service_u(chat_id)[0]
        except:
            serv = 'None'
        if serv == "None" or serv == [] or not serv or serv == "trial":
            await send_message(session, manager_ch, f"activate service ultra for user:\n\ntrading view id => {ids[0]}\nplan={plann}\n{chat_id}")
            services.set_service_u(service=plann, chat_id=chat_id)
            services.set_date_buy_u(chat_id, plann)
        else:
            await send_message(session, manager_ch, f"renewal service ultra for user:\n\ntrading view id => {ids[0]}\nplan={plann}\n{chat_id}")
            services.set_service_u(service=plann, chat_id=chat_id)
            services.set_date_u(chat_id, plann)

    # elif chat_id in user_data and user_data[chat_id]["step"] == "GET_TID2":
    #     if text == "/pass":
    #         text = "None"
    #     user_data[chat_id]["tid2"] = text
    #     services.set_ids(chat_id, user_data[chat_id]["tid"], user_data[chat_id]["tid2"])
    #     await send_photo(session, chat_id, file_id_d)
    #     await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan)
    #     user_data[chat_id]["step"] = "pl"

    
    elif text == "/تمدید" and chat_type == 'User':
        await send_message_keyboard(session, chat_id, "محصول خود را انتخاب کنید:", keyboard_service_re)

    elif text == "تمدید اندیکاتور لوکس الفا📊📈":
        try:
            ser = services.get_service(chat_id)
        except:
            ser = None
        k = allUser.check_user(chat_id)
        if not k:
            await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
        elif ser == "None" or ser == "trial" or ser == None or ser == []:
            await send_message(session, chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده")
        else:
            await send_photo(session, chat_id, file_id_d)
            await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan)
            user_data[chat_id] = {"step":"pl"}
#############################gold
    elif text == "تمدید اندیکاتور لوکس الفا الترا مخصوص طلا📊📈":
        try:
            ser = services.get_service_u(chat_id)
        except:
            ser = None
        k = allUser.check_user(chat_id)
        if not k:
            await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
        elif ser == "None" or ser == "trial" or ser == None or ser == []:
            await send_message(session, chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده")
        else:
            await send_photo(session, chat_id, file_id_u)
            await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_au)
            user_data[chat_id] = {"step":"plu"}
###########################gold

    # elif text =="تمدید ربات🤖💹":
    #     k = allUser.check_user(chat_id)
    #     try:
    #         ser = services.get_service_bot(chat_id)[0]
    #     except:
    #         ser = "None"
    #     if not k:
    #         await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    #     elif ser == "None" or ser == "trial" or ser == None or ser == []:
    #         await send_message(session, chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده کنید.")
    #     else:
    #         await send_photo(session, chat_id, file_id_b, "LUXALPHA BOTS")
    #         await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_b)
    #         user_data[chat_id] = {"step":"plb"}

    # elif text =="تمدید ربات پرو🤖💹":
    #     k = allUser.check_user(chat_id)
    #     try:
    #         ser = services.get_service_pro(chat_id)[0]
    #     except:
    #         ser = "None"
    #     if not k:
    #         await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
    #     elif ser == "None" or ser == "trial" or ser == None or ser == []:
    #         await send_message(session, chat_id, "شما اشتراک فعال ندارید.برای خرید از دستور /خرید استفاده کنید.")
    #     else:
    #         await send_photo(session, chat_id, file_id_p, "LUXALPHA PRO BOTS")
    #         await send_message_keyboard(session, chat_id, "لطفا پلن خود را انتخاب کنید", keyboard_plan_bp)
    #         user_data[chat_id] = {"step":"plbp"}

    elif text == "/خرید" and chat_type == 'User':
        k = allUser.check_user(chat_id)
        if not k:
            await send_message(session, chat_id, "قبل از خرید با ارسال عدد 10 اطلاعات خود را ثبت کنید")
        else:
            await send_message_keyboard(session, chat_id, "محصول خود را انتخاب کنید:", keyboard_service)

    elif chat_id in user_data and user_data[chat_id]["step"] == "GET_NAME" and chat_type == 'User':
        user_data[chat_id]["name"] = text
        user_data[chat_id]["step"] = "GET_FNAME"
        await send_message(session, chat_id, "نام خانوادگی خود را وارد کنید:")

    elif chat_id in user_data and user_data[chat_id]["step"] == "GET_FNAME" and chat_type == 'User':
        user_data[chat_id]["F-name"] = text
        user_data[chat_id]["step"] = "GET_PHONE"
        await send_message(session, chat_id, "شماره تلفن خود را وارد کنید")
    
    elif chat_id in user_data and user_data[chat_id]["step"] == "GET_PHONE" and chat_type == 'User':
        user_data[chat_id]["phone"] = text
        # c = await code(chat_id)
        user_data[chat_id]["c"] = 'EMPTY'
        user_data[chat_id]["code"] = 'EMPTY'
        summary = (f"✅ اطلاعات شما ثبت شد:\n"
               f"👤 نام: {user_data[chat_id]['name']} {user_data[chat_id]['F-name']}\n"
               f"📞 شماره: {user_data[chat_id]['phone']}\n"
        )
        summary2 = (f"✅ اطلاعات شما ویرایش شد:\n"
               f"👤 نام: {user_data[chat_id]['name']} {user_data[chat_id]['F-name']}\n"
               f"📞 شماره: {user_data[chat_id]['phone']}\n"
        )
        
        if user_data[chat_id]["command"] == "10" and chat_type == 'User':
            await send_message(session, chat_id, summary)
            await send_message_keyboard(session, chat_id, after_register, keyboard_service1)
            # await send_message(session, chat_id, "💎💎💎💎💎💎💎💎💎💎")
            # li = await create_license(chat_id, 1010)
            # lip = await create_license(chat_id, "pro")
            # await send_message(session, chat_id, "لایسنس سه روزه ربات لوکس الفا:")
            # await send_message(session, chat_id, li)
            # await send_file(session, chat_id, ex_id)
            # await send_message(session, chat_id, "http://87.107.105.244:8000")
            # await send_message(session, chat_id, "💎💎💎💎💎💎💎💎💎💎")
            # await send_message(session, chat_id, "لایسنس سه روزه ربات لوکس الفا پرو:")
            # await send_message(session, chat_id, lip)
            # await send_file(session, chat_id, ex_id_p)
            # await send_message(session, chat_id, "http://87.107.105.244:8080")
            # await send_message(session, chat_id, "💎💎💎💎💎💎💎💎💎💎")
            # await send_message(session, chat_id, "اگر چنانچه مشکلی در نصب و راه اندازی ربات داشتین با ایدی\n @luxalphafxx \n ارتباط بگیرید")
            # await send_message(session, chat_id, "پس از اتمام طرح سه روزه برای خرید اشتراک دستور\n /خرید را ارسال کنید")
            allUser.register_user(user_data[chat_id]["name"], user_data[chat_id]["F-name"], user_data[chat_id]["phone"], user_data[chat_id]["c"], chat_id, "tel", text, user_id)
            services.set_service(chat_id, "trial")
            services.set_service_u(chat_id, "trial")
            # services.set_service_bot(chat_id, "trial")
            # services.set_service_pro(chat_id, "trial")
            # services.register_licese(chat_id, li, 0)
            # services.register_licese_pro(chat_id, lip, 0)
            services.set_date_3(chat_id)
            services.set_date_3_u(chat_id)
            # services.set_date_3_bot(chat_id)
            # services.set_date_3_bot_pro(chat_id)
            # services.set_account_id(chat_id, "allTimeFull")
            # services.set_account_id_pro(chat_id, "allTimeFull")

        elif user_data[chat_id]["command"] == "edit" and chat_type == 'User':
            allUser.update_info(user_data[chat_id]['name'], user_data[chat_id]['F-name'], user_data[chat_id]['phone'], chat_id)
            await send_message(session, chat_id, summary2)
        
        del user_data[chat_id]
    
    elif chat_id in user_data and user_data[chat_id]["step"] == "support" and chat_type == 'User':
        message_id = message["message_id"]
        if text == "/exit":
            await remove_keyboard(session, chat_id, "اتصال شما قطع شد.")
            del user_data[chat_id]
        else:
            if "file" in message:
                await forward_photo(
                    session=session,
                    fro=chat_id,
                    id=message_id,
                    to=support_group_id
                )
                await send_message(session, support_group_id, f"{chat_id}")
            else:
                await send_message(session, support_group_id, f"{text}\n\n{chat_id}")
            await send_message(session, chat_id, "پیام به کارشناس مربوطه ارسال شد.در اسرع وقت به درخواست شما رسیدگی میشود.در صورت تمایل برای ادامه گف و گو پیام خود را ارسال کنید .درغیر این صورت دستور /exit را ارسال کنید.")

    elif chat_id == support_group_id:
        if "reply_to_message_id" in message:
            reply_to = message["reply_to_message_id"]
            message_id = message["message_id"]
            admin_answer = "\n".join(text.split("\n")[:-1])
            target_id = text.split("\n")[-1]
            final_msg = f"🎧 پاسخ پشتیبانی:\n\n{admin_answer}"
            if "file" in message:
                await send_message(session, target_id, "پاسخ جدید در پشتیبانی🎧:")
                await forward_photo(
                    session=session,
                    fro=support_group_id,
                    id=message_id,
                    to=target_id
                )
            else:
                await send_message(session, target_id, final_msg)
            await edit_text(session, msg_id=reply_to, text=f"پاسخ داده شده")

    # elif chat_id in user_data and user_data[chat_id]["step"] == "plbp":
    #     if text not in ["بات پرو یک ماهه", "بات پرو سه ماهه", "بات پرو شش ماهه"]:
    #         await send_message_keyboard(session, chat_id, "لطفا یکی از گزینه هارا انتخاب کنید", keyboard_plan_bp)
    #         user_data[chat_id] = {"step":"plbp"}
        # else:
        #     user_data[chat_id] = {"step":"BUY", "command":"pro"}
        #     services.update_temp_service_pro(text, chat_id)
        #     await send_message(session, chat_id, f"پلن {text} انتخاب شد.")
        #     await send_message_keyboard(session, chat_id, "شبکه مورد نظر را انتخاب کنید", keyboard_wallet)

    # elif chat_id in user_data and user_data[chat_id]["step"] == "plb":
    #     if text not in ["بات یک ماهه", "بات سه ماهه", "بات شش ماهه"]:
    #         await send_message_keyboard(session, chat_id, "لطفا یکی از گزینه هارا انتخاب کنید", keyboard_plan_b)
    #         user_data[chat_id] = {"step":"plb"}
    #     else:
    #         user_data[chat_id] = {"step":"BUY", "command":"bot"}
    #         services.update_temp_service_bot(text, chat_id)
    #         await send_message(session, chat_id, f"پلن {text} انتخاب شد.")
    #         await send_message_keyboard(session, chat_id, "شبکه مورد نظر را انتخاب کنید", keyboard_wallet)

    elif chat_id in user_data and user_data[chat_id]["step"] == "plu":
        if text not in ["یک ماهه الترا", "سه ماهه الترا", "شش ماهه الترا"]:
            await send_message_keyboard(session, chat_id, "لطفا یکی از گزینه هارا انتخاب کنید", keyboard_plan_au)
            user_data[chat_id] = {"step":"plu"}
        else:
            user_data[chat_id] = {"step":"BUY", "command":"andu"}
            services.update_temp_service_u(text, chat_id)
            await send_message(session, chat_id, f"پلن {text} انتخاب شد.")
            res = await send_message_keyboard(session, chat_id, "نحوه پرداخت را انتخاب کنید", keyboard_pay)

    elif chat_id in user_data and user_data[chat_id]["step"] == "pl":
        if text not in ["یک ماهه", "سه ماهه", "شش ماهه"]:
            await send_message_keyboard(session, chat_id, "لطفا یکی از گزینه هارا انتخاب کنید", keyboard_plan)
            user_data[chat_id] = {"step":"pl"}
        else:
            user_data[chat_id] = {"step":"BUY", "command":"and"}
            services.update_temp_service(text, chat_id)
            await send_message(session, chat_id, f"پلن {text} انتخاب شد.")
            res = await send_message_keyboard(session, chat_id, "نحوه پرداخت را انتخاب کنید", keyboard_pay)
    
    elif text == "ارز دیجیتال":
        await send_message_keyboard(session, chat_id, "شبکه مورد نظر را انتخاب کنید:", keyboard_wallet)

    elif text == "ریالی":
        t = tether()
        price = t.get_price()
        if not price:
            await send_message(session, chat_id, "مشکلی در دریافت قیمت پیش امد.لطفا بعدا تلاش کنید.")
        else:
            if user_data[chat_id]['command'] == 'andu':
                s = services.get_temp_u(chat_id)[0]
                if s == 'یک ماهه الترا':
                    c = 38
                elif s == 'سه ماهه الترا':
                    c = 99
                else:
                    c = 149
            else:
                s = services.get_temp(chat_id)[0]
                if s == 'یک ماهه':
                    c = 28
                elif s == 'سه ماهه':
                    c = 79
                else:
                    c = 139

            price2 = price*c
            finall_price = math.floor(price2/100000)*100000
            await send_photo(session, chat_id, card)
            await send_message(
                session,
                chat_id, 
                f"💵 *تومان نهایی:* `{finall_price:,}`\n"
                f"🟢 *مبنا:* `{price:,}`\n"
                f"────────────────\n"
                f"🕒 *اعتبار تراکنش:* ۱ ساعت\n"
            )
            await send_message(session, chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")

    elif text == "trc20":
        await remove_keyboard(session, chat_id, "TK6ybs7iALN7n5GqE5kagu7JBRfFUQkcT8")
        await send_message(session, chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")
    
    elif text == "bep20":
        await remove_keyboard(session, chat_id, "0x5d6b8c8c1577f2b71b9cca4492a2cbec57fd51a9")
        await send_message(session, chat_id, "بعد از انجام واریز، فقط کافیست اسکرین‌شاتِ موفقیت‌آمیز بودنِ تراکنش را برای ما بفرستید.همکارانِ من در بخشِ فنی بلافاصله واریزی شما را بررسی و دسترسی‌تان را فعال می‌کنند.\nبرای ارسال عکس از دستور /عکس استفاده کنید.")
    
    elif text == "/عکس" and chat_type == 'User':
        user_data[chat_id]['step'] = "get_photo"
        await send_message(session, chat_id, "عکس واریزی خود را ارسال.\nدر صورت انصراف دستور /exit را وارد کنید.")

    elif chat_id in user_data and user_data[chat_id]["step"] == "get_photo":
        message_id = message["message_id"]
        if user_data[chat_id]["command"] and user_data[chat_id]["command"] == "and":
            p = services.get_temp(chat_id)
        elif user_data[chat_id]["command"] == "andu":
            p = services.get_temp_u(chat_id)
        else:
            p = services.get_temp_bot(chat_id)
        if "file" in message:
            file_id = message["file"]["file_id"]

            await forward_photo(
                session=session,
                fro=chat_id,
                id=message_id,
                to=photo_group_id
            )
            
            full_caption = f"📸\nplan:{p[0]}\n{chat_id}"
            await send_message(session, photo_group_id, full_caption)
            await send_message(session, chat_id, "✅ تصویر شما با موفقیت به مجموعه کارشناسان LUXalpha ارسال شد و پس از تایید دسترسی شما فعال میشود ")
            del user_data[chat_id]

        else:
            if message['text'] == '/exit':
                await send_message(session, chat_id, "خارج شدید.")
                del user_data[chat_id]
            else:
                await send_message(session, chat_id, "لطفا فقط عکس ارسال کنید")
        
    elif chat_id == photo_group_id:
        if "reply_to_message_id" in message:
            msg_id = message["reply_to_message_id"]
            action, target_chat_id = text.split("_")
            if action == "accept":
                plan = services.get_temp(target_chat_id)[0]
                try:
                    c = allUser.get_invited(target_chat_id)
                    user_data[target_chat_id] = {"step":"GET_TID"}
                    if c != "None":
                        allUser.add_person(c[0])
                    # ids = services.get_ids_u(target_chat_id)
                    # if serv == "trial" or serv == "None" or not serv:
                    #     res = await send_message(session, "b0Jq2Is0ofz020e4b2ed85d224dda671", f"activate service for user:\n\ntrading view id 1 => {ids[0]}\ntrading view id 2 => {ids[1]}\nplan:{plan}")
                    #     services.set_date_buy_u(target_chat_id, plan)
                    # else:
                    #     res = await send_message(session, "b0Jq2Is0ofz020e4b2ed85d224dda671", f"renewal service for user:\n\ntrading view id 1 => {ids[0]}\ntrading view id 2 => {ids[1]}\nplan:{plan}")
                    #     services.set_date_u(target_chat_id, plan)
                    services.set_expiration_notified3(target_chat_id)
                    await send_message(session, target_chat_id, """
        فعال‌سازیِ دسترسی شما ✅

«واریزیِ شما توسطِ تیم فنی تأیید شد. به تیمِ حرفه‌ای LUXalpha خوش آمدید! 💎
لطفا جهت دریافت اندیکاتور ایدی تریدیگ ویو خودتونو کامل باری ما ارسال کنین تا بتونیم لایسنس شمارو متصل کنیم.
        """)
                    await send_file(session, target_chat_id, after_buy_pdf)
                    await edit_text2(session, msg_id=msg_id, text=f"تایید شد")
            
                except Exception as e:
                    print(e)

            if action == "acceptu":
                plan = services.get_temp_u(target_chat_id)[0]
                try:
                    c = allUser.get_invited(target_chat_id)
                    user_data[target_chat_id] = {"step":"GET_TIDU"}
                    if c != "None":
                        allUser.add_person(c[0])
                    # ids = services.get_ids_u(target_chat_id)
                    # if serv == "trial" or serv == "None" or not serv:
                    #     res = await send_message(session, "b0Jq2Is0ofz020e4b2ed85d224dda671", f"activate service for user:\n\ntrading view id 1 => {ids[0]}\ntrading view id 2 => {ids[1]}\nplan:{plan}")
                    #     services.set_date_buy_u(target_chat_id, plan)
                    # else:
                    #     res = await send_message(session, "b0Jq2Is0ofz020e4b2ed85d224dda671", f"renewal service for user:\n\ntrading view id 1 => {ids[0]}\ntrading view id 2 => {ids[1]}\nplan:{plan}")
                    #     services.set_date_u(target_chat_id, plan)
                    services.set_expiration_notified3(target_chat_id)
                    await send_message(session, target_chat_id, """
        فعال‌سازیِ دسترسی شما ✅

«واریزیِ شما توسطِ تیم فنی تأیید شد. به تیمِ حرفه‌ای LUXalpha خوش آمدید! 💎
لطفا جهت دریافت اندیکاتور ایدی تریدیگ ویو خودتونو کامل برای ما ارسال کنین تا بتونیم لایسنس شمارو متصل کنیم.
        """)
                    await send_file(session, target_chat_id, after_buy_pdf)
                    await edit_text2(session, msg_id=msg_id, text=f"تایید شد")
            
                except:
                    pass

            elif action == "reject":
                await edit_text2(session, msg_id, "رد شده")
                await send_message(session, target_chat_id, """واریز شما توسط کارشناس مربوطه رد شد.""")


#             elif action == "acceptbot":
#                 try:
#                     serv = services.get_service_bot(target_chat_id)[0]
#                 except:
#                     serv = None
#                 try:
#                     coun = services.get_counter(target_chat_id)[0]
#                 except:
#                     coun = 100
#                 li = await create_license(target_chat_id, coun)
#                 services.increase_counter(target_chat_id)
#                 plan = services.get_temp_bot(target_chat_id)[0]
#                 try:
#                     await edit_text2(session, msg_id=msg_id, text=f"تایید شد")
#                     c = allUser.get_invited(target_chat_id)
#                     if c != "None":
#                         allUser.add_person(c[0])
#                     if serv == "trial" or serv == "None" or not serv:
#                         services.del_license(target_chat_id)
#                         services.register_licese(target_chat_id, li, 99)
#                         services.set_date_buy_bot(target_chat_id, plan)
#                     else:
#                         services.update_license(target_chat_id, li)
#                         services.set_date_bot(target_chat_id, plan)
#                     services.set_service_bot(service=plan, chat_id=target_chat_id)
#                     services.set_account_id(target_chat_id, "allTimeFull")
#                     await send_message_keyboard(session, target_chat_id, """
# تبریک می‌گوییم! شما اکنون به تکنولوژی LUXalpha مجهز شدید. 🚀

# دوست عزیز، ورود شما را به جمع معامله‌گران هوشمند لوکس‌آلفا تبریک می‌گوییم. فایل ربات و لایسنس اختصاصی شما آماده است. لطفاً پیش از هر اقدامی، این چند نکته حیاتی را با دقت مطالعه کنید:

# 1️⃣ مشاهده ویدئوی آموزشی (الزامی):

# ابتدا ویدئوی آموزشی که در [لینک یا پیوست] برای شما قرار داده شده را تا انتها ببینید. تنظیمات دقیق، نحوه اتصال به متاتریدر و مدیریت ریسک در این ویدئو گام‌به‌گام توضیح داده شده است. عدم رعایت این تنظیمات می‌تواند منجر به عملکرد نادرست ربات شود.

# 2️⃣ محدودیت تعداد سیستم (License Limit):

# لایسنس شما به صورت اختصاصی صادر شده و تنها روی ۲ سیستم (یا ۲ شماره حساب متاتریدر) قابل اجراست. پیشنهاد ما استفاده از یک سیستم شخصی و یک VPS (سرور مجازی) است تا ربات ۲۴ ساعته فعال بماند.

# 3️⃣ هشدار مهم - عدم امکان ریست لایسنس:

# توجه داشته باشید که لایسنس‌های صادر شده تحت هیچ شرایطی امکان ریست یا انتقال به سیستم جدید را ندارند. بنابراین در انتخاب سیستم‌هایی که می‌خواهید ربات را روی آن‌ها فعال کنید، نهایت دقت را داشته باشید و از لایسنس خود مانند دارایی ارزشمندتان مراقبت کنید.

# ✅ پشتیبانی:

# اگر در حین نصب یا بر اساس ویدئوی آموزشی به سوالی برخوردید، تیم پشتیبانی ما در کنار شماست.

# با LUXalpha، هوشمندانه و با انضباط معامله کنید.
# """, keyboard_help)
                    
#                     await send_message(session, target_chat_id, "لایسنس شما:")
#                     await send_message(session, target_chat_id, li)
#                     await send_file(session, target_chat_id, ex_id)
#                     await send_message(session, target_chat_id, "http://87.107.105.244:8000")
#                     await send_message(session, target_chat_id, """اگر چنانچه مشکلی در نصب و راه اندازی ربات داشتین با ایدی \n @luxalpha \n ارتباط بگیرید""")
#                 except Exception as e:
#                     print(e)

#             elif action == "acceptpro":
#                 try:
#                     serv = services.get_service_pro(target_chat_id)[0]
#                 except:
#                     serv = None
#                 try:
#                     coun = services.get_counter_pro(target_chat_id)[0]
#                 except:
#                     coun = 100
#                 li = await create_license(target_chat_id, coun)
#                 services.increase_counter_pro(target_chat_id)
#                 plan = services.get_temp_pro(target_chat_id)[0]
#                 try:
#                     await edit_text2(session, msg_id=msg_id, text=f"تایید شد")
#                     c = allUser.get_invited(target_chat_id)
#                     if c != "None":
#                         allUser.add_person(c[0])
#                     if serv == "trial" or serv == "None" or not serv:
#                         services.del_license_pro(target_chat_id)
#                         services.register_licese_pro(target_chat_id, li, 99)
#                         services.set_date_buy_bot_pro(target_chat_id, plan)
#                     else:
#                         services.update_license_pro(target_chat_id, li)
#                         services.set_date_bot_pro(target_chat_id, plan)
#                     services.set_service_pro(service=plan, chat_id=target_chat_id)
#                     services.set_account_id_pro(target_chat_id, "allTimeFull")
#                     await send_message_keyboard(session, target_chat_id, """
# تبریک می‌گوییم! شما اکنون به تکنولوژی LUXalpha مجهز شدید. 🚀

# دوست عزیز، ورود شما را به جمع معامله‌گران هوشمند لوکس‌آلفا تبریک می‌گوییم. فایل ربات و لایسنس اختصاصی شما آماده است. لطفاً پیش از هر اقدامی، این چند نکته حیاتی را با دقت مطالعه کنید:

# 1️⃣ مشاهده ویدئوی آموزشی (الزامی):

# ابتدا ویدئوی آموزشی که در [لینک یا پیوست] برای شما قرار داده شده را تا انتها ببینید. تنظیمات دقیق، نحوه اتصال به متاتریدر و مدیریت ریسک در این ویدئو گام‌به‌گام توضیح داده شده است. عدم رعایت این تنظیمات می‌تواند منجر به عملکرد نادرست ربات شود.

# 2️⃣ محدودیت تعداد سیستم (License Limit):

# لایسنس شما به صورت اختصاصی صادر شده و تنها روی 1 سیستم قابل اجراست. پیشنهاد ما استفاده از یک سیستم شخصی و یک VPS (سرور مجازی) است تا ربات ۲۴ ساعته فعال بماند.

# 3️⃣ هشدار مهم - عدم امکان ریست لایسنس:

# توجه داشته باشید که لایسنس‌های صادر شده تحت هیچ شرایطی امکان ریست یا انتقال به سیستم جدید را ندارند. بنابراین در انتخاب سیستم‌هایی که می‌خواهید ربات را روی آن‌ها فعال کنید، نهایت دقت را داشته باشید و از لایسنس خود مانند دارایی ارزشمندتان مراقبت کنید.

# ✅ پشتیبانی:

# اگر در حین نصب یا بر اساس ویدئوی آموزشی به سوالی برخوردید، تیم پشتیبانی ما در کنار شماست.

# با LUXalpha، هوشمندانه و با انضباط معامله کنید.
# """, keyboard_help)
                    
#                     await send_message(session, target_chat_id, "لایسنس شما:")
#                     await send_message(session, target_chat_id, li)
#                     await send_file(session, target_chat_id, ex_id_p)
#                     await send_message(session, target_chat_id, "http://87.107.105.244:8080")
#                     await send_message(session, target_chat_id, """اگر چنانچه مشکلی در نصب و راه اندازی ربات داشتین با ایدی \n @luxalpha \n ارتباط بگیرید""")
#                 except Exception as e:
#                     print(e)
        

    elif text == "/help" and chat_type == 'User':
        await send_message(session, chat_id, """
                           

🔹 خرید اشتراک ▫️▫️▫️▫️▫️ /خرید
🔹 مشاهده پروفایل ▫️▫️▫️ /پروفایل
🔸 ویرایش پروفایل ▫️▫️▫️ /ویرایش
🔹 سوالات متداول ▫️▫️▫️ /سوالات متداول
🔹 ارسال عکس واریزی ▫️▫️ /عکس
🔸 پشتیبانی ▫️▫️▫️▫️▫️ /پشتیبانی
🔸 ثبت اطلاعات ▫️▫️▫️▫️▫️10
➖➖➖➖➖➖➖➖➖➖
🔑 ورود به پنل ادمین ▫️▫️ /ادمین
🔑 ورود به پنل مدیریت ▫️ /مدیر
                           
            
                           """)
        
    elif text == "/پروفایل" and chat_type == 'User':
        info = allUser.get_info(chat_id)
        try:
            id1u, id2u = services.get_ids(chat_id)
        except:
            id1u, id2u = ['ندارد', 'ندارد']
        try:
            date3 = services.get_date_3(chat_id)[0]
        except:
            date3 = ''
        try:
            date_and = services.get_date(chat_id)[0]
        except Exception as e:
            print(f"a:{e}")
            date_and = ''

        try:
            id1, id2 = services.get_ids_u(chat_id)
        except:
            id1, id2 = ['ندارد', 'ندارد']
        try:
            date_andu = services.get_date_u(chat_id)[0]
        except Exception as e:
            print(f"a:{e}")
            date_andu = ''
        # try:
        #     date_bot = services.get_date_bot(chat_id)[0]
        # except Exception as e:
        #     print(f"b:{e}")
        #     date_bot = ''
        
        # try:
        #     date_pro = services.get_date_pro(chat_id)[0]
        # except:
        #     date_pro = ''

        try:
            service = services.get_service(chat_id)[0]
        except:
            service = 'None'

        try:
            serviceu = services.get_service_u(chat_id)[0]
        except:
            serviceu = 'None'

        if not info:
            await send_message(session, chat_id, "اطلاعات شما ثبت نشده.")
        else:
            if service != 'trial' and serviceu != 'trial':
                profile_text = (
                    f"👤 نام: {info[0]} {info[1]}\n"
                    f"📞 شماره: {info[2]}\n\n"
                    # f"🎫 کد معرف: {info[3]}\n"
                    # f"👍کاربران دعوت کرده: {info[7]}\n\n"
                    f"💹اشتراک: {service}\n"
                    f"🆔 تریدینگ‌ویو: {id1}\n"
                    f"📅 تاریخ انقضا: {date_and}\n\n"
                    f"💹اشتراک الترا: {serviceu}\n"
                    f"🆔 تریدینگ‌ویو: {id1u}\n"
                    f"📅 تاریخ انقضا: {date_andu}"
                    # f"🤖 لایسنس ربات: {service_bot}\n"
                    # f"📅 تاریخ انقضا ربات: {date_bot}\n\n"
                    # f"🤖 لایسنس ربات پرو: {service_pro}\n"
                    # f"📅 تاریخ انقضا ربات پرو: {date_pro}"
                )
                await send_message(session, chat_id, profile_text)
            elif service == "trial" and serviceu != "trial":
                profile_text = (
                    f"👤 نام: {info[0]} {info[1]}\n"
                    f"📞 شماره: {info[2]}\n\n"
                    # f"🎫 کد معرف: {info[3]}\n"
                    # f"👍کاربران دعوت کرده: {info[7]}\n\n"
                    f"💹اشتراک: {service}\n"
                    f"🆔 تریدینگ‌ویو: {id1}\n"
                    f"📅 تاریخ انقضا: {date3}\n\n"
                    f"💹اشتراک الترا: {serviceu}\n"
                    f"🆔 تریدینگ‌ویو: {id1u}\n"
                    f"📅 تاریخ انقضا: {date_andu}"
                    # f"🤖 لایسنس ربات: {service_bot}\n"
                    # f"📅 تاریخ انقضا ربات: {date_bot}\n\n"
                    # f"🤖 لایسنس ربات پرو: {service_pro}\n"
                    # f"📅 تاریخ انقضا ربات پرو: {date_pro}"
                )
                await send_message(session, chat_id, profile_text)
            elif service != "trial" and serviceu == "trial":
                profile_text = (
                    f"👤 نام: {info[0]} {info[1]}\n"
                    f"📞 شماره: {info[2]}\n\n"
                    # f"🎫 کد معرف: {info[3]}\n"
                    # f"👍کاربران دعوت کرده: {info[7]}\n\n"
                    f"💹اشتراک: {service}\n"
                    f"🆔 تریدینگ‌ویو: {id1}\n"
                    f"📅 تاریخ انقضا: {date_and}\n\n"
                    f"💹اشتراک الترا: {serviceu}\n"
                    f"🆔 تریدینگ‌ویو: {id1u}\n"
                    f"📅 تاریخ انقضا: {date3}"
                    # f"🤖 لایسنس ربات: {service_bot}\n"
                    # f"📅 تاریخ انقضا ربات: {date_bot}\n\n"
                    # f"🤖 لایسنس ربات پرو: {service_pro}\n"
                    # f"📅 تاریخ انقضا ربات پرو: {date_pro}"
                )
                await send_message(session, chat_id, profile_text)
            elif service == "trial" and serviceu == "trial":
                profile_text = (
                    f"👤 نام: {info[0]} {info[1]}\n"
                    f"📞 شماره: {info[2]}\n\n"
                    # f"🎫 کد معرف: {info[3]}\n"
                    # f"👍کاربران دعوت کرده: {info[7]}\n\n"
                    f"💹اشتراک: {service}\n"
                    f"🆔 تریدینگ‌ویو: {id1}\n"
                    f"📅 تاریخ انقضا: {date3}\n\n"
                    f"💹اشتراک الترا: {serviceu}\n"
                    f"🆔 تریدینگ‌ویو: {id1u}\n"
                    f"📅 تاریخ انقضا: {date3}"
                    # f"🤖 لایسنس ربات: {service_bot}\n"
                    # f"📅 تاریخ انقضا ربات: {date_bot}\n\n"
                    # f"🤖 لایسنس ربات پرو: {service_pro}\n"
                    # f"📅 تاریخ انقضا ربات پرو: {date_pro}"
                )
                await send_message(session, chat_id, profile_text)
    
    elif text == "/ویرایش" and chat_type == 'User':
        exist = allUser.check_user(chat_id)
        if not exist:
            await send_message(session, chat_id, "اطلاعات شما ثبت نشده.")
        else:
            await send_message(session, chat_id, "نام خود را وارد کنید:")
            user_data[chat_id] = {"step":"GET_NAME", "command":"edit"}
    
    elif text == "/سوالات متداول" and chat_type == 'User':
        await send_message(session, chat_id, questions)

    elif text == "/پشتیبانی":
        await send_message_keyboard(session, chat_id, """
به پشتیبانی مجموعه LUXalpha خوش امدید.
برای دریافت اطلاعات تماس گزینه 1
برای اتصال مستقیم به پشتیبان گزینه 2
را انتخاب کنید
""", keyboard_support)
    
    elif text == "گزینه 1":
        await send_message(session, chat_id, "موقتا غیر فعال\nساعت پاسخگویی 12 الی 20")
        await remove_keyboard(session, chat_id, "از بخش پشتیبانی خارج شدید.")
    elif text == "گزینه 2":
        await send_message(session, chat_id, "🔵متصل هستید")
        await send_message(session, chat_id, ".برای خروج از بخش پشتیبانی دستور /exit را وارد کنید\nسوال خود را بپرسید:")
        user_data[chat_id] = {"step":"support"}

    elif text == "/ادمین" and chat_type == 'User':
        res = generall.get_admins()
        ress=[r[0] for r in res]
        if user_id not in ress:
            await send_message(session, chat_id, "شما به این بخش دسترسی ندارید.")
        else:
            await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل ادمین دستور /exit را وارد کنید.", keyboard_admin)
            user_data[chat_id] = {"step":"SELECT_OPERATION"}
    
    elif chat_id in user_data and user_data[chat_id]["step"] == "SELECT_OPERATION" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل ادمین خارج شدید", keyboard_help)
            del user_data[chat_id]
        elif text == "ارسال پیام گروهی":
            await send_message_keyboard(session, chat_id, "فیلتر کاربران را انتخاب کنید", keyboard_filter)
            user_data[chat_id]["step"] = "FILTER"
        else:
            await send_message_keyboard(session, chat_id, "پیام یافت نشد.عملیات را به درستی انتخاب کنید", keyboard_admin)
    elif chat_id in user_data and user_data[chat_id]["step"] == "FILTER" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل ادمین خارج شدید", keyboard_help)
            del user_data[chat_id]
        elif text in ["کاربران تستی", "کاربران فعال", "کاربران یک ماهه", "کاربران سه ماهه", "کاربران شش ماهه", "کاربران بدون اشتراک", "کاربران یک ماهه الترا", "کاربران سه ماهه الترا", "کاربران شش ماهه الترا"]:
            if text == 'کاربران تستی':
                ids = services.get_trial_user_ids()
                ids2 = services.get_trial_user_ids_u()
                # ids2 = services.get_trial_user_ids_bot()
                # ids3 = services.get_trial_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
                finall_ids = [x for x in ids if x in ids2]
            elif text == "کاربران فعال":
                ids = services.get_active_user_ids()
                ids2 = services.get_active_user_ids_u()
                # ids2 = services.get_active_user_ids_bot()
                # ids3 = services.get_active_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
                finall_ids = ids+ids2
                finall_ids = set(finall_ids)
            elif text == 'کاربران بدون اشتراک':
                ids = services.get_deactive_user_ids()
                ids2 = services.get_deactive_user_ids_u()
                # ids2 = services.get_deactive_user_ids_bot()
                # ids3 = services.get_deactive_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
                finall_ids = [x for x in ids if x in ids2]
            elif text == "کاربران یک ماهه":
                finall_ids = services.get_basic_user_ids()
                # ids2 = services.get_basic_user_ids_bot()
                # ids3 = services.get_basic_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            elif text == "کاربران سه ماهه":
                finall_ids = services.get_pro_user_ids()
                # ids2 = services.get_pro_user_ids_bot()
                # ids3 = services.get_pro_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            elif text == "کاربران شش ماهه":
                finall_ids = services.get_elite_user_ids()
                # ids2 = services.get_elite_user_ids_bot()
                # ids3 = services.get_elite_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            elif text == "کاربران یک ماهه الترا":
                finall_ids = services.get_basic_user_ids_u()
                # ids2 = services.get_basic_user_ids_bot()
                # ids3 = services.get_basic_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            elif text == "کاربران سه ماهه الترا":
                finall_ids = services.get_pro_user_ids_u()
                # ids2 = services.get_pro_user_ids_bot()
                # ids3 = services.get_pro_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            elif text == "کاربران شش ماهه الترا":
                finall_ids = services.get_elite_user_ids_u()
                # ids2 = services.get_elite_user_ids_bot()
                # ids3 = services.get_elite_user_ids_pro()
                # ids.extend(ids2)
                # ids.extend(ids3)
            await send_message(session, chat_id, "پیام خود را بنویسید")
            user_data[chat_id]["step"] = "SEND_MESSAGE"
            user_data[chat_id]["ids"] = finall_ids
        else:
            await send_message_keyboard(session, chat_id, "پیام یافت نشد.فیلتر کاربران را به درستی انتخاب کنید", keyboard_filter)
    
    elif chat_id in user_data and user_data[chat_id]["step"] == "SEND_MESSAGE" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل ادمین خارج شدید", keyboard_help)
            del user_data[chat_id]
        else:
            ids = user_data[chat_id]["ids"]
            await send_message(session, chat_id, "⏳ ارسال پیام گروهی در پس‌زمینه شروع شد")
            if ids:
                asyncio.create_task(broadcast_message(session, ids, text))
            await send_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل ادمین دستور /exit را وارد کنید.", keyboard_admin)
            user_data[chat_id] = {"step":"SELECT_OPERATION"}

    elif text == "/مدیر" and chat_type == 'User':
        if user_id not in manager_users:
            await send_message(session, chat_id, "شما به این بخش دسترسی ندارید.")
        else:
            res = await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}
    elif chat_id in user_data and user_data[chat_id]["step"] == "choose_operation" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل مدیر خارج شدید", keyboard_help)
            del user_data[chat_id]
        elif text == "امار کاربران":
            await send_message(session, chat_id, "در این بخش، نمای کاملی از جمعیت کاربری پلتفرم ارائه شده است. این آمار به شما کمک می‌کند تا روند جذب و رضایت مشتریان را به صورت دقیق پایش نمایید")
            amar = services.get_user_status()
            if 'None' not in amar:
                amar['None'] = 0
            if 'trial' not in amar:
                amar['trial'] = 0
            if 'یک ماهه' not in amar:
                amar['یک ماهه'] = 0
            if 'سه ماهه' not in amar:
                amar["سه ماهه"] = 0
            if 'شش ماهه' not in amar:
                amar["شش ماهه"] = 0
            await send_message(session, chat_id, "اندیکاتور")
            await send_message(session, chat_id, f"""📊 خلاصه وضعیت کلی:
- کل کاربران ثبت‌نامی: {amar['trial']+amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']+amar['None']} نفر
- کاربران فعال (اشتراک‌دار): {amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']} نفر""")
            await send_message(session, chat_id, f"""
- نرخ تبدیل تستی به پولی: {(amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه'])/(amar['trial']+amar['یک ماهه']+amar['سه ماهه']+amar['شش ماهه']+amar['None'])*100}

👥 جزئیات تفکیکی کاربران:
1.  کاربران بدون اشتراک : {amar['None']} نفر
1.  کاربران تستی: {amar['trial']} نفر (دوره آشنایی رایگان)
2.  اشتراک ماهانه: {amar['یک ماهه']} نفر
3.  اشتراک سه‌ماهه: {amar['سه ماهه']} نفر
4.  اشتراک شش‌ماهه: {amar['شش ماهه']} نفر
""")

            amar2 = services.get_user_status_u()
            if 'None' not in amar2:
                amar2['None'] = 0
            if 'trial' not in amar2:
                amar2['trial'] = 0
            if 'یک ماهه' not in amar:
                amar2['یک ماهه الترا'] = 0
            if 'سه ماهه' not in amar2:
                amar2["سه ماهه الترا"] = 0
            if 'شش ماهه' not in amar2:
                amar2["شش ماهه الترا"] = 0
            await send_message(session, chat_id, "اندیکاتور الترا")
            await send_message(session, chat_id, f"""📊 خلاصه وضعیت کلی:
- کل کاربران ثبت‌نامی: {amar2['trial']+amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']+amar2['None']} نفر
- کاربران فعال (اشتراک‌دار): {amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']} نفر""")
            await send_message(session, chat_id, f"""
- نرخ تبدیل تستی به پولی: {(amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا'])/(amar2['trial']+amar2['یک ماهه الترا']+amar2['سه ماهه الترا']+amar2['شش ماهه الترا']+amar2['None'])*100}

👥 جزئیات تفکیکی کاربران:
1.  کاربران بدون اشتراک : {amar2['None']} نفر
1.  کاربران تستی: {amar2['trial']} نفر (دوره آشنایی رایگان)
2.  اشتراک ماهانه: {amar2['یک ماهه الترا']} نفر
3.  اشتراک سه‌ماهه: {amar2['سه ماهه الترا']} نفر
4.  اشتراک شش‌ماهه: {amar2['شش ماهه الترا']} نفر
""")

            await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}


        elif text == "افزودن ادمین":
            await send_message(session, chat_id, "برای افزودن ادمین ایدی عددی کاربر را وارد کنید:")
            user_data[chat_id]["step"] = "add_admin"
        elif text == "حذف ادمین":
            await send_message(session, chat_id, "برای حذف ادمین ایدی عددی کاربر را وارد کنید")
            user_data[chat_id]["step"] = "remove_admin"
        elif text == "دریافت چت ایدی":
            await send_message(session, chat_id, "برای دریافت چت ایدی یک پیام دلخواه ارسال کنید\nبرای دریافت چت ایدی یک کاربر دیگر کافیست یک پیام از ان شخص برای من ارسال کنید")
            user_data[chat_id]["step"] = "chat_id"
        elif text == "خروجی کاربران":
            users = allUser.export_users()
            txt = ""
            for first_name, last_name, phone in users:
                users_info = (
                    f"نام: {first_name}\n"
                    f"نام خانوادگی: {last_name}\n"
                    f"شماره: {phone}\n"
                    "============================\n")
                if len(txt) + len(users_info) > 3000:
                    await send_message(session, chat_id, txt)
                    txt = ""
                txt += users_info
            if txt:
                await send_message(session, chat_id, txt)
            await send_message(session, chat_id, "برای خروج از بخش مدیریت دستور /exit را وارد کنید.")
            user_data[chat_id] = {"step":"choose_operation"}
        elif text == "خروجی کاربران جدید":
            users = allUser.export_new_users()
            if not users:
                await send_message(session, chat_id, "کاربر جدیدی وجود ندارد.")
            else:
                txt = ""
                for first_name, last_name, phone in users:
                    users_info = (
                        f"نام: {first_name}\n"
                        f"نام خانوادگی: {last_name}\n"
                        f"شماره: {phone}\n"
                        "============================\n")
                    if len(txt) + len(users_info) > 3000:
                        await send_message(session, chat_id, txt)
                        txt = ""
                    txt += users_info
                if txt:
                    await send_message(session, chat_id, txt)
            allUser.set_new_member()
            await send_message(session, chat_id, "برای خروج از بخش مدیریت دستور /exit را وارد کنید.")
            user_data[chat_id] = {"step":"choose_operation"}
        else:
            await send_message(session, chat_id, "پیام یافت نشد")
            await send_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}


    elif chat_id in user_data and user_data[chat_id]["step"] == "chat_id" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل مدیر خارج شدید", keyboard_help)
            del user_data[chat_id]
        else:
            if "forwarded_from" in message:
                forward_id = message["forwarded_from"]["from_sender_id"]
                await send_message(session, chat_id, f"forwarded caht-id -> {forward_id}")
                await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            else:
                await send_message(session, chat_id, f"your caht-id -> {user_id}")
                await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}

    elif chat_id in user_data and user_data[chat_id]["step"] == "add_admin" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل مدیر خارج شدید", keyboard_help)
            del user_data[chat_id]
        else:
            generall.register_admin(text)
            await send_message(session, chat_id, "ادمین استخدام شد.")
            await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}
    
    elif chat_id in user_data and user_data[chat_id]["step"] == "remove_admin" and chat_type == 'User':
        if text == "/exit":
            await send_message_keyboard(session, chat_id, "از پنل مدیر خارج شدید", keyboard_help)
            del user_data[chat_id]
        else:
            res = generall.get_admins()
            ress = [r[0] for r in res]
            if text in ress:
                generall.delete_admin(text)
                await send_message(session, chat_id, "ادمین حذف شد.")
            else:
                await send_message(session, chat_id, "ادمین وجود ندارد")
            await send_message_keyboard(session, chat_id, "یکی از گزینه ها را انتخاب کنید\nبرای خروج از پنل مدیریت دستور /exit را وارد کنید.", keyboard_manager)
            user_data[chat_id] = {"step":"choose_operation"}
        
    elif text == "درخواست عضویت در گروه VIP":
        await send_message_keyboard(session, chat_id, "درخواست عضویت شما ثبت شد.", learn_keyboard)
        res = await send_message(session, support_group_id, f"VIP-VIP-VIP-VIP-VIP\nساخت لینک یکبار مصرف\n{chat_id}")
        print(await res.json())

    elif chat_id == manager_ch:
        if "reply_to_message_id" in message:
            msg_id = message["reply_to_message_id"]
            action, target_chat_id = text.split("_")
            if action == 'Ok':
                await send_message_keyboard(session, target_chat_id, """
                دسترسیِ شما به اندیکاتور در اکانتِ تریدینگ‌ویو فعال شد.

                برای مشاهده و استفاده، کافیست:

                1. واردِ سایتِ TradingView شوید.

                2. از منوی بالا به بخش Indicators بروید.

                3. در تبِ Invite-only scripts، اندیکاتور LUXalpha برای شما ظاهر شده است؛ آن را روی نمودار فعال کنید

                4.توافق‌نامه سلب مسئولیت:

                شما می‌پذیرید که اندیکاتورهای LUXalpha و ربات های luxalpha صرفاً ابزارهای کمکی جهت تحلیل بوده و مسئولیت نهایی تمامی معاملات، مدیریت سرمایه و حد ضرر، مستقیماً بر عهده تریدر است. ما هیچ‌گونه تعهدی نسبت به نتایج معاملات شخصی شما نداریم
                
                """, keyboard_help)
                await edit_text3(session, msg_id=msg_id, text=f"فعال شد")
    
    elif text == "get":
        await send_message(session, chat_id, chat_id)

async def get_updates(session):
    # generall.make_offset()
    offset1 = generall.get_offset()
    #print(offset1)
    res = {}
    try:
        if offset1 == 'n':
            async with session.post(URL + "getUpdates") as resp:
                if resp.status == 200:
                    try:
                        res = await resp.json()
                    except:
                        print("n")
                        await asyncio.sleep(3)
                
                elif resp.status == 502:
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(5)
        else:
            async with session.post(URL + "getUpdates", json={"offset_id": offset1,}) as resp:
                if resp.status == 200:
                    try:
                        res = await resp.json()
                    except:
                        print("else")
                        await asyncio.sleep(3)
                
                elif resp.status == 502:
                    await asyncio.sleep(3)
                else:
                    await asyncio.sleep(5)
    except Exception as e:
        print(f"Error in get_updates: {e}")
        await asyncio.sleep(5)

    data = res.get("data", {})
    updates = data.get("updates", [])
    offset = data.get("next_offset_id")
    if offset != None:
        generall.set_offset(offset)
    return updates

async def main():
    async with aiohttp.ClientSession() as session:
        asyncio.create_task(check_expirations(session))
        asyncio.create_task(check_expirations3(session))
        asyncio.create_task(check_expirations_ban(session))
        asyncio.create_task(check_expirations_ban_u(session))
        asyncio.create_task(check_expirations_u(session))
        # asyncio.create_task(check_expirations_ban_bot(session))
        # asyncio.create_task(check_expirations_bot(session))

        while True:
            if not db_pool.check_connection():
                print("database unreachable")
                asyncio.sleep(3)
                continue
            updates = await get_updates(session)

            for update in updates:
                if update['type'] == 'NewMessage':
                    asyncio.create_task(handle_message(session, update))
                # elif "callback_query" in update:
                #     callback = update.get("callback_query")
                #     asyncio.create_task(handle_callback(session, callback))
            
            await asyncio.sleep(0.5)
asyncio.run(main())
