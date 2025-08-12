import asyncio
import os
import json
import getpass
from telethon import TelegramClient, events
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserNotMutualContactError, FloodWaitError, ChatAdminRequiredError, UserAlreadyParticipantError
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.channels import InviteToChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetFullChatRequest
import time
import random


class TelegramMemberTransferBot:

    def __init__(self):
        self.client = None
        self.source_group = None
        self.destination_group = None
        self.custom_invite_message = None
        self.settings_file = 'bot_settings.json'
        self.api_credentials_file = 'api_credentials.json'
        self.api_id = None
        self.api_hash = None
        self.load_settings()
        self.load_api_credentials()

    def load_settings(self):
        """بارگذاری تنظیمات از فایل"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.source_group = settings.get('source_group')
                    self.destination_group = settings.get('destination_group')
                    self.custom_invite_message = settings.get('custom_invite_message')
            except:
                pass

    def save_settings(self):
        """ذخیره تنظیمات در فایل"""
        settings = {
            'source_group': self.source_group,
            'destination_group': self.destination_group,
            'custom_invite_message': self.custom_invite_message
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def load_api_credentials(self):
        """بارگذاری API credentials از فایل"""
        if os.path.exists(self.api_credentials_file):
            try:
                with open(self.api_credentials_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                    self.api_id = credentials.get('api_id')
                    self.api_hash = credentials.get('api_hash')
            except:
                pass

    def save_api_credentials(self, api_id, api_hash):
        """ذخیره API credentials در فایل"""
        credentials = {
            'api_id': api_id,
            'api_hash': api_hash
        }
        with open(self.api_credentials_file, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, ensure_ascii=False, indent=2)

    async def get_api_credentials_manually(self):
        """دریافت دستی API credentials"""
        print("\n🔧 دریافت دستی API credentials:")
        print("1. به آدرس https://my.telegram.org بروید")
        print("2. با شماره تلفن خود وارد شوید")
        print("3. به قسمت API development tools بروید")
        print("4. اگر application ندارید، یکی بسازید")
        print("5. API ID و API Hash را کپی کنید")

        api_id = input("\n📋 API ID را وارد کنید: ").strip()
        api_hash = input("🔐 API Hash را وارد کنید: ").strip()

        if api_id.isdigit() and len(api_hash) > 10:
            return int(api_id), api_hash
        else:
            print("❌ API ID یا API Hash نامعتبر است")
            return None, None

    async def start_bot(self):
        """راه‌اندازی ربات"""
        print("🤖 خوش آمدید به ربات انتقال اعضای تلگرام")
        print("=" * 50)

        # بررسی وجود API credentials
        if not self.api_id or not self.api_hash:
            print("🔑 API credentials یافت نشد.")
            api_id, api_hash = await self.get_api_credentials_manually()

            if not api_id or not api_hash:
                print("❌ خطا در دریافت API credentials. لطفاً دوباره تلاش کنید.")
                return

            self.api_id = api_id
            self.api_hash = api_hash
            self.save_api_credentials(api_id, api_hash)
            print("💾 API credentials ذخیره شد.")

        # ایجاد کلاینت
        self.client = TelegramClient('member_transfer_session', self.api_id, self.api_hash)

        try:
            # اتصال و احراز هویت
            await self.client.start()

            # دریافت اطلاعات کاربر
            me = await self.client.get_me()
            print(f"✅ با موفقیت وارد شدید به عنوان: {me.first_name}")

            # ثبت هندلرهای کامند
            self.register_handlers()

            print("\n📋 کامندهای موجود:")
            print("• .راهنما - نمایش راهنمای کامل")
            print("• .تنظیم گروه مبدا - تنظیم گروه مبدا")
            print("• .تنظیم گروه مقصد - تنظیم گروه مقصد")
            print("• .شروع انتقال - شروع انتقال اعضا")
            print("• .ارسال لینک - فقط لینک برای غیر عضوها")
            print("• .تنظیم متن دعوت - تنظیم متن سفارشی دعوت")
            print("• .راهنمای تنظیم - راهنمای دریافت API")
            print("• .ریست انتقال - پاک کردن تنظیمات")
            print("• .ریست اکانت - پاک کردن session و خروج")
            print("• .وضعیت - نمایش وضعیت فعلی")
            print("\n🚀 ربات آماده است! کامندها را در تلگرام اجرا کنید.")
            print("برای خروج Ctrl+C را فشار دهید.")

            # اجرای ربات
            await self.client.run_until_disconnected()

        except Exception as e:
            print(f"❌ خطا در راه‌اندازی: {str(e)}")

    def register_handlers(self):
        """ثبت هندلرهای کامند"""

        @self.client.on(events.NewMessage(pattern=r'\.راهنما'))
        async def help_handler(event):
            await self.show_help(event)

        @self.client.on(events.NewMessage(pattern=r'\.تنظیم گروه مبدا'))
        async def set_source_handler(event):
            await self.set_source_group(event)

        @self.client.on(events.NewMessage(pattern=r'\.تنظیم گروه مقصد'))
        async def set_dest_handler(event):
            await self.set_destination_group(event)

        @self.client.on(events.NewMessage(pattern=r'\.شروع انتقال'))
        async def start_transfer_handler(event):
            await self.start_transfer(event)

        @self.client.on(events.NewMessage(pattern=r'\.ریست انتقال'))
        async def reset_handler(event):
            await self.reset_settings(event)

        @self.client.on(events.NewMessage(pattern=r'\.وضعیت'))
        async def status_handler(event):
            await self.show_status(event)

        @self.client.on(events.NewMessage(pattern=r'\.ارسال لینک'))
        async def send_links_handler(event):
            await self.send_links_only(event)

        @self.client.on(events.NewMessage(pattern=r'\.راهنمای تنظیم'))
        async def setup_guide_handler(event):
            await self.show_setup_guide(event)

        @self.client.on(events.NewMessage(pattern=r'\.تنظیم متن دعوت'))
        async def set_invite_message_handler(event):
            await self.set_custom_invite_message(event)

        @self.client.on(events.NewMessage(pattern=r'\.ریست اکانت'))
        async def reset_account_handler(event):
            await self.reset_account(event)

    async def show_help(self, event):
        """نمایش راهنمای کامل"""
        help_text = """
