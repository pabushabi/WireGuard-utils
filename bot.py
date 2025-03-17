from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import subprocess
import os
import re
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHITELIST_USER_IDS = list(map(int, os.getenv("WHITELIST_USER_IDS").split(",")))
CLIENTS_DIR = os.getenv("CLIENTS_DIR")
SERVICE_NAME = os.getenv("SERVICE_NAME")
SCRIPT_PATH = os.getenv("SCRIPT_PATH")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет! Я твой телеграм бот. Как дела? {update.message.text}')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(update.message.from_user.id)
    user_text = update.message.text
    if user_text == "ping":
        await update.message.reply_text(f'pong')
    else:
        await update.message.reply_text(f'Вы написали: {user_text}')


async def addclient(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in WHITELIST_USER_IDS:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text(f'Вы не указали имя клиента')
        else:
            try:
                result = subprocess.run(
                    ["python3", SCRIPT_PATH] + args,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0: 
                    await update.message.reply_text(f"Ошибка при выполнении скрипта: {result.stderr}")
                    return
                
                await update.message.reply_text(f"Результат работы скрипта:\n{result.stdout}")

                file_names = extract_file_names(args)
                for file_name in file_names:
                    file_path = f"{CLIENTS_DIR}/wg-{file_name}.conf"

                    if os.path.exists(file_path): 
                        with open(file_path, "rb") as file:
                            await update.message.reply_document(document=file, filename=file_path)
                    else:
                        await update.message.reply_text(f"Файл {file_path} не найден.")

                result = subprocess.run(
                    ["systemctl", "restart", SERVICE_NAME, "--no-pager"],
                    capture_output=True,
                    text=True
                )

                if (result.returncode != 0):
                    await update.message.reply_text(f"Ошибка при перезапуске сервиса: {result.stderr}")
                    return
                else:
                    await update.message.reply_text("Сервис успешно перезапущен.")

            except Exception as e:
                await update.message.reply_text(f"Ошибка при выполнении скрипта: {e}")


async def list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in WHITELIST_USER_IDS:
        try:
            files = os.listdir(CLIENTS_DIR)
            
            if not files:
                await update.message.reply_text("Файлы не найдены.")
                return
            
            message = "Список файлов:\n" + "\n".join(files)
            await update.message.reply_text(message)
        except Exception as e: 
            await update.message.reply_text(f"Ошибка при получении файлов: {e}")


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in WHITELIST_USER_IDS:
        args = context.args
        if len(args) == 0:
            await update.message.reply_text(f'Вы не указали имя файла')
        try: 
            for file_name in args:
                file_path = f"{CLIENTS_DIR}/wg-{file_name}.conf"

                if os.path.exists(file_path):
                        with open(file_path, "rb") as file:
                            await update.message.reply_document(document=file, filename=file_path)
                else:
                    await update.message.reply_text(f"Файл {file_path} не найден.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при загрузке файла: {e}")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in WHITELIST_USER_IDS:
        args = context.args
        show_full = "full" in args
        try:
            result = subprocess.run(
                ["systemctl", "status", SERVICE_NAME, "--no-pager"],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout
            if result.returncode != 0:
                await update.message.reply_text(f"Ошибка при выполнении команды: {result.stderr}")
                return

            if show_full:
                await update.message.reply_text(f"Статус сервиса:\n{output}")
            else:
                line = re.search("Active:.*", output)
                if line:
                    await update.message.reply_text(f"Стаус сервиса:\n{line.group()}")
                else:
                    await update.message.reply_text(f"Статус сервиса:\n{output.splitlines()[2]}")
        except subprocess.TimeoutExpired:
            await update.message.reply_text("Время ожидания истекло.")
        except Exception as e:
            await update.message.reply_text(f"Ошибка при выполнении команды: {e}")



def extract_file_names(args):
    file_names = []
    skip_next = False 

    for arg in args:
        if skip_next:
            skip_next = False
            continue

        if arg.startswith("-"):
            skip_next = True
        else:
            file_names.append(arg)

    return file_names


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", addclient))
    application.add_handler(CommandHandler("list", list))
    application.add_handler(CommandHandler("save", save))
    application.add_handler(CommandHandler("status", status))

    # text message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()