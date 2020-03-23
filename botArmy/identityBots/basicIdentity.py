#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
See License in project root folder
"""

import logging
import json

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram import (KeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# # Assign Unicode character for USER DATA keys - Difficult to debug, but faster
# # Ensure that the below do not overlap
# # State definitions for top level conversation
# SELECTING_REASON, GENERAL, EMERGENCY = map(chr, range(3))
# # State definitions for second level conversation
# SELECTING_ACTION, SELECTING_FIELD, START_CAPTURE = map(chr, range(3, 6))
# # State definitions for descriptions conversation
# TYPING = map(chr, range(6, 7))
# # Meta states
# STOPPING, SHOWING, START_OVER = map(chr, range(7, 10))
# # Different constants for this example
# (SELF, FIELDS, NAME, SURNAME, NATIONALITY, IDENTIFICATION, SA_ID, PASSPORT,
#  MOBILE_NUMBER, LOCATION, AGE, GENDER, GO_BACK, UPDATING_INFO, CURRENT_LEVEL, CURRENT_FIELD) = map(chr, range(10, 26))
# # Shortcut for ConversationHandler.END
# END = ConversationHandler.END

# Assign NAMED keys for USER_DATA keys - Easier to debug, but not great for processing load
# Ensure that the below do not overlap
# State definitions for top level conversation
SELECTING_REASON = "SELECTING_REASON"
GENERAL = "GENERAL"
EMERGENCY = "EMERGENCY"
# State definitions for second level conversation
SELECTING_ACTION = "SELECTING_ACTION"
SELECTING_FIELD = "SELECTING_FIELD"
START_CAPTURE = "START_CAPTURE"
SUBMIT = "SUBMIT"
# State definitions for descriptions conversation
TYPING = "TYPING"
CHOOSING = "CHOOSING"
# Meta states
STOPPING = "STOPPING"
SHOWING = "SHOWING"
START_OVER = "START_OVER"
# Different constants for this example
SELF = "SELF"
FIELDS = "FIELDS"
NAME = "NAME"
SURNAME = "SURNAME"
AGE = "AGE"
GENDER = "GENDER"
NATIONALITY = "NATIONALITY"
IDENTIFICATION = "IDENTIFICATION"
SA_ID = "SA_ID"
PASSPORT = "PASSPORT"
MOBILE_NUMBER = "MOBILE_NUMBER"
LOCATION = "LOCATION"
# GO_BACK = "GO_BACK"
UPDATING_INFO = "UPDATING_INFO"
CURRENT_LEVEL = "CURRENT_LEVEL"
CURRENT_FIELD = "CURRENT_FIELD"

# MALE = "MALE"
# FEMALE = "FEMALE"
# OTHER_GEN = "OTHER_GEN"
# PREFER_NO_GEN = "PREFER_NO_GEN"

f = open("../config/bots/basicIdentity.json", "r")
bot_menus = json.loads(f.read())
f.close()
f = open("../config/country.json", "r")
nationality_dict = json.loads(f.read())
f.close()
f = open("../config/gender.json", "r")
gender_dict = json.loads(f.read())
f.close()
f = open("../config/identification_type.json", "r")
id_type_dict = json.loads(f.read())
f.close()

# Shortcut for ConversationHandler.END
END = ConversationHandler.END


# Top level conversation callbacks
def start(update, context):
    """Select an action: Adding parent/child or show data."""
    text = "Please confirm the main reason for making contact? ↴"
    buttons = [[
        InlineKeyboardButton(text=bot_menus["level-1"]["Q1"], callback_data=str(GENERAL)),
        InlineKeyboardButton(text=bot_menus["level-1"]["Q2"], callback_data=str(EMERGENCY))
    ], [
        InlineKeyboardButton(text=bot_menus["level-1"]["Q3"], callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need do send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(
            "Hi there. My name is XXX Bot.\n" +
            "I'm your virtual assistant and work in the Chatbot Community Contact Centre.\n" +
            "I'll be assisting you with Identity & Personal Information " +
            "management and then hand you over to my human friend, " +
            "Agent001: XXX, who will assist you further.\n\n" +
            "In order to assist you, please confirm your basic identity by navigating through the options below."
            )
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_REASON


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.callback_query.edit_message_text(text=text)

    return END


def stop(update, context):
    """End Conversation by command."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.message.reply_text(text)

    return END