🤖 **راهنمای ربات انتقال اعضای تلگرام**

📋 **کامندهای اصلی:**

🔹 **.راهنما**
   نمایش این راهنمای

🔹 **.تنظیم گروه مبدا**
   تنظیم گروه فعلی به عنوان گروه مبدا (منبع اعضا)
   باید در گروه مورد نظر این کامند را اجرا کنید

🔹 **.تنظیم گروه مقصد**
   تنظیم گروه فعلی به عنوان گروه مقصد (مقصد انتقال)
   باید در گروه مورد نظر این کامند را اجرا کنید

🔹 **.شروع انتقال**
   شروع فرآیند انتقال اعضا از گروه مبدا به مقصد
   - اعضایی که امکان اضافه کردن دارند، اضافه می‌شوند
   - اعضایی که اضافه نمی‌شوند، لینک دعوت دریافت می‌کنند

🔹 **.ارسال لینک**
   فقط برای کسانی که در گروه مبدا هستند اما در مقصد نیستند
   لینک دعوت ارسال می‌کند (بدون تلاش برای اضافه کردن)

🔹 **.تنظیم متن دعوت [متن دلخواه]**
   تنظیم متن سفارشی برای پیام دعوت
   متغیرهای قابل استفاده: {user_name}, {source_group}, {dest_group}, {invite_link}

🔹 **.ریست انتقال**
   پاک کردن تمام تنظیمات و شروع مجدد

🔹 **.وضعیت**
   نمایش گروه‌های تنظیم شده فعلی

🔹 **.راهنمای تنظیم**
   راهنمای دریافت API ID و API Hash

🔹 **.ریست اکانت**
   پاک کردن session فایل‌ها و خروج از اکانت فعلی

