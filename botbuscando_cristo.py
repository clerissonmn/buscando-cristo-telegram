#%%
from os import environ

from telethon import TelegramClient, client, events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from funcoes.helper import amanha, carrega_segredos, hoje, mensagem_formatada, texto_final

import time
#%% [ Variáveis de configuração ]

try:
    segredos = carrega_segredos(file="segredos", delim="=>")
except FileNotFoundError:
    segredos = environ

doc_key = segredos["doc_key"]
sheet_name = segredos["sheet_name"]
api_id = segredos["api_id"]
api_hash = segredos["api_hash"]
bot_token = segredos["bot_token"]

canal = segredos["canal"]
#canal = "me"

session_string = segredos["session_string"]

client = TelegramClient(StringSession(session_string), api_id, api_hash)


async def main(client):

    print("==> Aplicação corretamente iniciada.")

    #%% [ Bot ]
    # Apaga todas as mensagens com o comnado /apaga
    @client.on(events.NewMessage(pattern=f"\/clear"))
    async def handler(event, client=client, canal=canal):

        entidade = await client.get_entity(canal)

        # Pega os ids de todas as mensagens que não são fixadas
        ids = [
            mensagem.id
            async for mensagem in client.iter_messages(entidade)
            if not mensagem.pinned == True
        ]

        print("==> Apagando todas as mensagens")
        await client.delete_messages(canal, ids)

    # Envia os horários para um dado dia da semana
    @client.on(events.NewMessage(pattern=f"(?i)\/[a-z]+"))
    async def handler(event, client=client):

        entidade = await client.get_entity(canal)

        tempo = 1

        # Escolhe o dia da semana
        if "segunda" in str(event.raw_text).lower():
            dia = ["Segunda-Feira"]
        elif "terça" in str(event.raw_text).lower():
            dia = ["Terça-Feira"]
        elif "quarta" in str(event.raw_text).lower():
            dia = ["Quarta-Feira"]
        elif "quinta" in str(event.raw_text).lower():
            dia = ["Quinta-Feira"]
        elif "sexta" in str(event.raw_text).lower():
            dia = ["Sexta-Feira"]
        elif "sábado" in str(event.raw_text).lower():
            dia = ["Sábado"]
        elif "domingo" in str(event.raw_text).lower():
            dia = ["Domingo"]
        elif "hoje" in str(event.raw_text).lower():
            dia = [hoje.split("-")[0]]
        elif "amanhã" in str(event.raw_text).lower():
            dia = [amanha]
        elif "todos" in str(event.raw_text).lower():
            dia = [
                "Segunda-Feira",
                "Terça-Feira",
                "Quarta-Feira",
                "Quinta-Feira",
                "Sexta-Feira",
                "Sábado",
                "Domingo",
            ]
            tempo = 30 #s
        else:
            dia = None

        if dia:
            for i in dia:
                # Prepara as mensagens
                mensagens = mensagem_formatada(
                    dia=i, doc_key=doc_key, sheet_name=sheet_name
                )

                for mensagem in mensagens:
                    print(f'esperando: 10 segundos')
                    time.sleep(10)
                    print(f'pronto!')
                    await client.send_message(canal, mensagem)

                print(f'esperando: {tempo} segundos')
                time.sleep(tempo)
                print(f'pronto!')

            # Envia a mensgem final
            await client.send_message(canal, texto_final)

    print("===> Bot operante.")

    #    await client.start()
    await client.run_until_disconnected()


#     @client.on(events.NewMessage(pattern=f"\/apc"))
#     async def handler(event, client=client, canal=canal):
#         await apaga_comandos(client, canal)

# async def apaga_comandos(entidade, canal):
#     ids = [
#         mensagem.id
#         async for mensagem in client.iter_messages(entidade)
#         if "/" in str(mensagem.raw_text)
#     ]
#     await client.delete_messages(canal, ids)

def teste_mensagens():

    dia_lista = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]

    for dia in dia_lista:
        mensagens = mensagem_formatada(dia=dia, doc_key=doc_key, sheet_name=sheet_name)

        with open(f"mensagens_{dia}.md", "w") as file:
            file.writelines(mensagens)


if __name__ == "__main__":
    with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        client.loop.run_until_complete(main(client))
