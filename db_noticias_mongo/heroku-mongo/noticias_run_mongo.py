import pandas as pd
import requests
from bs4 import BeautifulSoup
import pymongo

# db = client['novabase']

# db_noticias = db['noticias']
# db_palavras = db['sites-palavras']

client = pymongo.MongoClient("mongodb+srv://mongo:SUA_SENHA@cluster0.tiyed.mongodb.net/base?retryWrites=true&w=majority")

db = client.base

db_noticias = db['noticias']
db_palavras = db['sites-palavras']

# CANAL RURAL
def web_canalrural(page_url):
    #page_url1 = 'https://www.canalrural.com.br/noticias/'
    #page_url2 = 'https://www.canalrural.com.br/noticias/page/2/'

    page = requests.get(page_url)

    soup = BeautifulSoup(page.text, 'html.parser')

    lista_noticias = soup.find_all('div', {'class':'fl-post-column'})[:10]

    for container in lista_noticias:
        # Pegar data e hora
        div_data_hora = container.find('div',{'class':'data-hora'})
        data, hora = div_data_hora.text.strip().split(' às ')
        #data = datetime.strptime(data, '%d/%m/%Y').date()

        # Pegar titulo1
        titulo1 = container.h3.text.strip()

        # Pegar titulo2
        titulo2 = container.h2.a['title']

        # Pegar link
        link = container.h2.a['href']

        # Pegar Descrição
        desc = container.p.text
    
        #c.execute("INSERT INTO noticias (DATA, HORA, TITULO, TITULO2, DESC, LINK) VALUES (?,?,?,?,?,?)",(data, hora, titulo1, titulo2, desc, link))
        db_noticias.insert_one({"DATA": data, "HORA": hora, "CATEGORIA": titulo1, "TITULO": titulo2, "DESC": desc, "SITE": "CANAL RURAL", "LINK": link})

    #db_noticias = db_noticias.aggregate([{ "$group": { "_id": { "value": "$value" }, "uniqueIds": { "$addToSet": "$_id" }, "count": { "$sum": 1 } } }, { "$match": { "count": { "$gt": 1 } } }])
    #df = pd.DataFrame({'DATA':lista_data,'HORA':lista_hora,'TITULO':lista_titulo1,'TITULO2':lista_titulo2,'DESC':lista_desc,'LINK':lista_link})
    return 

def canalrural():
    web_canalrural('https://www.canalrural.com.br/noticias/')
    for i in range(2,7):
        web_canalrural(f'https://www.canalrural.com.br/noticias/page/{i}/')

def make_clickable(link,titulo):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = titulo
    return f'<a target="_blank" href="{link}">{text}</a>'

def join_collections():
    result = db_noticias.aggregate([{
        "$lookup":{
            "from":"sites-palavras",
            "localField":"SITE",
            "foreignField":"site",
            "as":"palavrasChave"
        }
    }, {
        "$set": {
        "palavrasChave": { "$arrayElemAt": ["$palavrasChave.palavrasChave", 0] }
        }
    }])

    df = (pd.DataFrame(list(result))).drop(columns=['_id']).drop_duplicates(subset=['TITULO'])
    return df

if __name__ == '__main__':
    # db_noticias.insert_many(df.to_dict('records'))
    # Função para pegar as notícias do canal rural 
    canalrural()
    print("--- SUCESSO ---")


