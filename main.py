import asyncio
import os
import json
from telethon import TelegramClient, events
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserNotMutualContactError, FloodWaitError, ChatAdminRequiredError, UserAlreadyParticipantError
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.channels import InviteToChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest, GetFullChatRequest
import time
import random

# اطلاعات API شما
API_ID = 21415011
API_HASH = '9c8975607ab13f6873e98efb57a66b82'

class TelegramMemberTransferBot:
    def __init__(self):
        self.client = None
        self.source_group = None
        self.destination_group = None
        self.settings_file = 'bot_settings.json'
        self.load_settings()
        
    def load_settings(self):
        """بارگذاری تنظیمات از فایل"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.source_group = settings.get('source_group')
                    self.destination_group = settings.get('destination_group')
            except:
                pass
    
    def save_settings(self):
        """ذخیره تنظیمات در فایل"""
        settings = {
            'source_group': self.source_group,
            'destination_group': self.destination_group
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    async def start_bot(self):
        """راه‌اندازی ربات"""
        print("🤖 خوش آمدید به ربات انتقال اعضای تلگرام")
        print("=" * 50)
        
        # ایجاد کلاینت
        self.client = TelegramClient('member_transfer_session', API_ID, API_HASH)
        
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
            print("• .ریست انتقال - پاک کردن تنظیمات")
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

    async def show_help(self, event):
        """نمایش راهنمای کامل"""
        help_text = """
🤖 **راهنمای ربات انتقال اعضای تلگرام**

📋 **کامندهای اصلی:**

🔹 **.راهنما**
   نمایش این راهنما

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

🔹 **.ریست انتقال**
   پاک کردن تمام تنظیمات و شروع مجدد

🔹 **.وضعیت**
   نمایش گروه‌های تنظیم شده فعلی

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
        
        if self.source_group and self.destination_group:
            status_text += "\n✅ آماده برای انتقال اعضا"
        else:
            status_text += "\n⚠️ ابتدا گروه‌ها را تنظیم کنید"
        
        await event.respond(status_text)

    async def reset_settings(self, event):
        """ریست تنظیمات"""
        self.source_group = None
        self.destination_group = None
        if os.path.exists(self.settings_file):
            os.remove(self.settings_file)
        await event.respond("🔄 تمام تنظیمات پاک شد. می‌توانید مجدداً تنظیم کنید.")

    async def start_transfer(self, event):
        """شروع انتقال اعضا"""
        if not self.source_group or not self.destination_group:
            await event.respond("❌ ابتدا گروه مبدا و مقصد را تنظیم کنید!")
            return
        
        await event.respond("🚀 شروع انتقال اعضا...")
        
        try:
            # دریافت اعضای گروه مبدا
            source_participants = []
            async for user in self.client.iter_participants(self.source_group['id']):
                if isinstance(user, User) and not user.bot:
                    source_participants.append(user)
            
            await event.respond(f"📊 تعداد {len(source_participants)} عضو در گروه مبدا یافت شد.")
            
            # شمارنده‌ها
            added_count = 0
            link_sent_count = 0
            error_count = 0
            
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
            
            # انتقال اعضا
            for i, user in enumerate(source_participants):
                try:
                    # تلاش برای اضافه کردن عضو
                    if self.destination_group['type'] == 'channel':
                        await self.client(InviteToChannelRequest(
                            channel=self.destination_group['id'],
                            users=[user]
                        ))
                    else:
                        await self.client(AddChatUserRequest(
                            chat_id=self.destination_group['id'],
                            user_id=user,
                            fwd_limit=0
                        ))
                    
                    added_count += 1
                    print(f"✅ {user.first_name} اضافه شد")
                    
                except UserAlreadyParticipantError:
                    print(f"⚠️ {user.first_name} قبلاً عضو است")
                    
                except (UserPrivacyRestrictedError, UserNotMutualContactError):
                    # ارسال لینک به کاربر
                    if invite_link:
                        try:
                            await self.client.send_message(
                                user,
                                f"سلام! شما دعوت شده‌اید به گروه **{self.destination_group['title']}**:\n\n{invite_link}"
                            )
                            link_sent_count += 1
                            print(f"📨 لینک برای {user.first_name} ارسال شد")
                        except:
                            error_count += 1
                            print(f"❌ خطا در ارسال پیام به {user.first_name}")
                    else:
                        error_count += 1
                        print(f"❌ لینک دعوت موجود نیست برای {user.first_name}")
                
                except FloodWaitError as e:
                    print(f"⏳ محدودیت زمانی: {e.seconds} ثانیه صبر...")
                    await asyncio.sleep(e.seconds)
                    continue
                
                except ChatAdminRequiredError:
                    await event.respond("❌ نیاز به دسترسی ادمین در گروه مقصد!")
                    return
                
                except Exception as e:
                    error_count += 1
                    print(f"❌ خطا برای {user.first_name}: {str(e)}")
                
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