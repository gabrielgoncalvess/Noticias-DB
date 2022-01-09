import pandas as pd
import sqlite3 
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import streamlit as st

# Criar ou se conectar ao banco de dados
conn = sqlite3.connect('noticias.db')

# Criar cursor
c = conn.cursor()

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
        data = datetime.strptime(data, '%d/%m/%Y').date()

        # Pegar titulo1
        titulo1 = container.h3.text.strip()

        # Pegar titulo2
        titulo2 = container.h2.a['title']

        # Pegar link
        link = container.h2.a['href']

        # Pegar Descrição
        desc = container.p.text
    
        c.execute("INSERT INTO noticias (DATA, HORA, TITULO, TITULO2, DESC, LINK) VALUES (?,?,?,?,?,?)",(data, hora, titulo1, titulo2, desc, link))

    conn.commit()
    
    #df = pd.DataFrame({'DATA':lista_data,'HORA':lista_hora,'TITULO':lista_titulo1,'TITULO2':lista_titulo2,'DESC':lista_desc,'LINK':lista_link})
    return 

def canalrural():
    web_canalrural('https://www.canalrural.com.br/noticias/')
    for i in range(2,7):
        web_canalrural(f'https://www.canalrural.com.br/noticias/page/{i}/')

    c.execute("""
    DELETE FROM noticias
    WHERE ID NOT IN (
    SELECT MIN(ID) 
    FROM noticias 
    GROUP BY TITULO2, LINK
    )
    """)
    conn.commit()

    # Resetar sequencia de ID
    c.execute("delete from sqlite_sequence where name='noticias'")
    conn.commit()

def make_clickable(link,titulo):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = titulo
    return f'<a target="_blank" href="{link}">{text}</a>'

def cria_pagina():
    # Configurar página para ficar em mode wide
    st.set_page_config(layout='wide')

    # Título do site
    st.write("# Banco de dados - Notícias - Canal Rural")

    # Puxar as notícias do banco de dados
    df = pd.read_sql_query("""SELECT STRFTIME('%d/%m/%Y', DATA) as DATA_F, DATA, HORA, TITULO AS CATEGORIA, 
    TITULO2 AS TITULO, LINK FROM noticias ORDER BY DATA DESC, HORA DESC LIMIT 20""",conn)
    df['DATA'] = df['DATA_F']
    df.drop(columns=['DATA_F'], inplace=True)
    
    # Função para tornar o link clicável
    df['TITULO'] = df.apply(lambda row: make_clickable(row['LINK'],row['TITULO']), axis=1)

    # Excluir coluna do link
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
        h1, table thead tr th{text-align:center !important;}
        footer {visibility: hidden}
        table {
            margin: 0 auto;
            text-align: center;
        }
        </style>
    """,unsafe_allow_html=True)
    
if __name__ == '__main__':
    # Função para pegar as notícias do canal rural 
    canalrural()

    cria_pagina()

    # Fechar conexão com o banco de dados
    conn.close()