## chatbot.py
from logging.handlers import RotatingFileHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
# The messageHandler is used for all message updates
import configparser
import os
import logging
import omdb
from py_youtube import Search ,Data

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import numpy as np 

def main():
    # Load your token and create an Updater for your Bot
    #omdb.set_default('apikey', os.environ['OMDB_APIKEY'])
    #config = configparser.ConfigParser()
    #config.read('config.ini')

    #TELEGRAM
    #updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)

    #FIREBASE
    cred = credentials.Certificate('firebase-adminsdk.json')
    #firebase_admin.initialize_app(cred, {
    #    'databaseURL': config['FIREBASE']['URL']
    #})
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ['FIREBASE_URL']
    })

    #OMDB
    #OMDB_API_KEY= '70dae977'
    omdb.set_default('apikey', os.environ['OMDB_API_KEY'])

    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    text_handler = MessageHandler(Filters.text & (~Filters.command), txt_msg)
    dispatcher.add_handler(text_handler)

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("search", search))
    dispatcher.add_handler(CommandHandler("toprate", toprate))
    dispatcher.add_handler(CommandHandler("contribute", contribute))
    dispatcher.add_handler(CommandHandler("recommend", recommend))
    dispatcher.add_handler(CommandHandler("comment", comment)) 
    dispatcher.add_handler(CommandHandler("help", help))    
    dispatcher.add_handler(CallbackQueryHandler(button))

    global comment_ind
    comment_ind = 0

    global rating_ind
    rating_ind = 0

    # To start the bot:
    updater.start_polling()
    updater.idle()

def listToString(s): 
    str1 = " "  
    return (str1.join(s))

def average(lst):
    return sum(lst) / len(lst)

