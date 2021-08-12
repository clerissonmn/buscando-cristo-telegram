#%%
from datetime import datetime as dt

from pandas.io.parsers import read_csv
from telethon import TelegramClient

from lib.funcoes import (_dias_da_semana, apaga_msg_todas,
                         baixa_csv_do_gsheets, carrega_segredos,
                         envia_mensagem, formata_mensagem, pega_horarios,
                         traduz)

# [ Carrega os segredos ]

segredos = carrega_segredos(file="segredos")

doc_key = segredos["doc_key"]
sheet_name = segredos["sheet_name"]
api_id = segredos["api_id"]
api_hash = segredos["api_hash"]
bot_token = segredos["bot_token"]

client = TelegramClient("anon", api_id, api_hash)
canal = "https://t.me/missaseconfissoes"

print(f"==> Apagando as mensagens do canal")
with client:
    client.loop.run_until_complete(apaga_msg_todas(client=client, canal=canal))

#%% [ Faz a busca das informações]
tabela_csv = baixa_csv_do_gsheets(doc_key=doc_key, sheet_name=sheet_name)
df = read_csv(tabela_csv)

programacao_lista = ["Missa", "Confissão"]
cidade_lista = ["Belém", "Ananindeua"]
hoje = _dias_da_semana[dt.today().strftime("%A")]

for programacao in programacao_lista:
    for cidade in cidade_lista:

        print(f"==> Enviando {programacao} em {cidade}")

        resultado = pega_horarios(
            df=df,
            programacao=programacao,
            natureza="Presencial",
            cidade=cidade,
            bairro="todos",
            dia_da_semana="hoje",
            formato_saida="dict",
        )

        mensagem = formata_mensagem(
            resultado=resultado, cidade=cidade, programacao=programacao, dia=hoje
        )

        with client:
            client.loop.run_until_complete(
                envia_mensagem(client=client, canal=canal, mensagem=mensagem)
            )
