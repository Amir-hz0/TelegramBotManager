import asyncio
from datetime import datetime
import sqlite3
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import requests, os

TOKEN = 'Your_Bot_Token'

# Directory to save user-uploaded files
UPLOAD_DIR = 'user_uploads'

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db1():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db1()

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            city TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()


ADMIN_USER_IDS = [Admin1, Admin2]  # Replace with actual user IDs

categories = [
    {"name": "Products", "commands": [
        {"command": "product_info", "description": "Get information about a product"},
        {"command": "product_list", "description": "List of available products"}
    ]},
    {"name": "Orders", "commands": [
        {"command": "order_status", "description": "Check order status"},
        {"command": "order_history", "description": "View order history"}
    ]}
]

questions = [
    "What is your name?",
    "How old are you?",
    "Which city do you live in?"
]

# Store the current question index for each user
user_states = {}

commands = [
    {"command": "start", "description": "Start the bot"},
    {"command": "hi", "description": "Say hi to the bot"},
    {"command": "hello", "description": "Say hello to the bot"},
    {"command": "send_file", "description": "Send a file"},
    {"command": "dashboard", "description": "Open dashboard"},
    {"command": "add_user", "description": "Add a new user"},
    {"command": "remove_user", "description": "Remove an existing user"},
    {"command": "list_users", "description": "List all users"},
    {"command": "product_info", "description": "List product's info!"},
    {"command": "product_list", "description": "List all products!"},
]

# Inline buttons data
inline_buttons = [
    {"text": "Send Text", "callback_data": "send_text"},
    {"text": "Send Image", "callback_data": "send_image"},
    {"text": "Send File", "callback_data": "send_file"},
    {"text": "Help", "callback_data": "show_help"},
]

# Keyboard buttons data for non-admin users
keyboard_buttons = [
    {"text": "/start"},
    {"text": "/hi"},
    {"text": "/hello"},
    {"text": "/help"},
    {"text": "/send_text"},
    {"text": "/send_image"},
    {"text": "/send_file"},
    {"text": "/dashboard"},
    {"text": "/product_info"},
    {"text": "/product_list"},
]

