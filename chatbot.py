## chatbot.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
# The messageHandler is used for all message updates
import configparser
import os
import logging
import firebase_admin
import omdb
from py_youtube import Search ,Data 

def main():
    # Load your token and create an Updater for your Bot
    omdb.set_default('apikey', '1bd45b7f')
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    # updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)

    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)

    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("movie", search_movie))
    dispatcher.add_handler(CommandHandler("search", search))
    dispatcher.add_handler(CommandHandler("youtube", search_youtube))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # To start the bot:
    updater.start_polling()
    updater.idle()

def search(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        raw = omdb.search_movie(context.args)
        keyboard = []
        for i in raw:
            #update.message.reply_text(i['title'])
            if '-' not in i['title']:
                keyboard.append([InlineKeyboardButton(i["title"], callback_data=i["title"])])
        update.message.reply_text('dead1')
        reply_markup = InlineKeyboardMarkup(keyboard)
        #update.message.reply_text(str(reply_markup))
        update.message.reply_text("Please select", reply_markup=reply_markup) 
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /search <keyword>')

def search_movie(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    
   ## raw = omdb.search_movie(context.args, fullplot=True, tomatoes=True)
    raw = omdb.get(title=context.args)
   #### for i in raw:
       ### update.message.reply_text(i['title'] + " plot: " + i['plot'])
    update.message.reply_text(raw['title'])
    update.message.reply_text(raw['plot'])
    update.message.reply_photo(raw['poster'])
    Title = ' '.join([str(elem) for elem in context.args])
    videos = Search(Title + " Trailer", limit = 1).videos()
    update.message.reply_text("https://youtu.be/" + str(videos[0]['id']))
   # update.message.reply_text(str(type(raw)))
    update.message.reply_text('Do you like the movie?:', 
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Like", callback_data='Like'),InlineKeyboardButton("Dislike", callback_data='Dislike')],[InlineKeyboardButton("No Comment", callback_data='No Comment')]]))
    update.message.reply_text(str(type(context.args)))

def search_movie(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    
   ## raw = omdb.search_movie(context.args, fullplot=True, tomatoes=True)
    raw = omdb.get(title=context.args)
   #### for i in raw:
       ### update.message.reply_text(i['title'] + " plot: " + i['plot'])
    update.message.reply_text(raw['title'])
    update.message.reply_text(raw['plot'])
    update.message.reply_photo(raw['poster'])
    Title = ' '.join([str(elem) for elem in context.args])
    videos = Search(Title + " Trailer", limit = 1).videos()
    update.message.reply_text("https://youtu.be/" + str(videos[0]['id']))
   # update.message.reply_text(str(type(raw)))
    update.message.reply_text('Do you like the movie?:', 
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Like", callback_data='Like'),InlineKeyboardButton("Dislike", callback_data='Dislike')],[InlineKeyboardButton("No Comment", callback_data='No Comment')]]))
    update.message.reply_text(str(type(context.args)))

def button(update: Updater, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    #search_movie(Updater, query.data)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data == 'Like':
        query.edit_message_text(text=f"Liked")
        context.bot.send_message(chat_id=update.effective_chat.id, text='Liked')
    elif query.data == 'Dislike':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Disiked')    
    else:
        raw = omdb.get(title=query.data)
        videos = Search(query.data + " Trailer", limit = 1).videos()
        
        query.edit_message_text(text=f"You selected: {query.data}")
        context.bot.send_message(chat_id=update.effective_chat.id, text=raw['plot'])
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=raw['poster'])
        context.bot.send_message(chat_id=update.effective_chat.id, text="https://youtu.be/" + str(videos[0]['id']))
        context.bot.send_message(chat_id=update.effective_chat.id, text='Do you like the movie?:', 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Like", callback_data='Like'),InlineKeyboardButton("Dislike", callback_data='Dislike')],[InlineKeyboardButton("No Comment", callback_data='No Comment')]]))
        
    #context.bot.send_message(chat_id=update.effective_chat.id, text=str(videos[0]['id']))
    
def search_youtube(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    videos = Search(context.args[0], limit = 3).videos()
    update.message.reply_text(str(videos))
    update.message.reply_text(context.args[0])
    
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)

if __name__ == '__main__':
    main()