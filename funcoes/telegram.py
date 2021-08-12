# -------------------- Telegram -----------------------------

from telethon.client.telegramclient import TelegramClient


async def envia_mensagem(client=None, canal=None, mensagem=None):
    await client.send_message(canal, mensagem)


async def apaga_msg_todas(client=None, canal=None):

    entidade = await client.get_entity(canal)

    lista_mensagens = [
        i.id async for i in client.iter_messages(entidade) if not i.pinned == True
    ]

    await client.delete_messages(entidade, lista_mensagens)

async def teste(client, canal):
    entidade = await client.get_entity(canal)
    async for i in client.iter_messages(entidade):
        print(i)