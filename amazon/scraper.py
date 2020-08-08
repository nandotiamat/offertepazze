from selenium import webdriver
import time
import tkinter
import base64
from urllib.request import urlopen
import json
from bitlyshortener import Shortener
from playsound import playsound
from selenium.webdriver.common.keys import Keys
import sys

def loading(t, msg) :
    print(msg)
    time.sleep(t)

def login() :
    credentials = []
    with open("credentials.json", "r") as read_file:
        credentials = json.load(read_file)
    email = driver.find_element_by_xpath("//input[@type='email']")
    password = driver.find_element_by_xpath("//input[@type='password']")
    email.send_keys(credentials["email"])
    password.send_keys(credentials["password"])
    driver.find_element_by_xpath("//input[@id='signInSubmit']").click()

def scroll() :
    for i in range(0,5):
        driver.execute_script('document.getElementsByClassName("ac-card-content ac-overflow-auto search-result-body")[0].scrollTo(0,10000)')
        driver.execute_script('document.getElementsByClassName("ac-card-content ac-overflow-auto search-result-body")[0].scrollTo(0,10000)')
        loading(2, "scrolling...")

def main():
    if len(sys.argv) == 2:
        print("handling " + category + "  " + keyword + ":") 
    driver.get("https://programma-affiliazione.amazon.it/home/productlinks/search?ac-ms-src=ac-nav")
    loading(5, "loading page...")
    try:
        driver.find_element_by_xpath("//input[@type='email']")
        login()
        loading(3, "loading data...")
    except:
        pass
    search_bar = driver.find_element_by_xpath("//input[@class='a-input-text search-field']")
    search_bar.send_keys(keyword)
    driver.find_element_by_xpath("//input[@class='a-button-input']").click()
    loading(4, "searching products...")
    prodotti = []
    scroll()
    tabella_prodotti = driver.find_elements_by_xpath("//tr[@class='search-result-item']")
    print("test")
    for prodotto in tabella_prodotti: 
        img = prodotto.find_element_by_xpath(".//td[@class='a-span2 product-image']//img").get_attribute("src")
        nome = prodotto.find_element_by_xpath(".//li[@class='product-name']//span//a").get_attribute("title")
        productlink = prodotto.find_element_by_xpath(".//li[@class='product-name']//span//a").get_attribute("href")
        try: 
            prezzo_non_scontato = prodotto.find_element_by_xpath(".//div[@class='ac-product-price ac-product-price-discounted']").text
            prezzo_non_scontato = "€" + prezzo_non_scontato[1:]
        except:
            prezzo_non_scontato = None
        try:
            prezzo_scontato = prodotto.find_element_by_xpath(".//div[@class='ac-product-price']").text
            prezzo_scontato = "€" + prezzo_scontato[1:]
        except: 
            prezzo_scontato = None
        if prezzo_non_scontato != None and prezzo_scontato != None:
            prodotti.append({"nome": nome, "productlink": productlink, "img": img, "prezzo_non_scontato": prezzo_non_scontato, "prezzo_scontato": prezzo_scontato})

    with open('db.json', 'r') as dbFile:
        db = json.loads(dbFile.read())
        
    with open('db.json', 'w') as outfile:
        if len(sys.argv) == 3:
            db[sys.argv[1]][sys.argv[2]] = prodotti
            json.dump(db, outfile, indent= 2)
        else:
            db[category][keyword] = prodotti
            json.dump(db, outfile, indent= 2)
   
    
token = ["23962db8cca72c72682ca716a4476d6837486e2f"]
shortener = Shortener(tokens=token, max_cache_size=8192)
with open("db.json", "r") as database:
    db = json.loads(database.read())
try:
    if len(sys.argv) == 3:
        if sys.argv[1] in db and sys.argv[2] in db[sys.argv[1]]:    
            category = sys.argv[1]
            keyword = sys.argv[2]
            driver = webdriver.Chrome("chromedriver.exe")
            main()
            driver.quit()
        else: 
            print("Errore, categoria e keywords sbagliate.")
            sys.exit(0)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "refresh":
            driver = webdriver.Chrome("chromedriver.exe")
            for category in db:
                for keyword in db[category]:
                    main()
            driver.quit()
    else:
        print("Scrivi bene gli argomenti.")
except IndexError as e:
    print(e)
    print("il programma vuole due parametri: categoria e keyword.")
    sys.exit(0) 