def help(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        line1 = "/help" + "\n" + "- command list"
        line2 = "/search <keyword>" + "\n" + "- search movie"
        line3 = "/toprate" + "\n" + "- top 10 rated movie"
        line4 = "/contribute" + "\n" + "- most active commentator"
        line5 = "/recommend" + "\n" + "- movie recommendationa"
        line6 = "/comment" + "\n" + "- leave comment for movie"
        msg =  line1 + "\n" + line2 + "\n" + line3 + "\n" + line4 + "\n" + line5 + "\n" + line6
        context.bot.send_message(chat_id=update.effective_chat.id, text= msg)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /help <keyword>')

def toprate(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /toprate is issued."""
    try:
        ref = db.reference("/Rating/")
        rating_dict = ref.get()
        user_raing_avg = {}
        for k1, v1 in rating_dict.items():
            movieid = str(k1)
            movierate = []
            for k2, v2 in v1.items():
                movierate.append(list(v2.values())[0])
                movierate_avg = average(movierate)
                user_raing_avg[movieid] = movierate_avg
        sorted_user_raing_avg_keys = sorted(user_raing_avg, key=user_raing_avg.get, reverse=True)
        toprate_result = ''
        if len(sorted_user_raing_avg_keys) < 10:
            for k3 in sorted_user_raing_avg_keys:
                toprate_result += '\n' + k3 + ' : ' + str(user_raing_avg[k3])
        else:
            for k3 in sorted_user_raing_avg_keys[10:]:
                toprate_result += '\n' + k3 + ' : ' + str(user_raing_avg[k3])
        update.message.reply_text('Congratulation to our top 10 best rated movies. \n' + toprate_result)
    except (IndexError, ValueError):
        update.message.reply_text('No rated movie in our database! Please share your first movie rating.')

def contribute(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /contribute is issued."""
    try:
        ref = db.reference("/Comment/")
        comment_dict = ref.get()
        user_comment_count = {}
        for k1, v1 in comment_dict.items():
            for k2, v2 in v1.items():
                userid = list(v2.keys())[0]
                if userid not in user_comment_count.keys():
                    user_comment_count[userid] = 1
                elif userid in user_comment_count.keys():
                    user_comment_count[userid] += 1
        active_user = max(user_comment_count, key=user_comment_count.get)
        comment_vol = user_comment_count[active_user]
        update.message.reply_text('Congratulation to our most active user. \n' + active_user + ' has left ' + str(comment_vol) + ' comments.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /contribute <keyword>')

def recommend(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /recommend is issued."""
    try:
        ref = db.reference("/Rating/")
        rating_dict = ref.get()
        user_raing_avg = {}
        for k1, v1 in rating_dict.items():
            movieid = str(k1)
            movierate = []
            for k2, v2 in v1.items():
                movierate.append(list(v2.values())[0])
                movierate_avg = average(movierate)
                user_raing_avg[movieid] = movierate_avg
        sorted_user_raing_avg_keys = sorted(user_raing_avg, key=user_raing_avg.get, reverse=True)
        if len(sorted_user_raing_avg_keys) < 10:
            print(len(sorted_user_raing_avg_keys))
            randnbr=np.random.randint(1, len(sorted_user_raing_avg_keys))
            print(randnbr)
            rmd = sorted_user_raing_avg_keys[randnbr]
            #rmd = sorted_user_raing_avg_keys[randnbr] + ' : ' + str(user_raing_avg[sorted_user_raing_avg_keys[randnbr]])
        else:
            randnbr=np.random.randint(1,10)
            rmd = sorted_user_raing_avg_keys[10:][randnbr]
        update.message.reply_text('We recommend you check out \n' + rmd)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /recommend <keyword>')

def search(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        raw = omdb.search_movie(context.args)
        keyboard = []
        for i in raw:
            if '-' not in i['title']:
                keyboard.append([InlineKeyboardButton(i["title"], callback_data='1_1 '+i["title"])])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Please select", reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /search <keyword>')

def button(update: Updater, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query
    print(query.from_user.id)
    print(query.from_user['username'])
    print(query.from_user['first_name'])
    print(query.from_user['id'])
    query.answer()
    if query.data == 'Like':
        query.edit_message_text(text=f"Liked")
        context.bot.send_message(chat_id=update.effective_chat.id, text='Liked')
    elif query.data == 'Dislike':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Disiked')        
    elif query.data.split(" ",1)[0] == '1_1':
            global movie_chosen
            movie_chosen = query.data.split(" ",1)[1]
            context.bot.send_message(chat_id=update.effective_chat.id, text='Would you like to...', 
                reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("More Information", callback_data='1_2 Information'),InlineKeyboardButton("Leave Comment", callback_data='1_2 Comment')],[InlineKeyboardButton("Check Reviews", callback_data='1_2 Review'),InlineKeyboardButton("Give Rating", callback_data='1_2 Rating')]]))
    elif query.data.split(" ",1)[0] == '1_2':
        if query.data.split(" ",1)[1] == 'Information':
            raw = omdb.get(title=movie_chosen)
            videos = Search(movie_chosen + " Trailer", limit = 1).videos()
            query.edit_message_text(text=f"You selected: {movie_chosen}")
            context.bot.send_message(chat_id=update.effective_chat.id, text=raw['plot'])
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=raw['poster'])
            context.bot.send_message(chat_id=update.effective_chat.id, text="https://youtu.be/" + str(videos[0]['id']))
        #    context.bot.send_message(chat_id=update.effective_chat.id, text='Do you like the movie?:', 
        #        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Like", callback_data='Like'),InlineKeyboardButton("Dislike", callback_data='Dislike')]]))
        elif query.data.split(" ",1)[1] == 'Comment':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please leave comment')
            global comment_ind
            comment_ind = 1
        elif query.data.split(" ",1)[1] == 'Review':
            ref = db.reference("/Comment/" + movie_chosen + "/")
            comment_dict = ref.get()
            dict_len = len(comment_dict)
            if not dict_len:
                all_review = 'Reviews : \n'
                if dict_len < 3:
                    for k1, v1 in comment_dict.items():
                        all_review += '\n' + list(v1.keys())[0] + ' : ' + list(v1.values())[0]
                    context.bot.send_message(chat_id=update.effective_chat.id, text=all_review)
                else:
                    print(sorted(comment_dict.items())[:3])
                    for k1, v1 in sorted(comment_dict.items())[:3]:
                        all_review += '\n' + list(v1.keys())[0] + ' : ' + list(v1.values())[0]
                    context.bot.send_message(chat_id=update.effective_chat.id, text=all_review)
            else:
                update.message.reply_text('No comment of this movie in our database! Please share your comment.')
        elif query.data.split(" ",1)[1] == 'Rating':
            keyboard = [[1, 2, 3, 4, 5],[6, 7, 8, 9, 10]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please rate the movie in 1-10.', reply_markup=reply_markup)
            global rating_ind
            rating_ind = 1
    elif query.data.split(" ",1)[0] == '1_3' :
        if query.data.split(" ",1)[1] == 'Confirm' and comment_ind == 1 and rating_ind==0:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Comment Shared!')
            ref = db.reference('/Comment/' + movie_chosen)
            userid = query.from_user['id']
            global comment_text
            print(comment_text)
            value = {userid:comment_text}
            ref.push().set(value)
            comment_ind = 0
            del movie_chosen
            del comment_text
        elif query.data.split(" ",1)[1] == 'Reenter' and comment_ind == 1 and rating_ind==0:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please Reenter!')

        elif query.data.split(" ",1)[1] == 'Confirm' and comment_ind == 0 and rating_ind==1:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Rating Shared!')
            ref = db.reference('/Rating/' + movie_chosen)
            userid = query.from_user['id']
            global rating
            value = {userid:int(rating)}
            ref.push().set(value)
            rating_ind = 0
            del movie_chosen
            del rating
    
def txt_msg(update, context):
    if comment_ind == 1 and rating_ind==0:
        global comment_text
        comment_text = update.message.text.upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please review your comment: ' + '\n' + comment_text, 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data='1_3 Confirm'),InlineKeyboardButton("Reenter", callback_data='1_3 Reenter')]]))
    elif comment_ind == 0 and rating_ind==1:
        global rating
        rating = update.message.text.upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please review your rating: ' + '\n' + rating, 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data='1_3 Confirm'),InlineKeyboardButton("Reenter", callback_data='1_3 Reenter')]]))
    elif comment_ind == 0 and rating_ind==0:
        reply_message = update.message.text.upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)

def comment(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /comment is issued."""
    try:
        msg = "/help - command list" + "/n" + "/search - search movie"
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /comment <keyword>')

if __name__ == '__main__':
    main()