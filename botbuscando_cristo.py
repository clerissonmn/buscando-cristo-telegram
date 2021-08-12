#%%
from datetime import datetime as dt

from pandas.io.parsers import read_csv
from telethon import TelegramClient

from funcoes.helper import (_dias_da_semana, baixa_csv_do_gsheets,
                            carrega_segredos, formata_mensagem, pega_horarios)
from funcoes.telegram import apaga_msg_todas, envia_mensagem, teste

#%% [ Carrega os segredos ]

segredos = carrega_segredos(file="segredos")

doc_key = segredos["doc_key"]
sheet_name = segredos["sheet_name"]
api_id = segredos["api_id"]
api_hash = segredos["api_hash"]
bot_token = segredos["bot_token"]


#%% [ Entrada de dados ]
client = TelegramClient("anon", api_id, api_hash)
canal = segredos["canal"]

# Carrega as informações de hoje
tabela_csv = baixa_csv_do_gsheets(doc_key=doc_key, sheet_name=sheet_name)
df = read_csv(tabela_csv)

#%% [ Funções ]

print(f"==> Apagando as mensagens do canal")
with client:
    client.loop.run_until_complete(apaga_msg_todas(client=client, canal=canal))
    # client.loop.run_until_complete(teste(client=client, canal=canal))


hoje = _dias_da_semana[dt.today().strftime("%A")]
programacao_lista = ["Missa", "Confissão"]
cidade_lista = ["Belém", "Ananindeua"]

dia_da_semana = hoje #['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

for programacao in programacao_lista:
    for cidade in cidade_lista:
        print(f"==> Enviando {programacao} em {cidade} para {dia_da_semana}")

        resultado = pega_horarios(
            df=df,
            programacao=programacao,
            natureza="Presencial",
            cidade=cidade,
            bairro="todos",
            dia_da_semana=dia_da_semana,
            formato_saida="dict",
        )

        # Formata em uma mensagem
        mensagem = formata_mensagem(
            resultado=resultado,
            cidade=cidade,
            programacao=programacao,
            dia=dia_da_semana,
        )

        # Envia a mensagem
        with client:
            client.loop.run_until_complete(
                envia_mensagem(client=client, canal=canal, mensagem=mensagem)
            )