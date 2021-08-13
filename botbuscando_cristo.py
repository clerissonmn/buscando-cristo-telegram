#%%
from telethon import TelegramClient, client, events

from funcoes.helper import carrega_segredos, hoje, mensagem_formatada

from os import environ
#%% [ Variáveis de configuração ]

try:

    segredos = carrega_segredos(file="segredos")

    doc_key = segredos["doc_key"]
    sheet_name = segredos["sheet_name"]
    api_id = segredos["api_id"]
    api_hash = segredos["api_hash"]
    bot_token = segredos["bot_token"]
    canal = segredos["canal"]
    phone_number = segredos["phone_number"]
    code = segredos['code']

except FileNotFoundError:

    doc_key = environ["doc_key"]
    sheet_name = environ["sheet_name"]
    api_id = environ["api_id"]
    api_hash = environ["api_hash"]
    bot_token = environ["bot_token"]
    canal = environ["canal"]
    phone_number = environ["phone_number"]
    code = environ['code']

client = TelegramClient("anon", api_id, api_hash)

async def main():

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

    print("==> Iniciando o bot")

#    client.start('+5591982366631','61273')

    await client.connect()
    if not await client.is_user_authorized():
#        await client.send_code_request(phone_number)
        me = await client.sign_in(phone_number, code)

    await client.run_until_disconnected()
if __name__ == "__main__":
    client.loop.run_until_complete(main())