admin_keyboard_buttons = [
    {"text": "/add_user"},
    {"text": "/remove_user"},
    {"text": "/list_users"},
]

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Inline buttons
    inline_keyboard = [
        [InlineKeyboardButton(button["text"], callback_data=button["callback_data"]) for button in inline_buttons]
    ]
    inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)

    # Keyboard buttons
    reply_keyboard = [[KeyboardButton(button["text"])] for button in keyboard_buttons]
    
    # If user is an admin, add admin-specific buttons
    if is_admin(user_id):
        reply_keyboard.extend([[KeyboardButton(button["text"])] for button in admin_keyboard_buttons])

    reply_keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text('Choose an option:', reply_markup=inline_reply_markup)
    await update.message.reply_text('Or use the keyboard buttons:', reply_markup=reply_keyboard_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'hi':
        await reply_hi(update, context)
    elif query.data == 'hello':
        await reply_hello(update, context)
    elif query.data == 'send_text':
        await query.message.reply_text('Here is your text message!')
    elif query.data == 'send_image':
        category = 'nature'
        api_url = 'https://api.api-ninjas.com/v1/randomimage?category={}'.format(category)
        response = requests.get(api_url, headers={'X-Api-Key': 'Your-Api', 'Accept': 'image/jpg'}, stream=True)
        if response.status_code == requests.codes.ok:
            await query.message.reply_photo(photo=response.content)
    elif query.data == 'send_file':
        dir_path = os.path.dirname(__file__)
        file_path = os.path.join(dir_path,"Your_file_path")
        try:
            with open(file_path, 'rb') as file:
                await query.message.reply_document(file)
        except FileNotFoundError:
            await query.message.reply_text('File not found.')

# Send image to user
async def send_image(update: Update, context: CallbackContext) -> None:
    category = 'nature'
    api_url = 'https://api.api-ninjas.com/v1/randomimage?category={}'.format(category)
    response = requests.get(api_url, headers={'X-Api-Key': 'Your-Api', 'Accept': 'image/jpg'}, stream=True)
    if response.status_code == requests.codes.ok:
        await update.message.reply_photo(photo=response.content)

# Send text to user
async def send_text(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Here is your text message!')

# Handle document from user
async def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    file = await context.bot.get_file(document.file_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{document.file_name}")
    try:
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'File saved to {file_path}')
    except Exception as e:
        await update.message.reply_text(f'Error saving file: {e}')

# Handle photo
async def handle_photo(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_photo.jpg")
    try:
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'Photo saved to {file_path}')
    except Exception as e:
        await update.message.reply_text(f'Error saving photo: {e}')

# Handle audio
async def handle_audio(update: Update, context: CallbackContext) -> None:
    audio = update.message.audio
    file = await context.bot.get_file(audio.file_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_{audio.file_name}")
    try:
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'Audio saved to {file_path}')
    except Exception as e:
        await update.message.reply_text(f'Error saving audio: {e}')

# Handle voice
async def handle_voice(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(UPLOAD_DIR, f"{timestamp}_voice.ogg")
    try:
        await file.download_to_drive(file_path)
        await update.message.reply_text(f'Voice message saved to {file_path}')
    except Exception as e:
        await update.message.reply_text(f'Error saving voice message: {e}')


# Send file to user
async def send_file(update: Update, context: CallbackContext) -> None:
    dir_path = os.path.dirname(__file__)
    file_path = os.path.join(dir_path,"Your_file_path")
    try:
        with open(file_path, 'rb') as file:
            await update.message.reply_document(file)
    except FileNotFoundError:
        await update.message.reply_text('File not found.')


async def reply_to_user(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()
    if text == 'hello' and text == 'hi':
        await update.message.reply_text('Hello! What is your name?')
    elif text == 'how are you?':
        await update.message.reply_text('I am just a bot, but I am here to help you!')

async def reply_hi(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! What is your name?')

async def reply_hello(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hello! What is your name?')

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_response = update.message.text
    
    if user_id not in user_states:
        user_states[user_id] = {"question_index": 0, "data": {}}
    
    state = user_states[user_id]
    
    if state["question_index"] == 0:
        state["data"]["name"] = user_response
    elif state["question_index"] == 1:
        state["data"]["age"] = int(user_response)
    elif state["question_index"] == 2:
        state["data"]["city"] = user_response
    
    state["question_index"] += 1
    
    if state["question_index"] < len(questions):
        await update.message.reply_text(questions[state["question_index"]])
    else:
        save_user_data(user_id, state["data"])
        await update.message.reply_text("Thank you! Your information has been saved.")
        del user_states[user_id]

def save_user_data(user_id, data):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, name, age, city) VALUES (?, ?, ?, ?)
    ''', (user_id, data["name"], data["age"], data["city"]))
    conn.commit()
    conn.close()

async def set_bot_commands(application: Application) -> None:
    bot_commands = [BotCommand(cmd["command"], cmd["description"]) for cmd in commands]
    await application.bot.set_my_commands(bot_commands)

async def show_help(update: Update, context: CallbackContext) -> None:
    help_message = "Available commands:\n"
    
    for category in categories:
        help_message += f"\n<b>{category['name']}</b>:\n"
        for cmd in category["commands"]:
            help_message += f"/{cmd['command']} - {cmd['description']}\n"
    
    # Send the HTML-formatted message
    await update.message.reply_html(help_message)

async def product_info(update: Update, context: CallbackContext) -> None:
    # Example: Send product information
    product_id = '123'
    product_name = 'Example Product'
    product_description = 'This is a detailed description of the example product.'
    await update.message.reply_html(f"<b>Product ID:</b> {product_id}\n<b>Name:</b> {product_name}\n<b>Description:</b> {product_description}")

async def product_list(update: Update, context: CallbackContext) -> None:
    # Example: Send list of products
    products = [
        {"id": "123", "name": "Product A"},
        {"id": "456", "name": "Product B"},
        {"id": "789", "name": "Product C"}
    ]
    products_message = "Available Products:\n"
    for product in products:
        products_message += f"<b>{product['name']}</b> - /product_info_{product['id']}\n"
    
    await update.message.reply_html(products_message)

def is_admin(user_id):
    return user_id in ADMIN_USER_IDS

async def dashboard(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if is_admin(user_id):
        reply_keyboard = [[KeyboardButton(button["text"])] for button in admin_keyboard_buttons]
        reply_keyboard_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        await update.message.reply_text('Admin Panel:', reply_markup=reply_keyboard_markup)
    else:
        await update.message.reply_text('You do not have access to the admin panel.')

# Add user command handler
async def add_user(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Please send the user details in the format: name, age, city')

# Remove user command handler
async def remove_user(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Please send the user ID to remove')

async def list_users(update: Update, context: CallbackContext) -> None:
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, age, city FROM users')
    users = cursor.fetchall()
    conn.close()

    if users:
        users_message = "Registered Users:\n"
        for user in users:
            users_message += f"ID: {user[0]}, Name: {user[1]}, Age: {user[2]}, City: {user[3]}\n"
        await update.message.reply_text(users_message)
    else:
        await update.message.reply_text('No users found.')

def main() -> None:
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.Document.MP3, handle_audio))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler("product_info", product_info))
    application.add_handler(CommandHandler("product_list", product_list))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("send_file", send_file))
    application.add_handler(CommandHandler("send_image", send_image))
    application.add_handler(CommandHandler("send_text", send_text))
    application.add_handler(CommandHandler("hi", reply_hi))
    application.add_handler(CommandHandler("hello", reply_hello))
    application.add_handler(CommandHandler("dashboard", dashboard))
    application.add_handler(CommandHandler("add_user", add_user))
    application.add_handler(CommandHandler("remove_user", remove_user))
    application.add_handler(CommandHandler("list_users", list_users))

    set_bot_commands(application)

    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