⚠️ **نکات مهم:**
• حتماً مجوز ادمین در هر دو گروه داشته باشید
• ربات به تدریج اعضا را منتقل می‌کند تا مسدود نشود
• در صورت خطا، عملیات متوقف می‌شود

🛠️ **ویژگی‌های اضافی:**
• ذخیره خودکار تنظیمات
• مدیریت خطاهای تلگرام
• گزارش‌دهی دقیق از نتایج
• تأخیر هوشمند برای جلوگیری از محدودیت

💡 برای شروع، ابتدا گروه مبدا و مقصد را تنظیم کنید.
        """
        await event.respond(help_text)

    async def set_source_group(self, event):
        """تنظیم گروه مبدا"""
        try:
            chat = await event.get_chat()
            if hasattr(chat, 'title'):
                self.source_group = {
                    'id': chat.id,
                    'title': chat.title,
                    'type': 'channel' if isinstance(chat, Channel) else 'group'
                }
                self.save_settings()
                await event.respond(f"✅ گروه مبدا تنظیم شد: **{chat.title}**")
            else:
                await event.respond("❌ این کامند باید در گروه اجرا شود!")
        except Exception as e:
            await event.respond(f"❌ خطا در تنظیم گروه مبدا: {str(e)}")

    async def set_destination_group(self, event):
        """تنظیم گروه مقصد"""
        try:
            chat = await event.get_chat()
            if hasattr(chat, 'title'):
                self.destination_group = {
                    'id': chat.id,
                    'title': chat.title,
                    'type': 'channel' if isinstance(chat, Channel) else 'group'
                }
                self.save_settings()
                await event.respond(f"✅ گروه مقصد تنظیم شد: **{chat.title}**")
            else:
                await event.respond("❌ این کامند باید در گروه اجرا شود!")
        except Exception as e:
            await event.respond(f"❌ خطا در تنظیم گروه مقصد: {str(e)}")

    async def show_status(self, event):
        """نمایش وضعیت فعلی"""
        status_text = "📊 **وضعیت ربات:**\n\n"

        if self.source_group:
            status_text += f"🟢 گروه مبدا: {self.source_group['title']}\n"
        else:
            status_text += "🔴 گروه مبدا: تنظیم نشده\n"

        if self.destination_group:
            status_text += f"🟢 گروه مقصد: {self.destination_group['title']}\n"
        else:
            status_text += "🔴 گروه مقصد: تنظیم نشده\n"

        if self.custom_invite_message:
            status_text += f"📝 متن دعوت: سفارشی تنظیم شده\n"
        else:
            status_text += "📝 متن دعوت: پیش‌فرض\n"

        if self.source_group and self.destination_group:
            status_text += "\n✅ آماده برای انتقال اعضا"
        else:
            status_text += "\n⚠️ ابتدا گروه‌ها را تنظیم کنید"

        await event.respond(status_text)

    async def reset_settings(self, event):
        """ریست تنظیمات"""
        self.source_group = None
        self.destination_group = None
        self.custom_invite_message = None
        if os.path.exists(self.settings_file):
            os.remove(self.settings_file)
        await event.respond(
            "🔄 تمام تنظیمات پاک شد. می‌توانید مجدداً تنظیم کنید.")

    async def show_setup_guide(self, event):
        """راهنمای دریافت API"""
        guide_text = """
🔧 **راهنمای دریافت API ID و API Hash**

📋 **مراحل دریافت:**

1️⃣ **رفتن به سایت**
   • به آدرس https://my.telegram.org بروید
   • صفحه ورود باز خواهد شد

2️⃣ **ورود به حساب**
   • شماره تلفن خود را وارد کنید
   • کد تأیید دریافتی را وارد کنید

3️⃣ **دسترسی به API tools**
   • روی "API development tools" کلیک کنید
   • اگر قبلاً application ساخته‌اید، لیست نمایش داده می‌شود

