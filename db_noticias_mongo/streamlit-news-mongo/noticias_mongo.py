import pandas as pd
import streamlit as st
import pymongo
from datetime import datetime

client = pymongo.MongoClient("mongodb+srv://mongo:SUA_SENHAn@cluster0.tiyed.mongodb.net/base?retryWrites=true&w=majority")

db = client.base

db_noticias = db['noticias']
db_palavras = db['sites-palavras']

def make_clickable(link,titulo):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = titulo
    return f'<a target="_blank" href="{link}">{text}</a>'

def cria_pagina(df):
    # Configurar página para ficar em mode wide
    st.set_page_config(layout='wide')

    # Título do site
    st.write("# Banco de dados - Notícias - Canal Rural")
    st.write("## MongoDB")

    #Função para tornar o link clicável
    df['TITULO'] = df.apply(lambda row: make_clickable(row['LINK'],row['TITULO']), axis=1)

    #Excluir coluna do link
    df.drop(columns=['LINK'],inplace=True)

    # Começar o índice em 1
    df.index+=1

    # Centralizar o texto das colunas
    df.style.set_properties(**{'text-align': 'center'})

    # Transformar o df em html para tornar os links clicáveis
    st.write(df.to_html(escape=False),unsafe_allow_html=True)
    
    # CSS para estilizar a página
    st.markdown(""" 
        <style>
        a:link {text-decoration:none;}
        h1, h2, table thead tr th{text-align:center !important;}
        footer {visibility: hidden}
        table {
            margin: 0 auto;
            text-align: center;
        }
        </style>
    """,unsafe_allow_html=True)

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

    df = (pd.DataFrame(list(db_noticias.find({},{'_id':False,"DESC":False})))).drop_duplicates(subset=['TITULO'])
    df['DATA'] = df['DATA'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))

    df = df.sort_values(by=['DATA','HORA'],ascending=False).reset_index(drop=True).head(20)
    df['DATA'] = df['DATA'].apply(lambda x: f'{x:%d/%m/%Y}')

    cria_pagina(df)

