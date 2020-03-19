#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
See Licence in project root
"""

import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Ensure that the below do not overlap
# State definitions for top level conversation
SELECTING_REASON, GENERAL, EMERGENCY = map(chr, range(3))
# State definitions for second level conversation
SELECTING_ACTION, SELECTING_FIELD, START_CAPTURE = map(chr, range(3, 6))
# State definitions for descriptions conversation
TYPING = map(chr, range(6, 7))
# Meta states
STOPPING, SHOWING, START_OVER = map(chr, range(7, 10))
# Different constants for this example
(SELF, FIELDS, NAME, SURNAME, NATIONALITY, IDENTIFICATION, SA_ID, PASSPORT,
 MOBILE_NUMBER, LOCATION, AGE, GENDER, GO_BACK, UPDATING_INFO, CURRENT_LEVEL, CURRENT_FIELD) = map(chr, range(10, 26))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END


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
    return SELECTING_REASON


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.callback_query.edit_message_text(text=text)

    return END


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


def end_third_level(update, context):
    """End gathering of fields and return to 2nd level conversation."""
    level = context.user_data[CURRENT_LEVEL]
    if not context.user_data.get(level):
        context.user_data[level] = []
    context.user_data[level].append(context.user_data[FIELDS])

    # Print upper level menu
    if level == SELF:
        context.user_data[START_OVER] = True
        general_reason(update, context)

    return END


def stop(update, context):
    """End Conversation by command."""
    text = "Thank you for chatting to us! We'll get back to you shortly. " + \
           "\nIn the event of an emergency, please contact the NDOH National Corona Hotline on xxxx xxx xxxx"
    update.message.reply_text(text)

    return END


def emergency_reason(update, context):
    """EMERGENCY was chosen. Go to EMERGENCY Bot."""
    text = 'Okay, for an EMERGENCY click on the below link:\n -> @LAIOCommunityCBCEmergencyBot'
    update.callback_query.edit_message_text(text=text)

    return END

# Second level callbacks
def general_reason(update, context):
    """Choose to capture, show or go back"""
    text = 'Choose below to capture or show your info.'
    buttons = [[
        InlineKeyboardButton(text='Start Capturing', callback_data=str(SELECTING_FIELD))
    ], [
        InlineKeyboardButton(text='Show Your Info', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='<< Go Back', callback_data=str(END))
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

        text = ''
        if level == SELF:
            for person in user_data[level]:
                text += '\nName: {0}, Age: {1}'.format(person.get(NAME, '-'), person.get(AGE, '-'))

        return text

    ud = context.user_data
    text = prettyprint(ud, SELF)

    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True

    return SHOWING


# Third level callbacks
def select_field(update, context):
    """Select a FIELD to update for the person."""
    buttons = [[
        InlineKeyboardButton(text='Q1: Name', callback_data=str(NAME)),
        InlineKeyboardButton(text='Q2: Surname', callback_data=str(SURNAME)),
        ], [
        InlineKeyboardButton(text='Q3: Nationality', callback_data=str(NATIONALITY)),
        InlineKeyboardButton(text='Q4: Identification', callback_data=str(IDENTIFICATION)),
        ], [
        InlineKeyboardButton(text='Q5: Mobile Number', callback_data=str(MOBILE_NUMBER)),
        InlineKeyboardButton(text='Q6: Location', callback_data=str(LOCATION)),
        ], [
        InlineKeyboardButton(text='Q7: Age', callback_data=str(AGE)),
        InlineKeyboardButton(text='Q8: Gender', callback_data=str(GENDER)),
        ], [
        InlineKeyboardButton(text='Done', callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FIELDS] = {}
        text = 'Please select a field to update.'
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Got it! Please select a field to update.'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return UPDATING_INFO


def ask_for_input(update, context):
    """Prompt user to input data for selected FIELD."""
    context.user_data[CURRENT_FIELD] = update.callback_query.data
    text = 'Okay, please write and send the information'
    update.callback_query.edit_message_text(text=text)

    return TYPING


def save_input(update, context):
    """Save input for FIELD and return to field selection."""
    context.user_data[FIELDS][context.user_data[CURRENT_FIELD]] = update.message.text

    context.user_data[START_OVER] = True

    return select_field(update, context)


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
    updater = Updater("1141194468:AAH7BF-EzQQpmzh7fo45uG1mU3FSxHBE6KI", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set up third level ConversationHandler (collecting FIELDS)
    capture_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_field, pattern='^' + str(SELECTING_FIELD) + '$')],
        states={
            UPDATING_INFO: [CallbackQueryHandler(ask_for_input, pattern='^(?!' + str(END) + ').*$'),
                            ],
            TYPING: [MessageHandler(Filters.text, save_input)],
        },
        fallbacks=[
            CallbackQueryHandler(end_third_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
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
                               CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$')],
        },
        fallbacks=[
            CommandHandler('stop', stop_nested)
        ],
        map_to_parent={
            # Return to top level menu
            END: SELECTING_REASON,
            # Return to second level menu
            #END: CAPTURING,
            # End conversation alltogether
            STOPPING: STOPPING,
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
    # Because the states of the third level conversation map to the ones of the
    # second level conversation, we need to be a bit hacky about that:
    #action_conv.states[UPDATING_INFO] = action_conv.states[SELECTING_ACTION]
    #action_conv.states[STOPPING] = action_conv.entry_points

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
