from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import pytesseract
from PIL import Image
from langdetect import detect_langs, DetectorFactory

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Настройки
TOKEN = "7639621644:AAFKoDTtMEWFYm8Z1D2wDTTYIz1vhEaZGVw"

DetectorFactory.seed = 0

# Приветствия на разных языках
GREETINGS = {
    "en": "Hello! Here is the recognized text:",
    "ru": "Привет! Вот распознанный текст:",
    "zh-cn": "你好! 这是识别的文字：",
    "es": "¡Hola! Aquí está el texto reconocido:",
    "fr": "Bonjour! Voici le texte reconnu:",
    "de": "Hallo! Hier ist der erkannte Text:"
}

async def start(update: Update, context: CallbackContext):
    
    keyboard = [["Старт"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать! Нажмите 'Старт', чтобы начать.",
        reply_markup=reply_markup
    )

# Обработчик нажатия кнопки "Старт"
async def handle_start_button(update: Update, context: CallbackContext):
    if update.message.text == "Старт":
        await update.message.reply_text("Привет! Отправьте мне изображение, чтобы я распознал текст.")

# Обработчик фотографий
async def handle_photo(update: Update, context: CallbackContext):
    # Сохранение изображения
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"{photo_file.file_id}.jpg"
    await photo_file.download_to_drive(photo_path)

    try:
        # Распознавание текста
        image = Image.open(photo_path)
        custom_config = '--psm 6 -l rus+eng+chi_sim+fra+spa+deu'
        text = pytesseract.image_to_string(image, config=custom_config)

        if not text.strip():
            await update.message.reply_text("На изображении не удалось обнаружить текст. Попробуйте загрузить другое изображение.")
            return

        # Определение языков текста
        try:
            detected_langs = detect_langs(text)  # Список языков и вероятностей
        except Exception:
            detected_langs = []

        # Форматирование языков и вероятностей
        if detected_langs:
            lang_probabilities = ", ".join([f"{lang.lang} ({lang.prob:.2f})" for lang in detected_langs])
            primary_lang = detected_langs[0].lang  # Первый язык с наибольшей вероятностью
            greeting = GREETINGS.get(primary_lang, "Привет! Вот распознанный текст:")
        else:
            lang_probabilities = "Не удалось определить языки."
            greeting = "Привет! Вот распознанный текст:"

        # Отправка результата
        await update.message.reply_text(f"{greeting}\n\n{text.strip()}\n\nОбнаруженные языки: {lang_probabilities}")
    finally:
        # Удаление временного файла
        import os
        if os.path.exists(photo_path):
            os.remove(photo_path)

# Основной код
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start_button))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    application.run_polling()

if __name__ == "__main__":
    main()
