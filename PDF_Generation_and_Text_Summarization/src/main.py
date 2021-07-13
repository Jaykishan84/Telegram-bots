from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import os
import telebot
import convertapi
import requests
import nltk 

nltk.download("punkt")

LANGUAGE = "english"

#Set up the environment variables.
api_key = os.environ['API_KEY']

#taken from the website https://www.convertapi.com/
#Set up the environment variables after getting an api key.
file_conversion_api_key = os.environ['CONVERSION_API_KEY']

#Authentication
convertapi.api_secret = file_conversion_api_key

bot = telebot.TeleBot(api_key)

#Function to store number of sentences to be kept in the summary.
def ask_no_of_sentences(message):
  try:
    global SENTENCES_COUNT
    SENTENCES_COUNT = int(message.text)
    msg = bot.send_message(message.chat.id, "Please send the .txt file containing the text to be summarized.")
    bot.register_next_step_handler(msg, summarize)
  except Exception as e:
    bot.send_message(message.chat.id, "Please only send the number of sentences.")

#Function to summarize text.
def summarize(message):
  try:
    file_id = message.document.file_id
    url = bot.get_file_url(file_id)
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    l=[]
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
      l.append(str(sentence))
    sentences = "".join(l)  
    bot.send_message(message.chat.id, sentences)
  except Exception as e:
    bot.send_message(message.chat.id, "Something went wrong.")

#Function to convert documents to Pdf.
def convert_to_Pdf(message):
  try:
    #get the file id of the document.
    file_id = message.document.file_id
    #get the path of the document using the file_id.
    path = bot.get_file_url(file_id)
    #send the file to the api for converting it to pdf.
    result = convertapi.convert('pdf', { 'File': path })
    #send the converted file to the user.
    bot.send_document(message.chat.id,result.file.url)
  except Exception as e:
    bot.send_message(message.chat.id,"Seems like the document format is not supported. Please try converting on this website instead \n https://www.convertapi.com/ Sorry for inconvenience.")

#Function to convert images of format png,jpg and jpeg to pdf files.
def img_to_pdf(message):
  try:
    #get the file id of the photo.
    file_id = message.photo[0].file_id
    #get the path of the document using the file_id.
    path = bot.get_file_url(file_id)
    #send the img to the api for converting it to pdf.
    result = convertapi.convert('pdf', {'File': path})
    #send the converted file to the user who requested.
    bot.send_document(message.chat.id,result.file.url)
  except Exception as e:
    bot.send_message(message.chat.id,"Seems like either the file type doesnot match or the file is to big for conversion. Please try converting on this website instead \n https://www.convertapi.com/ Sorry For inconvenience.")
 
#Function to select the options for user.
def provide_functionality(message):
  try:
    if(message.text == "1"):
      msg = bot.send_message(message.chat.id, "Please send the document you wish to convert.")
      bot.register_next_step_handler(msg, convert_to_Pdf)
    elif(message.text == "2"):
      msg = bot.send_message(message.chat.id, "Please send the image you wish to convert.")
      bot.register_next_step_handler(msg, img_to_pdf)
    elif(message.text == "3"):
      msg = bot.send_message(message.chat.id, "Please send the number of sentences you wish to have in summary.")
      bot.register_next_step_handler(msg, ask_no_of_sentences)
    elif(message.text == "4"):
      exit(message)
    else:
      msg = bot.send_message(message.chat.id,"Please select an appropriate option. Thank you!")
      bot.register_next_step_handler(msg, provide_functionality)
  except Exception as e:
        bot.reply_to(message, 'Something went wrong!')
  
#Function for exiting.
@bot.message_handler(commands=['Exit'])
def exit(message):
  bot.send_message(message.chat.id, "OK, Thank You very much for your patience. Apologies for any kind of trouble you might have faced. It was great talking to you.")


@bot.message_handler(content_types=['text'])
def markup_eg(message):
  msg = bot.send_message(message.chat.id, "Hey there, Following are the functionalities I can provide you.\n Press the number you prefer...\n 1. Convert Doc to Pdf \n 2. Convert Images to PDF \n 3. Summarize a text \n 4. Exit")
  bot.register_next_step_handler(msg, provide_functionality)

bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()
  
bot.polling()
