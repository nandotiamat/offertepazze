TOKEN = "1328830616:AAHxU87dN_TBdBQRCpBpfNpgdEJIBDkUkIs"

from telegram.ext import Updater, CommandHandler, Job, JobQueue
import logging
import json
import random 
from selenium import webdriver
import time
WAIT_TIME_SECONDS = 900

def getPost(postJson) : 
    if postJson["prezzo_scontato"] != None and postJson["prezzo_non_scontato"] != None:
        return "📦 <a href='" + postJson["productlink"] + "'>" + postJson["nome"] +  '</a> 📦\n\n' + "💸 Nuovo a <b>" + postJson["prezzo_scontato"] + "</b> anzichè <del>" + postJson["prezzo_non_scontato"] + '</del> 💸\n\n' + "🚀 " + "Disponibile ora!" + " 🚀"
    elif postJson["prezzo_scontato"] != None:
        return "📦 <a href='" + postJson["productlink"] + "'>" + postJson["nome"] +  '</a> 📦\n\n' + "💸 " + postJson["prezzo_scontato"] + ' 💸\n\n' + "🚀 " + "Disponibile ora!" + " 🚀"
    elif postJson["prezzo_non_scontato"] != None:
        return "📦 <a href='" + postJson["productlink"] + "'>" + postJson["nome"] +  '</a> 📦\n\n'+ "💸 " + postJson["prezzo_non_scontato"] + ' 💸\n\n' + "🚀 " + "Disponibile ora!" + " 🚀"

def send_post(context):

    with open("db.json", "r") as database: 
        db = json.loads(database.read())
        database.close()

    prodotto = None

    while prodotto == None:

        categoria = random.choice(list(db))
        keyword = random.choice(list(db[categoria]))
        if db[categoria][keyword] == []:
            print("La parola chiave " + keyword + " della categoria " + categoria + " risulta essere vuota, provo a cercare una nuova parola chiave.")
        else:
            prodotto = random.choice(db[categoria][keyword])
    
    print(prodotto)

    prezzo_scontato = None
    prezzo_non_scontato = None
    while prezzo_scontato == None or prezzo_non_scontato == None:
        prezzo_scontato = None
        prezzo_non_scontato = None
        driver.get(prodotto["productlink"])
        time.sleep(3)
        
        try:
            prezzo_non_scontato = driver.find_element_by_xpath("//span[@class='priceBlockStrikePriceString a-text-strike']").text
        except: 
            print("Prezzo non scontato non trovato.")

        try:
            prezzo_scontato = driver.find_element_by_xpath("//span[@class='a-size-medium a-color-price priceBlockBuyingPriceString']").text
        except:
            try:
                prezzo_scontato = driver.find_element_by_xpath("//span[@class='a-size-medium a-color-price priceBlockBuyingPriceString']").text
            except:
                try:
                    prezzo_scontato = driver.find_element_by_xpath("//span[@class='a-size-medium a-color-price priceBlockSalePriceString']").text
                except:
                    try:
                        prezzo_scontato = driver.find_element_by_xpath("//span[@class='a-size-medium a-color-price priceBlockDealPriceString']").text
                    except:
                        print("prezzo scontato non trovato")
        
        if prezzo_scontato != None and prezzo_non_scontato != None:
            prodotto["prezzo_scontato"] = prezzo_scontato
            prodotto["prezzo_non_scontato"] = prezzo_non_scontato
            #driver.quit()
        else:
            db[categoria][keyword].remove(prodotto)
            prodotto =  random.choice(db[categoria][keyword])
        
    context.bot.send_photo(chat_id="@offertepazzedalweb", photo=prodotto["img"], caption=getPost(prodotto), parse_mode = 'HTML')
    del prodotto
    with open("db.json", "w") as database:
        database.write(json.dumps(db, indent = 2))
        database.close()

driver = webdriver.Chrome("chromedriver.exe")
updater = Updater(token=TOKEN, use_context=True)
job_queue = JobQueue()
dispatcher = updater.dispatcher
job_queue.set_dispatcher(dispatcher)
start_handler = CommandHandler('send_post', send_post, pass_job_queue=True)
dispatcher.add_handler(start_handler)
job_queue.start()
job_queue.run_repeating(callback = send_post, interval = WAIT_TIME_SECONDS)
logging.basicConfig()
updater.start_polling()
