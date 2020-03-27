#!/bin/sh
/bin/bash -c printenv > /home/"dir"/projects/LAIO-CCB/settings/env.txt
cd /home/"dir"/projects/LAIO-CCB/botArmy/identityBots/telegram
python3 basicIdentity.py
