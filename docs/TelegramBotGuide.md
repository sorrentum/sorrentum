# Telegram Bot Guide

<!-- toc -->

- [Create a Telegram Bot](#create-a-telegram-bot)
- [Set Up Environment](#set-up-environment)
- [Get IDs](#get-ids)
- [Add / Remove](#add--remove)

<!-- tocstop -->

# Create a Telegram Bot:

- To create a Telegram bot, you need to interact with the BotFather on Telegram.
  Here are the steps:
  - Start a chat with BotFather on Telegram: https://t.me/botfather
  - Use the /newbot command to create a new bot and follow the instructions.
  - Once the bot is created, you will receive an API token. Save this token
    securely, as you'll need it later.

- Add Bot to Your Group:
  - Add the bot to the desired Telegram group and make sure it has admin
    privileges.

# Set Up Environment:

  - Store the bot's API token in an environment variable.
    ```bash
    export TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN
    ```

# Get IDs

- Get your Group ID:
  - Use get_telegram_groupid.py
    ```bash
    > python dev_scripts/get_telegram_groupid.py
    ```
- Get target user ID:

# Add / Remove

- To add/remove a user from the group, use the following command:
  ```bash
  > python process_telegram_collaborator.py --action <add/remove> --username <USERNAME> --groupid <GROUP_ID>
  ```
