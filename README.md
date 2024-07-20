
# TelegramBotManager

TelegramBotManager is a feature-rich Telegram bot designed to manage user interactions, send messages, and handle various media files. This bot includes admin functionalities for managing users and provides a robust set of commands for both regular users and administrators.

## Features

- User Management: Add, remove, and list users.
- Media Handling: Send and receive text, images, files, audio, and voice messages.
- Inline Keyboard Support: Interactive inline buttons for quick user responses.
- Admin Dashboard: Dedicated commands and features for administrators.
- Product Information: Retrieve and display product information and lists.

## Commands

### General Commands

- `/start`: Start the bot and display options.
- `/hi`: Say hi to the bot.
- `/hello`: Say hello to the bot.
- `/help`: Display help information.
- `/send_file`: Send a file to the user.
- `/send_image`: Send an image to the user.
- `/send_text`: Send a text message to the user.
- `/product_info`: Get information about a product.
- `/product_list`: List all available products.

### Admin Commands

- `/dashboard`: Access the admin dashboard.
- `/add_user`: Add a new user.
- `/remove_user`: Remove an existing user.
- `/list_users`: List all registered users.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/TelegramBotManager.git
   cd TelegramBotManager
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a directory for user-uploaded files:
   ```sh
   mkdir user_uploads
   ```

4. Set your Telegram bot token in the source code:
   ```python
   TOKEN = 'Your_Bot_Token'
   ```

5. Run the bot:
   ```sh
   python main.py
   ```

## Configuration

- Ensure you replace `'Your_Bot_Token'` with your actual Telegram bot token.
- Replace `Admin1`, `Admin2`, etc., with actual admin user IDs.

## Usage

- Start the bot using the `/start` command.
- Use the inline buttons or keyboard commands to interact with the bot.
- Admins can access additional commands by using the `/dashboard` command.

## Contributing

Feel free to fork this repository, create a feature branch, and submit pull requests. Any contributions are welcome!

## License

This project is licensed under the MIT License.