4️⃣ **ساخت Application (در صورت نیاز)**
   • روی "Create new application" کلیک کنید
   • نام برنامه: Member Transfer Bot
   • Platform: Other
   • توضیحات: انتقال اعضای تلگرام

5️⃣ **دریافت Credentials**
   • API ID: عدد 8 رقمی
   • API Hash: رشته 32 کاراکتری

⚠️ **نکات امنیتی:**
• هرگز API credentials را به اشتراک نگذارید
• این اطلاعات فقط روی دستگاه شما ذخیره می‌شود
• در صورت مشکوک بودن، application را حذف کنید

💾 **ذخیره‌سازی:**
• اطلاعات در فایل محلی ذخیره می‌شود
• برای اجراهای بعدی نیازی به تکرار نیست

🔄 **تنظیم مجدد:**
• از کامند `.ریست اکانت` استفاده کنید
• API credentials جدید وارد کنید
        """
        await event.respond(guide_text)

    async def reset_account(self, event):
        """پاک کردن session فایل‌ها و خروج از اکانت"""
        try:
            await event.respond("🔄 در حال پاک کردن اطلاعات اکانت...")

            # قطع اتصال کلاینت
            if self.client:
                await self.client.log_out()
                await self.client.disconnect()

            # پاک کردن همه فایل‌های session ممکن
            session_files = [
                'member_transfer_session.session',
                'member_transfer_session.session-journal',
                'member_transfer_session.session-wal',
                'member_transfer_session.session-shm'
            ]

            deleted_files = []
            for session_file in session_files:
                try:
                    if os.path.exists(session_file):
                        os.remove(session_file)
                        deleted_files.append(session_file)
                        print(f"🗑️ فایل {session_file} پاک شد")
                except PermissionError:
                    print(f"⚠️ نتوانستم فایل {session_file} را پاک کنم (مجوز)")
                except Exception as file_error:
                    print(f"⚠️ خطا در پاک کردن {session_file}: {str(file_error)}")

            # پاک کردن تنظیمات ربات
            if os.path.exists(self.settings_file):
                try:
                    os.remove(self.settings_file)
                    deleted_files.append(self.settings_file)
                    print(f"🗑️ فایل {self.settings_file} پاک شد")
                except:
                    pass

            # پاک کردن API credentials
            if os.path.exists(self.api_credentials_file):
                try:
                    os.remove(self.api_credentials_file)
                    deleted_files.append(self.api_credentials_file)
                    print(f"🗑️ فایل {self.api_credentials_file} پاک شد")
                except:
                    pass

            if deleted_files:
                print("✅ اطلاعات اکانت پاک شد. برای ورود مجدد ربات را دوباره اجرا کنید.")
                await event.respond("✅ اطلاعات اکانت پاک شد. ربات در حال خروج...")
            else:
                print("⚠️ هیچ session فایلی یافت نشد")
                await event.respond("⚠️ هیچ session فایلی برای پاک کردن یافت نشد")

            # خروج از برنامه
            import sys
            sys.exit(0)

        except Exception as e:
            error_msg = f"❌ خطا در پاک کردن اطلاعات اکانت: {str(e)}"
            print(error_msg)
            await event.respond(error_msg)

    async def set_custom_invite_message(self, event):
        """تنظیم متن سفارشی دعوت"""
        message_text = event.message.text

        # حذف کامند از ابتدای متن
        if message_text.startswith('.تنظیم متن دعوت'):
            custom_message = message_text.replace('.تنظیم متن دعوت', '').strip()

            if custom_message:
                self.custom_invite_message = custom_message
                self.save_settings()

                preview_text = f"""
✅ **متن دعوت تنظیم شد!**

📝 **متن شما:**
{custom_message}

💡 **متغیرهای قابل استفاده:**
• {{user_name}} - نام کاربر
• {{source_group}} - نام گروه مبدا  
• {{dest_group}} - نام گروه مقصد
• {{invite_link}} - لینک دعوت

📋 **مثال نهایی:**
{self.format_invite_message(custom_message, "علی احمدی", "گروه قدیم", "گروه جدید", "https://t.me/example")}
                """
                await event.respond(preview_text)
            else:
                await event.respond("""
