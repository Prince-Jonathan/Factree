from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters,  InlineQueryHandler
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
import logging

updater = Updater(token='5089975823:AAFthd-y5fQyvlpZ5Ocg1iBVx-EUfKqw4pQ', use_context=True)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
#simple command function
def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

#implementing command handling
start_handler = CommandHandler('start', start)


#simple echo function
def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I don't understand what you mean by:\n" + update.message.text)

#implementing echo handling
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)


#receiving command arguments and converting to caps
def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

#implementing caps handler
caps_handler = CommandHandler('caps', caps)

#implementing inline commands
def inline_caps(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

#implementing caps handler
inline_caps_handler = InlineQueryHandler(inline_caps)

#implementing default (unknown)
def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

#implementing unknown handler
unknown_handler = MessageHandler(Filters.command, unknown)


dispatcher.add_handler(inline_caps_handler)
dispatcher.add_handler(caps_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()