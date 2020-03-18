#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using nested ConversationHandlers.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, GENERAL, EMERGENCY, DESCRIBING_SELF = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER, SELECTING_NATIONALITY = map(chr, range(5, 8))
SELECTING_IDENTIFICATION, SELECTING_AGE = map(chr, range(8, 10))
SELECTING_MOBILE_NUMBER, SELECTING_LOCATION, SELECTING_INFO = map(chr, range(10, 13))
# State definitions for descriptions conversation
SELECTING_FIELD, SELECTING_EMERGENCY, TYPING = map(chr, range(13, 16))
# Meta states
STOPPING, SHOWING = map(chr, range(16, 18))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(SELF, GENDER, MALE, FEMALE, AGE, NAME, SURNAME, NATIONALITY, IDENTIFICATION, SA_ID, PASSPORT, MOBILE_NUMBER,
 LOCATION, START_OVER, FIELDS, CURRENT_FIELD, CURRENT_LEVEL) = map(chr, range(18, 35))

INFO_LEVEL, CAPTURING, ADD = map(chr, range(35, 38))


# Top level conversation callbacks
def start(update, context):
    """Select an action: Adding parent/child or show data."""
    text = "Please confirm the main reason for making contact?"
    buttons = [[
        InlineKeyboardButton(text='GENERAL', callback_data=str(GENERAL)),
        InlineKeyboardButton(text='EMERGENCY', callback_data=str(EMERGENCY))
    ], [
        InlineKeyboardButton(text='Exit', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need do send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text("Hi there. My name is XXX Bot.\n" +
            "I'm your virtual assistant and work in the Chatbot Community Contact Centre.\n" +
            "I'll be assisting you with Identity & Personal Information " +
            "management and then hand you over to my human friend, " +
            "Agent001: XXX, who will assist you further.\n\n" +
            "In order to assist you, please confirm your basic identity.")
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def general_selected(update, context):
    """Choose to capture, show or go back"""
    text = 'Choose below to capture or show your info.'
    buttons = [[
        InlineKeyboardButton(text='Start Capturing', callback_data=str(CAPTURING))
    ], [
        InlineKeyboardButton(text='Show Your Info', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='<< Go Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return INFO_LEVEL


def emergency_selected(update, context):
    """Add information about youself."""
    context.user_data[CURRENT_LEVEL] = SELF
    text = 'Okay, for an EMERGENCY click on the below link:\n -> @LAIOCommunityCBCEmergencyBot'
    update.callback_query.edit_message_text(text=text)

    return END


def capture_info(update, context):
    """Add information about youself."""
    #context.user_data[CURRENT_LEVEL] = SELF
    text = 'Okay, please provide information about yourself.'
    button = InlineKeyboardButton(text='Add info', callback_data=str(ADD))
    keyboard = InlineKeyboardMarkup.from_button(button)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return DESCRIBING_SELF


def show_data(update, context):
    """Pretty print gathered data."""
    def prettyprint(user_data, level):
        people = user_data.get(level)
        if not people:
            return '\nNo information yet.'

        text = ''
        if level == SELF:
            for person in user_data[level]:
                text += '\nName: {0}, Age: {1}'.format(person.get(NAME, '-'), person.get(AGE, '-'))
        else:
            male, female = _name_switcher(level)

            for person in user_data[level]:
                gender = female if person[GENDER] == FEMALE else male
                text += '\n{0}: Name: {1}, Age: {2}'.format(gender, person.get(NAME, '-'),
                                                            person.get(AGE, '-'))
        return text

    ud = context.user_data
    text = 'Yourself:' + prettyprint(ud, SELF)
    text += '\n\nParents:' + prettyprint(ud, NATIONALITY)
    text += '\n\nChildren:' + prettyprint(ud, IDENTIFICATION)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True

    return SHOWING


def stop(update, context):
    """End Conversation by command."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.message.reply_text(text)

    return END


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.callback_query.edit_message_text(text=text)

    return END


# Second level conversation callbacks
def info_level(update, context):
    """Choose to capture, show or go back"""
    text = 'Choose below to show the captured info or go back to the top level.'
    buttons = [[
        InlineKeyboardButton(text='Start Capturing', callback_data=str(NATIONALITY))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='<< Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_ACTION


def select_level(update, context):
    """Choose to add a parent or a child."""
    text = 'You may add a parent or a child. Also you can show the gathered data or go back.'
    buttons = [[
        InlineKeyboardButton(text='Add parent', callback_data=str(NATIONALITY)),
        InlineKeyboardButton(text='Add child', callback_data=str(IDENTIFICATION))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL


def select_gender(update, context):
    """Choose to add mother or father."""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    text = 'Please choose, whom to add.'

    male, female = _name_switcher(level)

    buttons = [[
        InlineKeyboardButton(text='Add ' + male, callback_data=str(MALE)),
        InlineKeyboardButton(text='Add ' + female, callback_data=str(FEMALE))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_GENDER


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


# Third level callbacks
def select_field(update, context):
    """Select a FIELD to update for the person."""
    buttons = [[
        InlineKeyboardButton(text='Name', callback_data=str(NAME)),
        InlineKeyboardButton(text='Surname', callback_data=str(SURNAME)),
        ], [
        InlineKeyboardButton(text='Nationality', callback_data=str(NATIONALITY)),
        InlineKeyboardButton(text='Identification', callback_data=str(IDENTIFICATION)),
        ], [
        InlineKeyboardButton(text='Mobile Number', callback_data=str(MOBILE_NUMBER)),
        InlineKeyboardButton(text='Location', callback_data=str(LOCATION)),
        ], [
        InlineKeyboardButton(text='Age', callback_data=str(AGE)),
        InlineKeyboardButton(text='Gender', callback_data=str(GENDER)),
        ], [
        InlineKeyboardButton(text='Done', callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect FIELDs for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FIELDS] = {GENDER: update.callback_query.data}
        text = 'Please select a field to update.'
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Got it! Please select a field to update.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FIELD


def ask_for_input(update, context):
    """Prompt user to input data for selected FIELD."""
    context.user_data[CURRENT_FIELD] = update.callback_query.data
    text = 'Okay, please write and send the information'
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_input(update, context):
    """Save input for FIELD and return to FIELD selection."""
    ud = context.user_data
    ud[FIELDS][ud[CURRENT_FIELD]] = update.message.text

    ud[START_OVER] = True

    return select_field(update, context)


def end_describing(update, context):
    """End gathering of FIELDs and return to parent conversation."""
    ud = context.user_data
    level = ud[CURRENT_LEVEL]
    if not ud.get(level):
        ud[level] = []
    ud[level].append(ud[FIELDS])

    # Print upper level menu
    if level == SELF:
        ud[START_OVER] = True
        start(update, context)
    else:
        select_level(update, context)

    return END


def stop_nested(update, context):
    """Completely end conversation from within nested conversation."""
    update.message.reply_text("Thank you for chatting to us! We'll get back to you shortly. " +
        "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx")

    return STOPPING


# Error handler
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1080497761:AAHCDuZrkPp-WHeWR5jXujDFf8sbIKabhrA", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set up third level ConversationHandler (collecting FIELDS)
    capture_info_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_field, pattern='^' + str(ADD) + '$')],
        states={
            SELECTING_FIELD: [CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$')],
            TYPING: [MessageHandler(Filters.text, save_input)],
        },
        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],
        map_to_parent={
            # Return to second level menu
            END: CAPTURING,
            # End conversation alltogether
            STOPPING: STOPPING,
        }
    )

    # Set up second level ConversationHandler (adding a person)
    info_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(capture_info, pattern='^' + str(CAPTURING) + '$'),
                      CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$')],
        states={
            DESCRIBING_SELF: [capture_info_conv],
        },
        fallbacks=[
            CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],
        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: END,
        }
    )

    # Set up top level ConversationHandler (selecting action)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ACTION: [
                info_conv,
                CallbackQueryHandler(general_selected, pattern='^' + str(GENERAL) + '$'),
                CallbackQueryHandler(emergency_selected, pattern='^' + str(EMERGENCY) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
            ],
            INFO_LEVEL: [info_conv],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )
    # Because the states of the third level conversation map to the ones of the
    # second level conversation, we need to be a bit hacky about that:
    #conv_handler.states[DESCRIBING_SELF] = conv_handler.states[SELECTING_ACTION]
    #conv_handler.states[STOPPING] = conv_handler.entry_points

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