❌ **لطفاً متن دعوت را وارد کنید!**

📝 **نحوه استفاده:**
`.تنظیم متن دعوت سلام {user_name} عزیز! گروه {source_group} به {dest_group} انتقال یافت: {invite_link}`

💡 **متغیرهای قابل استفاده:**
• {user_name} - نام کاربر
• {source_group} - نام گروه مبدا
• {dest_group} - نام گروه مقصد  
• {invite_link} - لینک دعوت
                """)

    def format_invite_message(self, template, user_name, source_group, dest_group, invite_link):
        """فرمت کردن متن دعوت با متغیرها"""
        if not template:
            return f"سلام {user_name} عزیزم گروه {source_group} انتقال پیدا کرده به {dest_group} خوشحال میشیم تو گروه جدید ببینیمتون 💖:\n\n{invite_link}"

        return template.format(
            user_name=user_name,
            source_group=source_group, 
            dest_group=dest_group,
            invite_link=invite_link
        )

    async def send_invite_link(self, user, invite_link, link_sent_count, error_count):
        """ارسال لینک دعوت به کاربر"""
        if invite_link and hasattr(user, 'id'):
            user_name = user.first_name if hasattr(user, 'first_name') and user.first_name else "کاربر عزیز"

            # فرمت کردن متن با متغیرها
            source_group_name = self.source_group['title'] if self.source_group else "گروه قدیم"
            dest_group_name = self.destination_group['title'] if self.destination_group else "گروه جدید"

            message_text = self.format_invite_message(
                self.custom_invite_message,
                user_name,
                source_group_name,
                dest_group_name, 
                invite_link
            )

            # تلاش اول برای ارسال فوری
            try:
                await self.client.send_message(user, message_text)
                print(f"📨 لینک برای {user_name} ارسال شد")
                return {'success': True}
            except FloodWaitError as e:
                print(f"⏳ محدودیت ارسال پیام: {e.seconds} ثانیه صبر برای {user_name}...")
                await asyncio.sleep(e.seconds)
                # تلاش مجدد بعد از انتظار
                try:
                    await self.client.send_message(user, message_text)
                    print(f"📨 لینک برای {user_name} ارسال شد (تلاش دوم)")
                    return {'success': True}
                except Exception as retry_error:
                    print(f"❌ خطا در تلاش دوم ارسال پیام به {user_name}: {str(retry_error)}")
                    return {'success': False}
            except Exception as send_error:
                if "Too many requests" in str(send_error):
                    print(f"⚠️ محدودیت ارسال پیام برای {user_name} - لینک بعداً ارسال خواهد شد")
                    # در اینجا می‌توانیم لیست انتظار ایجاد کنیم
                    return {'success': False, 'retry_later': True}
                else:
                    print(f"❌ خطا در ارسال پیام به {user_name}: {str(send_error)}")
                    return {'success': False}
        else:
            user_name = user.first_name if hasattr(user, 'first_name') and user.first_name else "کاربر"
            print(f"❌ لینک دعوت موجود نیست یا کاربر نامعتبر: {user_name}")
            return {'success': False}

    async def send_links_only(self, event):
        """ارسال لینک فقط برای کسانی که در مبدا هستند اما در مقصد نیستند"""
        if not self.source_group or not self.destination_group:
            await event.respond("❌ ابتدا گروه مبدا و مقصد را تنظیم کنید!")
            return

        await event.respond("📨 شروع ارسال لینک برای غیر عضوها...")

        try:
            # دریافت اعضای گروه مبدا
            source_participants = []
            async for user in self.client.iter_participants(self.source_group['id']):
                if isinstance(user, User) and not user.bot:
                    source_participants.append(user)

            # دریافت اعضای گروه مقصد
            dest_participants = set()
            async for user in self.client.iter_participants(self.destination_group['id']):
                if isinstance(user, User) and not user.bot:
                    dest_participants.add(user.id)

            # فیلتر کردن: فقط کسانی که در مبدا هستند اما در مقصد نیستند
            users_to_send_link = [user for user in source_participants if user.id not in dest_participants]

            await event.respond(f"📊 تعداد {len(users_to_send_link)} نفر در گروه مبدا هستند اما در مقصد نیستند.")

            if len(users_to_send_link) == 0:
                await event.respond("✅ همه اعضای گروه مبدا در گروه مقصد حضور دارند!")
                return

            # دریافت لینک دعوت گروه مقصد
            try:
                if self.destination_group['type'] == 'channel':
                    dest_entity = await self.client.get_entity(self.destination_group['id'])
                    invite_link = f"https://t.me/{dest_entity.username}" if dest_entity.username else None
                    if not invite_link:
                        full_chat = await self.client(GetFullChannelRequest(self.destination_group['id']))
                        invite_link = full_chat.full_chat.exported_invite.link if full_chat.full_chat.exported_invite else None
                else:
                    full_chat = await self.client(GetFullChatRequest(self.destination_group['id']))
                    invite_link = full_chat.full_chat.exported_invite.link if full_chat.full_chat.exported_invite else None
            except:
                invite_link = None

            if not invite_link:
                await event.respond("❌ نتوانستم لینک دعوت گروه مقصد را دریافت کنم!")
                return

            # شمارنده‌ها
            link_sent_count = 0
            error_count = 0

            # ارسال لینک برای کاربران
            for i, user in enumerate(users_to_send_link):
                try:
                    result = await self.send_invite_link(user, invite_link, 0, 0)
                    if result['success']:
                        link_sent_count += 1
                        print(f"📨 لینک برای {user.first_name if user.first_name else 'کاربر'} ارسال شد")
                    else:
                        error_count += 1

                    # تأخیر برای جلوگیری از محدودیت
                    if i % 3 == 0 and i > 0:
                        delay = random.randint(3, 7)
                        print(f"⏸️ استراحت {delay} ثانیه...")
                        await asyncio.sleep(delay)

                    # گزارش پیشرفت
                    if (i + 1) % 5 == 0:
                        progress_text = f"📈 پیشرفت ارسال لینک: {i + 1}/{len(users_to_send_link)}\n"
                        progress_text += f"📨 لینک ارسال شده: {link_sent_count}\n"
                        progress_text += f"❌ خطا: {error_count}"
                        await event.respond(progress_text)

                except Exception as e:
                    error_count += 1
                    print(f"❌ خطا در ارسال لینک به {user.first_name if user.first_name else 'کاربر'}: {str(e)}")

            # گزارش نهایی
            final_report = f"""
