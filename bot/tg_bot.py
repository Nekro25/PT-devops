import os, logging, re, paramiko, psycopg2
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv("TOKEN")
ID = os.getenv("ID")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DATABASE")

finds = dict()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r'\+7[ ]?[| |\(|-]?\d{3}[| |\)|-][ ]?\d{3}[| |-]?\d{2}[| |-]?\d{2}|'
                               r'8[ ]?[| |\(|-]?\d{3}[| |\)|-][ ]?\d{3}[| |-]?\d{2}[| |-]?\d{2}') # Если писать [+7|8]... "+" Не включен в вывод
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return  ConversationHandler.END
    phoneNumbers = ''
    finds[ID] = phoneNumberList
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i + 1}. {phoneNumberList[i]}\n'
    update.message.reply_text(phoneNumbers)
    update.message.reply_text("Записать найденные номера в базу данных?")
    return 'findPhoneNumbers_db'

def findPhoneNumbers_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == ('да' or 'yes'):
        try:
            connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD,
                                          host=DB_HOST, port=DB_PORT, database=DATABASE)
            cursor = connection.cursor()
            data = 'INSERT INTO phone_nums (phone) VALUES '
            for i in finds[ID]:
                data += "('" + i + "'),"
            data = data[:-1] + ';'
            cursor.execute(data)
            connection.commit()
            update.message.reply_text("Успешно, записано")
            logging.info("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    return ConversationHandler.END

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронных почт: ')
    return 'findEmails'

def findEmails(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'[\w|\d]+@\w+\.\w+')
    emailList = emailRegex.findall(user_input)
    if not emailList:
        update.message.reply_text('Не найденно ни одной почты')
        return  ConversationHandler.END
    emails = ''
    finds[ID] = emailList
    for i in range(len(emailList)):
        emails += f'{i + 1}. {emailList[i]}\n'
    update.message.reply_text(emails)
    update.message.reply_text("Записать найденные почты в базу данных?")
    return 'findEmails_db'

def findEmails_db(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == ('да' or 'yes'):
        try:
            connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD,
                                          host=DB_HOST, port=DB_PORT, database=DATABASE)
            cursor = connection.cursor()
            data = 'INSERT INTO emails (email) VALUES '
            for i in finds[ID]:
                data += "('" + i + "'),"
            data = data[:-1] + ';'
            cursor.execute(data)
            connection.commit()
            update.message.reply_text("Успешно, записано")
            logging.info("Запись почты успешно выполнена")
        except (Exception, Error) as error:
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")
    return ConversationHandler.END

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите текст для проверки пароля: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(r'(?=\S*[!@#$%^&*()])(?=\S*[A-Z])(?=\S*[a-z])(?=\S*[0-9])[!@#$%^&*()A-Za-z0-9]{8,}')
    password = passwordRegex.search(user_input)
    if not password:
        update.message.reply_text('Пароль простой')
        return  ConversationHandler.END
    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END

def get_release(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('cat /etc/*-release')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_uname(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_uptime(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_df(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_free(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_mpstat(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_w(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_auths(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('last -10')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_critical(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('journalctl -p crit -n 5')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_ps(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)
def get_ss(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command(f'ss')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    data_splited = [data[i:i + 4096] for i in range(0, len(data), 4096)]
    for text in data_splited:
        update.message.reply_text(text)

def get_apt_list_command(update: Update, context):
    update.message.reply_text('Ведите название пакета для получения информации о ней или введите "-" для получения списка пакетов ')
    return 'get_apt_list'
def get_apt_list(update: Update, context):
    user_input = update.message.text
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    if user_input != "-":
        stdin, stdout, stderr = client.exec_command(f'apt show {user_input}')
    else:
        stdin, stdout, stderr = client.exec_command(f'apt list')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    data_splited = [data[i:i + 4096] for i in range(0, len(data), 4096)]
    for text in data_splited[:3]:
        update.message.reply_text(text)
    return ConversationHandler.END
def get_services(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command('systemctl list-units -t service -q')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    data_splited = [data[i:i + 4096] for i in range(0, len(data), 4096)]
    for text in data_splited:
        update.message.reply_text(text)

def get_repl_logs(update: Update, context):
    client.connect(hostname=HOST, username=USER, password=PASSWORD, port=PORT)
    stdin, stdout, stderr = client.exec_command(f'echo {PASSWORD} | sudo -S docker logs db')
    data = stdout.read() + stderr.read()
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    data_splited = [data[i:i + 4096] for i in range(0, len(data), 4096)]
    for text in data_splited:
        update.message.reply_text(text)

def get_emails(update: Update, context):
    try:
        connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM emails;")
        data = cursor.fetchall()
        data = '\n'.join([f'id = {el[0]}, email = {el[1]}' for el in data])
        update.message.reply_text(data)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

def get_phone_numbers(update: Update, context):
    try:
        connection = psycopg2.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM phone_nums;")
        data = cursor.fetchall()
        data = '\n'.join([f'id = {el[0]}, phone = {el[1]}' for el in data])
        update.message.reply_text(data)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'findPhoneNumbers_db': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers_db)],
        },
        fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmails', findEmailsCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'findEmails_db': [MessageHandler(Filters.text & ~Filters.command, findEmails_db)],
        },
        fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )

    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerAptList)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    dp.add_handler(CommandHandler('get_release', get_release))
    dp.add_handler(CommandHandler('get_uname', get_uname))
    dp.add_handler(CommandHandler('get_uptime', get_uptime))
    dp.add_handler(CommandHandler('get_df', get_df))
    dp.add_handler(CommandHandler('get_free', get_free))
    dp.add_handler(CommandHandler('get_mpstat', get_mpstat))
    dp.add_handler(CommandHandler('get_w', get_w))
    dp.add_handler(CommandHandler('get_auths', get_auths))
    dp.add_handler(CommandHandler('get_critical', get_critical))
    dp.add_handler(CommandHandler('get_ps', get_ps))
    dp.add_handler(CommandHandler('get_ss', get_ss))
    dp.add_handler(CommandHandler('get_services', get_services))

    dp.add_handler(CommandHandler('get_repl_logs', get_repl_logs))
    dp.add_handler(CommandHandler('get_emails', get_emails))
    dp.add_handler(CommandHandler('get_phone_numbers', get_phone_numbers))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