def stop_nested(update, context):
    """Completely end conversation from within nested conversation."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=None)

    return STOPPING


def emergency_reason(update, context):
    """EMERGENCY was chosen. Go to EMERGENCY Bot."""
    text = 'Okay, for an EMERGENCY click on the below link:\n -> @LAIOCommunityCBCEmergencyBot'
    update.callback_query.edit_message_text(text=text)

    return END


# Second level callbacks
def general_reason(update, context):
    """Choose to capture, show or go back"""
    text = 'Choose below to capture or show your information ↴'
    buttons = [[
        InlineKeyboardButton(text=bot_menus["level-2"]["Q1"], callback_data=str(SELECTING_FIELD))
    ], [
        InlineKeyboardButton(text=bot_menus["level-2"]["Q2"], callback_data=str(END)),
        InlineKeyboardButton(text=bot_menus["level-2"]["Q3"], callback_data=str(SHOWING))
    ], [
        InlineKeyboardButton(text=bot_menus["level-2"]["Q4"], callback_data=str(SUBMIT))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    # Only 1 Level to capture info for 1 User
    context.user_data[CURRENT_LEVEL] = SELF
    # Do not display the startup message..
    context.user_data[START_OVER] = False

    return SELECTING_ACTION


def show_data(update, context):
    """Pretty print gathered information."""
    # Nested function to renturn a pretty string of text containing all information
    def prettyprint(user_data, level):
        people = user_data.get(level)
        if not people:
            return '\nNo information yet.'

        r_text = 'Captured Info\n'
        r_text += '=============\n\n'
        if level == SELF:
            r_text += 'Name: {0}\n'.format(user_data[level].get(NAME, '-'))
            r_text += 'Surname: {0}\n'.format(user_data[level].get(SURNAME, '-'))
            r_text += 'Age: {0}\n'.format(user_data[level].get(AGE, '-'))
            r_text += 'Gender: {0}\n'.format(user_data[level].get(GENDER, '-'))
            r_text += 'Nationality: {0}\n'.format(user_data[level].get(NATIONALITY, '-'))
            r_text += 'Identification type: {0}\n'.format(user_data[level].get(IDENTIFICATION, '-'))
            r_text += 'ID: {0}\n'.format(user_data[level].get(SA_ID, '-'))
            r_text += 'Passport: {0}\n'.format(user_data[level].get(PASSPORT, '-'))
            r_text += 'Mobile number: {0}\n'.format(user_data[level].get(MOBILE_NUMBER, '-'))
            r_text += 'Location(gps): {0}\n'.format(user_data[level].get(LOCATION, '-'))

        return r_text

    ud = context.user_data
    text = prettyprint(ud, SELF)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True

    print(context.user_data)

    return SHOWING


def send_mail(user_data, level, data_submit):
    import smtplib
    import ssl

    port = 465  # For SSL
    password = "laio#com"
    smtp_server = "smtp.yandex.com"
    sender_email = "laiocommunity@yandex.com"  # Enter your address
    receiver_email = "laiocommunity@yandex.com"  # Enter receiver address

    # Create a secure SSL context
    context = ssl.create_default_context()

    message = """\
            Subject: LAIO Community Bot - Basic Identity

            Capture Data:"""

    message += str(data_submit)

    message += '\n\nName: {0}\n'.format(user_data[level].get(NAME, '-'))
    message += 'Surname: {0}\n'.format(user_data[level].get(SURNAME, '-'))
    message += 'Age: {0}\n'.format(user_data[level].get(AGE, '-'))
    message += 'Gender: {0}\n'.format(user_data[level].get(GENDER, '-'))
    message += 'Nationality: {0}\n'.format(user_data[level].get(NATIONALITY, '-'))
    message += 'Identification type: {0}\n'.format(user_data[level].get(IDENTIFICATION, '-'))
    message += 'ID: {0}\n'.format(user_data[level].get(SA_ID, '-'))
    message += 'Passport: {0}\n'.format(user_data[level].get(PASSPORT, '-'))
    message += 'Mobile number: {0}\n'.format(user_data[level].get(MOBILE_NUMBER, '-'))
    message += 'Location(gps): {0}\n'.format(user_data[level].get(LOCATION, '-'))

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def submit_info(update, context):
    """Submit gathered information."""
    # Nested function to renturn a pretty string of text containing all information
    def prettyprint(user_data, level):
        people = user_data.get(level)
        if not people:
            return '\nNo information yet. Exiting..'

        r_text = 'Submitting your Info. Exiting..\n'

        data_submit = {}
        if level == SELF:
            # for person in user_data[level]:
            #     text += '\nName: {0}, Age: {1}'.format(person.get(NAME, '-'), person.get(AGE, '-'))
            data_submit["name"] = '{0}'.format(user_data[level].get(NAME, '-'))
            data_submit["surname"] = '{0}'.format(user_data[level].get(SURNAME, '-'))
            data_submit["age"] = '{0}'.format(user_data[level].get(AGE, '-'))
            data_submit["gender"] = '{0}'.format(user_data[level].get(GENDER, '-'))
            data_submit["nationality"] = '{0}'.format(user_data[level].get(NATIONALITY, '-'))
            data_submit["identification_type"] = '{0}'.format(user_data[level].get(IDENTIFICATION, '-'))
            data_submit["sa_id_number"] = '{0}'.format(user_data[level].get(SA_ID, '-'))
            data_submit["passport"] = '{0}'.format(user_data[level].get(PASSPORT, '-'))
            data_submit["mobile_number"] = '{0}'.format(user_data[level].get(MOBILE_NUMBER, '-'))
            if user_data[level].get(LOCATION) and not None:
                gps_c = user_data[level].get(LOCATION)
                data_submit["location"] = {"latitude": gps_c["latitude"],
                                           "longitude": gps_c["longitude"]}
            else:
                data_submit["location"] = {}

        #send_mail(user_data, level, data_submit)

        return r_text

    ud = context.user_data
    text = prettyprint(ud, SELF)

    update.callback_query.edit_message_text(text=text, reply_markup=None)
    ud[START_OVER] = False

    return stop_nested(update, context)


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


# Third level callbacks
def select_field(update, context):
    """Select a FIELD to update for the person."""
    def check_done(user_data, key):
        item = ""
        if key in user_data:
            item = " ✅"

        return item

    level = context.user_data[CURRENT_LEVEL]
    # If there is no key, then create one, this should only happen once
    if not context.user_data.get(level):
        context.user_data[level] = {}

    ud = context.user_data[level]
    print(context.user_data)

    buttons = [[
        InlineKeyboardButton(text=bot_menus["level-3"]["Q1"] + check_done(ud, NAME),
                             callback_data=str(NAME)),
        InlineKeyboardButton(text=bot_menus["level-3"]["Q2"] + check_done(ud, SURNAME),
                             callback_data=str(SURNAME)),
        ], [
        InlineKeyboardButton(text=bot_menus["level-3"]["Q3"] + check_done(ud, AGE),
                             callback_data=str(AGE)),
        InlineKeyboardButton(text=bot_menus["level-3"]["Q4"] + check_done(ud, GENDER),
                             callback_data=str(GENDER)),
        ], [
        InlineKeyboardButton(text=bot_menus["level-3"]["Q5"] + check_done(ud, MOBILE_NUMBER),
                             callback_data=str(MOBILE_NUMBER)),
        InlineKeyboardButton(text=bot_menus["level-3"]["Q6"] + check_done(ud, LOCATION),
                             callback_data=str(LOCATION)),
        ], [
        InlineKeyboardButton(text=bot_menus["level-3"]["Q7"] + check_done(ud, NATIONALITY),
                             callback_data=str(NATIONALITY)),
        InlineKeyboardButton(text=bot_menus["level-3"]["Q8"] + check_done(ud, IDENTIFICATION),
                             callback_data=str(IDENTIFICATION)),
        ], [
        InlineKeyboardButton(text=bot_menus["level-3"]["Q9"],
                             callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        #context.user_data[FIELDS] = {}
        text = 'Please complete all the questions. Select the specific question to update it. ' + \
               'If you made a mistake, please select the question again to correct ↴'
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = "👍Thank you."
        update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
        text = 'Please select a question to update ↴'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return UPDATING_INFO


def ask_for_input(update, context):
    """Prompt user to input data for selected FIELD."""
    context.user_data[CURRENT_FIELD] = update.callback_query.data

    if update.callback_query.data == GENDER:
        text = 'Okay, please write and send your answer.'
        update.callback_query.edit_message_text(text=text, reply_markup=None)
        reply_keyboard = gender_dict["gender"]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'You can choose your gender from the provided buttons'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)

    elif update.callback_query.data == NATIONALITY:
        text = 'Okay, please write and send your answer'
        update.callback_query.edit_message_text(text=text, reply_markup=None)
        reply_keyboard = []
        for nation in nationality_dict:
            if nation["name"] == "South Africa":
                reply_keyboard.insert(0, [nation["name"]])
            reply_keyboard.append([nation["name"]])

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'You can choose your nationality from the provided buttons'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)

    elif update.callback_query.data == IDENTIFICATION:
        text = 'Okay, please write and send your answer'
        update.callback_query.edit_message_text(text=text, reply_markup=None)
        reply_keyboard = id_type_dict["identification_type"]

        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'You can choose your identification type from the provided buttons'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)

        return CHOOSING

    elif update.callback_query.data == MOBILE_NUMBER:
        text = 'Okay, please write and send your answer.'
        update.callback_query.edit_message_text(text=text, reply_markup=None)

        reply_keyboard = [[KeyboardButton(text="Send my mobile number", request_contact=True)]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'Or you can choose to send your number from the provided button'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)

    elif update.callback_query.data == LOCATION:
        text = 'Okay, please send your location'
        update.callback_query.edit_message_text(text=text, reply_markup=None)

        reply_keyboard = [[KeyboardButton(text="Send my current location", request_location=True)]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        text = 'Or you can choose to send your current location from the provided button.\n' + \
               'Please use a GPS capable mobile phone to capture the location.'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=markup)

    else:
        text = 'Okay, please write and send your answer'
        update.callback_query.edit_message_text(text=text, reply_markup=None)

    return TYPING


def process_choice(update, context):
    """Save input for FIELD and return to field selection."""
    level = context.user_data[CURRENT_LEVEL]
    # If there is no key, then create one, this should only happen once
    if not context.user_data.get(level):
        context.user_data[level] = {}

    # Update the corresponding field in the key
    if context.user_data[CURRENT_FIELD] == IDENTIFICATION:
        if update.message.text == id_type_dict["identification_type"][0][0]:
            context.user_data[level][context.user_data[CURRENT_FIELD]] = update.message.text
            context.user_data[CURRENT_FIELD] = SA_ID
            text = 'Okay, please write and send your SA ID number'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardRemove())
        elif update.message.text == id_type_dict["identification_type"][0][1]:
            context.user_data[level][context.user_data[CURRENT_FIELD]] = update.message.text
            context.user_data[CURRENT_FIELD] = PASSPORT
            text = 'Okay, please write and send your Passport number'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardRemove())
        else:
            text = 'Sorry, I cannot process that information.'
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardRemove())
            context.user_data[START_OVER] = True

            return select_field(update, context)

    return TYPING


def save_input(update, context):
    """Save input for FIELD and return to field selection."""
    level = context.user_data[CURRENT_LEVEL]
    # If there is no key, then create one, this should only happen once
    if not context.user_data.get(level):
        context.user_data[level] = {}

    # Update the corresponding field in the key
    if context.user_data[CURRENT_FIELD] == MOBILE_NUMBER:
        context.user_data[level][context.user_data[CURRENT_FIELD]] = update.message.contact["phone_number"]
    elif context.user_data[CURRENT_FIELD] == LOCATION:
        context.user_data[level][context.user_data[CURRENT_FIELD]] = update.message.location
    else:
        context.user_data[level][context.user_data[CURRENT_FIELD]] = update.message.text

    # context.user_data[FIELDS][context.user_data[CURRENT_FIELD]] = update.message.text

    context.user_data[START_OVER] = True

    return select_field(update, context)


def end_third_level(update, context):
    """End gathering of fields and return to 2nd level conversation."""
    level = context.user_data[CURRENT_LEVEL]
    # Print upper level menu
    if level == SELF:
        context.user_data[START_OVER] = True
        general_reason(update, context)

    return END


# Error handler
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(bot_menus["token"], use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Setup nested conversation handlers starting at the deepest level
    # Set up third level ConversationHandler (collecting FIELDS)
    capture_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_field, pattern='^' + str(SELECTING_FIELD) + '$')],
        states={
            UPDATING_INFO: [CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$'), ],
            TYPING: [MessageHandler(Filters.text, save_input),
                     MessageHandler(Filters.contact, save_input),
                     MessageHandler(Filters.location, save_input), ],
            CHOOSING: [MessageHandler(Filters.text, process_choice), ],
        },
        fallbacks=[
            CallbackQueryHandler(end_third_level, pattern='^' + str(END) + '$'),
        ],
        map_to_parent={
            # Return to 2nd level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: END,
        }
    )

    # Set up second level ConversationHandler (selecting action)
    action_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(general_reason, pattern='^' + str(GENERAL) + '$')],
        states={
            SHOWING: [CallbackQueryHandler(general_reason, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: [capture_conv,
                               CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
                               CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
                               CallbackQueryHandler(submit_info, pattern='^' + str(SUBMIT) + '$')],
        },
        fallbacks=[
            CommandHandler('stop', stop)
        ],
        map_to_parent={
            STOPPING: END,
            # Return to top level menu
            END: SELECTING_REASON,
        }
    )

    # Set up top level ConversationHandler (selecting reason)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_REASON: [
                action_conv,
                CallbackQueryHandler(emergency_reason, pattern='^' + str(EMERGENCY) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            ],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    conv_handler.states[STOPPING] = conv_handler.entry_points
    # Add Handler to the dispatcher
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
