import os
import yt_dlp
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# التوكن الخاص بك
# TOKEN = '8101740282:AAGwoOxziGcRmOIyH4PzFx1pve-Pp8DIrp0'
TOKEN = '8101740282:AAGwoOxziGcRmOIyH4PzFx1pve-Pp8DIrp0'
# دالة لإرسال رسالة ترحيب
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أنا هنا لمساعدتك في تنزيل فيديوهات YouTube.\n"
                              "يرجى إرسال رابط الفيديو الذي تريد تنزيله.")

# دالة لتنزيل الفيديو عند استلام الرابط
def download_video(update: Update, context: CallbackContext):
    video_url = update.message.text  # الحصول على الرابط المرسل من المستخدم

    # مجلد التنزيل
    output_dir = 'downloads'
    os.makedirs(output_dir, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجودًا
    output_file = os.path.join(output_dir, 'video.mp4')

    # إعدادات yt-dlp
    ydl_opts = {
        'format': 'best[filesize<50M]',  # اختيار أفضل جودة بحجم أقل من 50MB
        'outtmpl': output_file,  # مسار حفظ الفيديو
    }

    try:
        # إعلام المستخدم بأن التنزيل بدأ
        update.message.reply_text("جاري تنزيل الفيديو...")

        # تنزيل الفيديو
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)  # تنزيل الفيديو
            video_title = info_dict.get('title', 'video')  # الحصول على عنوان الفيديو

        # التحقق من حجم الفيديو
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # الحجم بالميجابايت
        if file_size > 50:
            update.message.reply_text("عذرًا، حجم الفيديو أكبر من 50MB ولا يمكن إرساله عبر Telegram.")
            os.remove(output_file)  # حذف الفيديو إذا كان كبيرًا
            return

        # إرسال الفيديو إلى المستخدم
        with open(output_file, 'rb') as video_file:
            update.message.reply_video(video=video_file, caption=f'تم تنزيل الفيديو: {video_title}')

        # حذف الفيديو بعد الإرسال
        os.remove(output_file)

    except Exception as e:
        update.message.reply_text(f'حدث خطأ أثناء تنزيل الفيديو: {str(e)}')
        if os.path.exists(output_file):
            os.remove(output_file)  # حذف الفيديو في حالة حدوث خطأ

def main():
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))  # معالج للأمر /start
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, download_video))  # معالجة الرسائل النصية

    # طباعة رسالة عند بدء البوت
    print("البوت يعمل الآن!")

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()