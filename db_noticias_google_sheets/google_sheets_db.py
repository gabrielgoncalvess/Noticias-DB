import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pandas as pd
import requests
from bs4 import BeautifulSoup

# FAZER UM SERVIDOR LOCAL, OU SEJA, UMA PLANILHA NO DIRETÓRIO QUE SERVE COMO DB PRINCIPAL, PARA RETIRAR DUPLICATAS
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = 'Página1!A2:F100000'


def auth():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    return service

def main():

    service = auth()

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    df = pd.DataFrame(values[1:], columns=values[0])
    
    return df

# CANAL RURAL
def web_canalrural(page_url):
    #page_url1 = 'https://www.canalrural.com.br/noticias/'
    #page_url2 = 'https://www.canalrural.com.br/noticias/page/2/'

    page = requests.get(page_url)

    soup = BeautifulSoup(page.text, 'html.parser')

    lista_noticias = soup.find_all('div', {'class':'fl-post-column'})[:10]

    lista_data = []
    lista_hora = []
    lista_titulo1 = []
    lista_titulo2 = []
    lista_desc = []
    lista_link = []
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

        lista_data.append(data)
        lista_hora.append(hora)
        lista_titulo1.append(titulo1)
        lista_titulo2.append(titulo2)
        lista_desc.append(desc)
        lista_link.append(link)
    
    df = pd.DataFrame({'DATA':lista_data,'HORA':lista_hora,'CATEGORIA':lista_titulo1,'TITULO':lista_titulo2,'DESC':lista_desc,'LINK':lista_link})
    
    return df 

def canalrural():
    df = web_canalrural('https://www.canalrural.com.br/noticias/')
    for i in range(2,7):
        df = df.append(web_canalrural(f'https://www.canalrural.com.br/noticias/page/{i}/'))
    return df
 
def Export_Data_To_Sheets(df, db):

    db = db.append(df)

    db.drop_duplicates(subset=['TITULO'], inplace=True)
    db.to_excel('noticias_db.xlsx',index=False)

    service = auth()

    service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=db.values.tolist()),
        valueInputOption="USER_ENTERED"
        # valueInputOption="RAW"
    ).execute()


if __name__ == '__main__':
    df_db = pd.read_excel('noticias_db.xlsx')
    Export_Data_To_Sheets(canalrural(), df_db)
    print('--- SUCESSO ---')