## chatbot.py
from logging.handlers import RotatingFileHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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
import re
import collections

def main():
    # Load your token and create an Updater for your Bot
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
    #omdb.set_default('apikey', OMDB_API_KEY)
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
    dispatcher.add_handler(CommandHandler("help", help))    
    dispatcher.add_handler(CallbackQueryHandler(button))

    global g_comment_ind
    g_comment_ind = 0

    global g_rating_ind
    g_rating_ind = 0

    global g_rating
    g_rating = 0

    # To start the bot:
    updater.start_polling()
    updater.idle()

def listToString(s): 
    str1 = " "  
    return (str1.join(s))

def average(lst):
    return sum(lst) / len(lst)

def cnt(lst):
    counter = collections.Counter()
    for d in lst: 
        counter.update(d)
    result = dict(counter)
    return result

def help(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        line1 = "/help" + " - command list"
        line2 = "/search <keyword>" + " - search movie information, give ratings, read and write comments to movies"
        line3 = "/toprate" + " - top rated movies"
        line4 = "/contribute" + " - most active commentators"
        line5 = "/recommend" + " - movie recommendation"
        msg =  line1 + "\n"+ "\n" + line2 + "\n"+ "\n" + line3 + "\n"+ "\n" + line4 + "\n"+ "\n" + line5
        context.bot.send_message(chat_id=update.effective_chat.id, text= msg)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /help <keyword>')

def toprate(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /toprate is issued."""
    try:
        ref = db.reference("/Rating/")
        rating_dict = ref.get()
        user_raing_avg = {}
        if rating_dict is not None:
            for k1, v1 in rating_dict.items():
                raw = omdb.get(imdbid=str(k1))
                movieid = raw['title']
                movierate = []
                for k2, v2 in v1.items():
                    movierate.append(list(v2.values())[0])
                    movierate_avg = round(average(movierate), 1)
                    user_raing_avg[movieid] = movierate_avg
            sorted_user_raing_avg_keys = sorted(user_raing_avg, key=user_raing_avg.get, reverse=True)
            toprate_result = ''
            if len(sorted_user_raing_avg_keys) < 10:
                for k3 in sorted_user_raing_avg_keys:
                    toprate_result += '\n' + k3 + ' : ' + str(user_raing_avg[k3])
            else:
                for k3 in sorted_user_raing_avg_keys[:10]:
                    toprate_result += '\n' + k3 + ' : ' + str(user_raing_avg[k3])
            update.message.reply_text('Congratulation to our top 10 best rated movies. \n' + toprate_result)
        else:
            update.message.reply_text('No comment or rating in our database! Please share your thoughts with us.')    
    except (IndexError, ValueError):
        update.message.reply_text('No comment or rating in our database! Please share your thoughts with us.')

def contribute(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /contribute is issued."""
    try:
        comb_list = []
        c_ref = db.reference("/Comment/")
        comment_dict = c_ref.get()
        user_comment_count = {}
        r_ref = db.reference("/Rating/")
        rating_dict = r_ref.get()
        user_rating_count = {}
        if comment_dict is not None:
            for k1, v1 in comment_dict.items():
                for k2, v2 in v1.items():
                    userid = list(v2.keys())[0]
                    if userid not in user_comment_count.keys():
                        user_comment_count[userid] = 1
                    elif userid in user_comment_count.keys():
                        user_comment_count[userid] += 1
            comb_list.append(user_comment_count)
            #result=cnt(comb_list)
            #active_user = max(result, key=result.get)
            #comment_vol = user_comment_count[active_user]
            #msg_txt_2='\n - ' + str(comment_vol) + ' comment'
        if rating_dict is not None:
            for k1, v1 in rating_dict.items():
                for k2, v2 in v1.items():
                    userid = list(v2.keys())[0]
                    if userid not in user_rating_count.keys():
                        user_rating_count[userid] = 1
                    elif userid in user_rating_count.keys():
                        user_rating_count[userid] += 1
            comb_list.append(user_rating_count)
            result=cnt(comb_list)
            #active_user = max(result, key=result.get)
            #rating_vol = user_rating_count[active_user]
            #msg_txt_3='\n - ' + str(rating_vol) + ' rating'
        result=cnt(comb_list)
        #print(result)
        #print(user_rating_count)
        #print(user_comment_count)
        sorted_result=sorted_user_raing_avg_keys = sorted(result, key=result.get, reverse=True)
        msg_txt='Congratulation to our active users! \n'
        if len(sorted_result) < 3:
            for k3 in sorted_result:
                if k3 in user_rating_count and k3 in user_comment_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : '  + str(user_comment_count[k3]) + ' comment & ' + str(user_rating_count[k3]) + ' rating' + '\n'
                elif k3 in user_rating_count and k3 not in user_comment_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : '  + str(user_rating_count[k3]) + ' rating' + '\n'
                elif k3 in user_comment_count and k3 not in user_rating_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : '  + str(user_comment_count[k3]) + ' comment' + '\n'
        else:
            for k3 in sorted_result[:3]:
                if k3 in user_rating_count and k3 in user_comment_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : ' + str(user_comment_count[k3]) + ' comment & ' + str(user_rating_count[k3]) + ' rating' + '\n'
                elif k3 in user_rating_count and k3 not in user_comment_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : ' + str(user_rating_count[k3]) + ' rating' + '\n'
                elif k3 in user_comment_count and k3 not in user_rating_count:
                    msg_txt += '\n' +'user_' + k3.split('_')[1].upper() + ' : ' + str(user_comment_count[k3]) + ' comment' + '\n'
        update.message.reply_text(msg_txt)
    except (IndexError, ValueError):
        update.message.reply_text('No comment or rating in our database! Please share your thoughts with us.')

def recommend(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /recommend is issued."""
    try:
        ref = db.reference("/Rating/")
        rating_dict = ref.get()
        user_raing_avg = {}
        if rating_dict is not None:
            for k1, v1 in rating_dict.items():
                raw = omdb.get(imdbid=k1)
                movieid = k1+'_'+raw['title']
                movierate = []
                for k2, v2 in v1.items():
                    movierate.append(list(v2.values())[0])
                    movierate_avg = average(movierate)
                    user_raing_avg[movieid] = movierate_avg
            sorted_user_raing_avg_keys = sorted(user_raing_avg, key=user_raing_avg.get, reverse=True)
            print(sorted_user_raing_avg_keys)
            if len(sorted_user_raing_avg_keys) < 10:
                randnbr=np.random.randint(1, len(sorted_user_raing_avg_keys))
                rmd = sorted_user_raing_avg_keys[randnbr]
                videos = Search(rmd + " Trailer", limit = 1).videos()
                rmd_chk = omdb.get(imdbid=rmd.split("_",1)[0])
                context.bot.send_message(chat_id=update.effective_chat.id, text='We recommend you check out \n' + rmd_chk['title'])
                context.bot.send_message(chat_id=update.effective_chat.id, text=rmd_chk['plot'])
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=rmd_chk['poster'])
                context.bot.send_message(chat_id=update.effective_chat.id, text="https://youtu.be/" + str(videos[0]['id']))
            else:
                randnbr=np.random.randint(1,10)
                rmd = sorted_user_raing_avg_keys[10:][randnbr]
                videos = Search(rmd + " Trailer", limit = 1).videos()
                rmd_chk = omdb.get(imdbid=rmd.split("_",1)[0])
                context.bot.send_message(chat_id=update.effective_chat.id, text='We recommend you check out \n' + rmd_chk['title'])
                context.bot.send_message(chat_id=update.effective_chat.id, text=rmd_chk['plot'])
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=rmd_chk['poster'])
                context.bot.send_message(chat_id=update.effective_chat.id, text="https://youtu.be/" + str(videos[0]['id']))
        else:
            update.message.reply_text('No recommendation from other users at the moment! Please share your thoughts with us.')
    except (IndexError, ValueError):
        update.message.reply_text('No recommendation from other users at the moment! Please share your thoughts with us.')

def search(update: Updater, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    try:
        out_list_1 = [re.sub(r'[^a-zA-Z0-9]','',string) for string in context.args]
        out_list_2 = ['*' + sub + '*' for sub in out_list_1]
        raw = omdb.search_movie(out_list_2)
        keyboard = []
        dup_chk = []
        n=0
        if raw is None:
            update.message.reply_text("No search result! Please select other keywords.")
        else:
            for i in raw:
                if n <=5:
                    if i['imdb_id'] not in dup_chk:
                        dup_chk.append(i['imdb_id'])
                        keyboard.append([InlineKeyboardButton(i["title"], callback_data='1_1 '+i["imdb_id"])])
                        n+=1
                else:
                    break
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please select one movie from below or revise your keyword if you can't find what you want.", reply_markup=reply_markup)
    except (IndexError, ValueError):
        update.message.reply_text("No search result! Please select other keywords.")

def button(update: Updater, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""

    query = update.callback_query
    query.answer()
    global g_menu_button
    if query.data.split(" ",1)[0] == '1_1':
            global movie_chosen
            movie_chosen = query.data.split(" ",1)[1]
            raw = omdb.get(imdbid=movie_chosen)
            print(type(movie_chosen))
            print(movie_chosen)
            query.edit_message_text(text='You have selected : \n \n' + raw['title'])
            context.user_data['menu']=context.bot.send_message(chat_id=update.effective_chat.id, text='\n \n' + 'Would you like to...',reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("More Information", callback_data='1_2 Information'),InlineKeyboardButton("Leave Comment", callback_data='1_2 Comment')],[InlineKeyboardButton("Check Reviews", callback_data='1_2 Review'),InlineKeyboardButton("Give Rating", callback_data='1_2 Rating')]]))
            g_menu_button = context.user_data['menu']
    elif query.data.split(" ",1)[0] == '1_2':
        if query.data.split(" ",1)[1] == 'Information':
            raw = omdb.get(imdbid=movie_chosen)
            videos = Search(raw['title'] + " Trailer", limit = 1).videos()
            query.edit_message_text(text=raw['plot'])
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=raw['poster'])
            context.bot.send_message(chat_id=update.effective_chat.id, text="https://youtu.be/" + str(videos[0]['id']))
        elif query.data.split(" ",1)[1] == 'Comment':
            query.edit_message_text(text='Please leave comment')
            global g_comment_ind
            g_comment_ind = 1
        elif query.data.split(" ",1)[1] == 'Review':
            ref = db.reference("/Comment/" + movie_chosen + "/")
            comment_dict = ref.get()
            if comment_dict is None:
                query.edit_message_text(text='No comment of this movie in our database! Please share your comment.')
            else:
                dict_len = len(comment_dict)
                all_review = 'Reviews : \n'
                if dict_len < 3:
                    for k1, v1 in comment_dict.items():
                        all_review += '\n' + list(v1.keys())[0].split('_')[1].upper() + ' : ' + list(v1.values())[0]
                    query.edit_message_text(text=all_review)
                else:
                    print(sorted(comment_dict.items())[:3])
                    for k1, v1 in sorted(comment_dict.items())[:3]:
                        all_review += '\n' + list(v1.keys())[0].split('_')[1].upper() + ' : ' + list(v1.values())[0]
                    query.edit_message_text(text=all_review)
        elif query.data.split(" ",1)[1] == 'Rating':
            global g_keyboard
            g_keyboard = [[1, 2, 3, 4, 5],[6, 7, 8, 9, 10]]
            global g_reply_markup
            g_reply_markup = ReplyKeyboardMarkup(g_keyboard, one_time_keyboard=True, resize_keyboard=True)
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=g_menu_button.message_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please rate the movie in 1-10.', reply_markup=g_reply_markup)
            global g_rating_ind
            g_rating_ind = 1
    elif query.data.split(" ",1)[0] == '1_3' :
        if query.data.split(" ",1)[1] == 'Confirm' and g_comment_ind == 1 and g_rating_ind==0:
            ref = db.reference('/Comment/' + movie_chosen)
            key = str(query.from_user['id'])+'_'+str(query.from_user['first_name'])
            global g_comment_text
            value = {key:g_comment_text}
            ref.push().set(value)
            query.edit_message_text(text='Comment Shared!')
            g_comment_ind = 0
            del movie_chosen
            del g_comment_text
        elif query.data.split(" ",1)[1] == 'Reenter' and g_comment_ind == 1 and g_rating_ind==0:
            query.edit_message_text(text='Please Reenter!')

        elif query.data.split(" ",1)[1] == 'Confirm' and g_comment_ind == 0 and g_rating_ind==1:
            ref = db.reference('/Rating/' + movie_chosen)
            key = str(query.from_user['id'])+'_'+str(query.from_user['first_name'])
            global g_rating
            global g_rating_review
            value = {key:int(g_rating)}
            ref.push().set(value)
            reply_markup = ReplyKeyboardRemove()
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=g_rating_review.message_id)
            context.bot.send_message(chat_id=update.effective_chat.id,text='Rating Shared!',reply_markup=reply_markup)
            g_rating_ind = 0
            del movie_chosen
            del g_rating
            del g_rating_review
        elif query.data.split(" ",1)[1] == 'Reenter' and g_comment_ind == 0 and g_rating_ind==1:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=g_rating_review.message_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Please Reenter!', reply_markup=g_reply_markup)
    
def txt_msg(update, context):
    if g_comment_ind == 1 and g_rating_ind==0:
        global g_comment_text
        g_comment_text = update.message.text.upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please review your comment: ' + '\n \n' + g_comment_text,
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data='1_3 Confirm'),InlineKeyboardButton("Reenter", callback_data='1_3 Reenter')]]))

    elif g_comment_ind == 0 and g_rating_ind==1:
        global g_rating
        g_rating = update.message.text.upper()
        context.user_data['rating_review']= context.bot.send_message(chat_id=update.effective_chat.id, text='Please review your rating: ' + '\n \n' + g_rating,
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Confirm", callback_data='1_3 Confirm'),InlineKeyboardButton("Reenter", callback_data='1_3 Reenter')]]))
        global g_rating_review
        g_rating_review = context.user_data['rating_review']
    elif g_comment_ind == 0 and g_rating_ind==0:
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