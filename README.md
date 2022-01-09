# Banco de Dados de Notícias

Este projeto teve o intuito de se comparar 3 bancos de dados diferentes (Google Sheets, MongoDB e SQLite) tendo como objetivo armazer notícias do Canal Rural, de forma serverless (Heroku), e disponibilizá-las por meio de um web app utilizando-se o Streamlit. Link: https://streamlit-news-mongodb.herokuapp.com/

## Google Sheets:
Foi utilizada a API do google sheets para armazenar as notícias, geradas a partir de webscraping utilizando-se o Beautiful Soup. Após coletadas, são enviadas para uma planilha quer serve como base de dados. O código roda de forma serverless pelo Heroku

## MongoDB:
A partir do MongoDB Atlas, serviço de banco de dados em nuvem totalmente gerenciado, desenvolvido pela equipe oficial do MongoDB; um cluster foi criado para servir como base de dados para as notícias. Por meio do Advanced Scheduler do Heroku (add-on que fornece agendamento de tarefas como um serviço), foi possível programar o script de webscraping em horários e dias definidos para alimentar essa base. Em um outro arquivo, foi feito o deploy para o Heroku de um script que puxa essas informações do cluster e as disponibilza por meio do Streamlit. 

## SQLite
Dado que o Canal Rural é um site trivial para se realizar webscraping, não sendo necessário o uso de, por exemplo, Selenium, pode-se optar por usar uma base de dados local com o SQLite, visto que o script roda extremamente rápido. Nesse caso, também foi utilizado o Streamlit para disponibilizar as notícias, que são dispostas em ordem decrescente de data e hora, além de possuir o limite de 20 notícias.  
