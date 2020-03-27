# LAIO-CCB
LAIO Community Chat Bots

## Prerequisites
Install the python-telegram-bot package. Details available at this [github](https://github.com/python-telegram-bot/python-telegram-bot)

```
pip install python-telegram-bot --upgrade
```

## Setup
To configure the bot token, replace the "token" key with the token as per @BotFather
```
nano ~/projects/LAIO-CCB/botArmy/identityBots/telegram/basicIdentity.json
```

## Installing
To setup the bot service

```
cd ~/projects/LAIO-CCB/settings
sudo cp bot.service /lib/systemd/system
/bin/bash -c printenv > ~/projects/LAIO-CCB/settings/env.txt
sudo systemctl enable bot.service
sudo systemctl start bot.service
```

Verify that the service is running
```
sudo systemctl status bot.service
```