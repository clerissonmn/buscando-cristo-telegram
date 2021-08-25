#%%
from os import environ

from telethon import TelegramClient, client, events
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from config import flags
from funcoes.helper import carrega_segredos, hoje, mensagem_formatada

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

        # Escolhe o dia da semana
        if "segunda" in str(event.raw_text).lower():
            dia = "Segunda"
        elif "terça" in str(event.raw_text).lower():
            dia = "Terça"
        elif "quarta" in str(event.raw_text).lower():
            dia = "Quarta"
        elif "quinta" in str(event.raw_text).lower():
            dia = "Quinta"
        elif "sexta" in str(event.raw_text).lower():
            dia = "Sexta"
        elif "sábado" in str(event.raw_text).lower():
            dia = "Sábado"
        elif "domingo" in str(event.raw_text).lower():
            dia = "Domingo"
        elif "hoje" in str(event.raw_text).lower():
            dia = hoje.split("-")[0]
        else:
            dia = None

        if dia:
            # Envias as mensagens
            mensagens = mensagem_formatada(
                dia=dia, doc_key=doc_key, sheet_name=sheet_name
            )
            for mensagem in mensagens:
                await client.send_message(canal, mensagem)

            # Pega os ids do comando passado
            ids = [
                mensagem.id
                async for mensagem in client.iter_messages(entidade)
                if dia.lower() in str(mensagem.raw_text)
            ]
            await client.delete_messages(canal, ids)

    print("===> Bot operante.")

    await client.start()
    await client.run_until_disconnected()


def teste_mensagens():

    dia_lista = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]

    for dia in dia_lista:
        mensagens = mensagem_formatada(dia=dia, doc_key=doc_key, sheet_name=sheet_name)

        with open(f"mensagens_{dia}.md", "w") as file:
            file.writelines(mensagens)


if __name__ == "__main__":
    if flags["modo"].lower() == "teste":
        print(teste_mensagens())
    else:
        client.loop.run_until_complete(main(client))