📨 **ارسال لینک تکمیل شد!**

📊 **آمار نهایی:**
• کل کاربران هدف: {len(users_to_send_link)}
• 📨 لینک ارسال شده: {link_sent_count}
• ❌ خطا: {error_count}

🎯 **نرخ موفقیت:** {(link_sent_count / len(users_to_send_link) * 100):.1f}%
            """
            await event.respond(final_report)

        except Exception as e:
            await event.respond(f"❌ خطای کلی در ارسال لینک: {str(e)}")

    async def start_transfer(self, event):
        """شروع انتقال اعضا"""
        if not self.source_group or not self.destination_group:
            await event.respond("❌ ابتدا گروه مبدا و مقصد را تنظیم کنید!")
            return

        await event.respond("🚀 شروع انتقال اعضا...")

        try:
            # دریافت اعضای گروه مبدا
            source_participants = []
            async for user in self.client.iter_participants(
                    self.source_group['id']):
                if isinstance(user, User) and not user.bot:
                    source_participants.append(user)

            await event.respond(
                f"📊 تعداد {len(source_participants)} عضو در گروه مبدا یافت شد."
            )

            # شمارنده‌ها
            added_count = 0
            link_sent_count = 0
            error_count = 0

            # دریافت لینک دعوت گروه مقصد
            try:
                if self.destination_group['type'] == 'channel':
                    dest_entity = await self.client.get_entity(
                        self.destination_group['id'])
                    invite_link = f"https://t.me/{dest_entity.username}" if dest_entity.username else None
                    if not invite_link:
                        full_chat = await self.client(
                            GetFullChannelRequest(self.destination_group['id'])
                        )
                        invite_link = full_chat.full_chat.exported_invite.link if full_chat.full_chat.exported_invite else None
                else:
                    full_chat = await self.client(
                        GetFullChatRequest(self.destination_group['id']))
                    invite_link = full_chat.full_chat.exported_invite.link if full_chat.full_chat.exported_invite else None
            except:
                invite_link = None

            # انتقال اعضا
            for i, user in enumerate(source_participants):
                try:
                    # تلاش برای اضافه کردن عضو
                    if self.destination_group['type'] == 'channel':
                        await self.client(
                            InviteToChannelRequest(
                                channel=self.destination_group['id'],
                                users=[user]))
                    else:
                        await self.client(
                            AddChatUserRequest(
                                chat_id=self.destination_group['id'],
                                user_id=user,
                                fwd_limit=0))

                    added_count += 1
                    print(f"✅ {user.first_name} اضافه شد")

                except UserAlreadyParticipantError:
                    print(f"⚠️ {user.first_name} قبلاً عضو است")

                except (UserPrivacyRestrictedError, UserNotMutualContactError):
                    # ارسال لینک به کاربر (تنظیمات حریم خصوصی)
                    result = await self.send_invite_link(user, invite_link, 0, 0)
                    if result['success']:
                        link_sent_count += 1
                        print(f"📨 شمارنده لینک: {link_sent_count}")
                    else:
                        error_count += 1

                except FloodWaitError as e:
                    print(f"⏳ محدودیت زمانی: {e.seconds} ثانیه صبر...")
                    await asyncio.sleep(e.seconds)
                    continue

                except ChatAdminRequiredError:
                    await event.respond("❌ نیاز به دسترسی ادمین در گروه مقصد!")
                    return

                except Exception as e:
                    # برای سایر خطاها هم لینک ارسال کن (Too many requests, Invalid object ID و غیره)
                    if "Too many requests" in str(e) or "Invalid object ID" in str(e):
                        # تلاش برای ارسال لینک
                        result = await self.send_invite_link(user, invite_link, 0, 0)
                        if result['success']:
                            link_sent_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                    print(f"❌ خطا برای {user.first_name if hasattr(user, 'first_name') and user.first_name else 'کاربر'}: {str(e)}")

                # تأخیر برای جلوگیری از محدودیت
                if i % 5 == 0 and i > 0:
                    delay = random.randint(2, 5)
                    print(f"⏸️ استراحت {delay} ثانیه...")
                    await asyncio.sleep(delay)

                # گزارش پیشرفت
                if (i + 1) % 10 == 0:
                    progress_text = f"📈 پیشرفت: {i + 1}/{len(source_participants)}\n"
                    progress_text += f"✅ اضافه شده: {added_count}\n"
                    progress_text += f"📨 لینک ارسال شده: {link_sent_count}\n"
                    progress_text += f"❌ خطا: {error_count}"
                    print(f"📊 آمار فعلی - اضافه شده: {added_count}, لینک ارسال شده: {link_sent_count}, خطا: {error_count}")
                    await event.respond(progress_text)

            # گزارش نهایی
            final_report = f"""
🎉 **انتقال اعضا تکمیل شد!**

📊 **آمار نهایی:**
• کل اعضا: {len(source_participants)}
• ✅ اضافه شده: {added_count}
• 📨 لینک ارسال شده: {link_sent_count}
• ❌ خطا: {error_count}

🎯 **نرخ موفقیت:** {((added_count + link_sent_count) / len(source_participants) * 100):.1f}%
            """
            await event.respond(final_report)

        except Exception as e:
            await event.respond(f"❌ خطای کلی در انتقال: {str(e)}")


# تابع اصلی
async def main():
    bot = TelegramMemberTransferBot()
    await bot.start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 ربات متوقف شد.")
