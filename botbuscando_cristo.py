#%%
from telethon import TelegramClient, events

from funcoes.helper import carrega_segredos, mensagem_formatada, hoje


#%% [ Variáveis de configuração ]

segredos = carrega_segredos(file="segredos")

doc_key = segredos["doc_key"]
sheet_name = segredos["sheet_name"]
api_id = segredos["api_id"]
api_hash = segredos["api_hash"]
bot_token = segredos["bot_token"]

client = TelegramClient("anon", api_id, api_hash)
canal = segredos["canal"]


if __name__ == '__main__':
    #%% [ Bot ]
    # Apaga todas as mensagens com o comnado /apaga
    @client.on(events.NewMessage(pattern=f'\/clear'))
    async def handler(event, client=client, canal=canal):

        entidade = await client.get_entity(canal)

        # Pega os ids de todas as mensagens que não são fixadas
        ids = [mensagem.id async for mensagem in client.iter_messages(entidade) if not mensagem.pinned == True]

        print('==> Apagando todas as mensagens')
        await client.delete_messages(canal, ids)

    # Envia os horários para um dado dia da semana
    @client.on(events.NewMessage(pattern=f'(?i)\/[a-z]+'))
    async def handler(event, client=client):

        entidade = await client.get_entity(canal)

        # Escolhe o dia da semana
        if 'segunda' in str(event.raw_text).lower():
            dia = 'Segunda'
        elif 'terça' in str(event.raw_text).lower():
            dia = 'Terça'
        elif 'quarta' in str(event.raw_text).lower():
            dia = 'Quarta'
        elif 'quinta' in str(event.raw_text).lower():
            dia = 'Quinta'
        elif 'sexta' in str(event.raw_text).lower():
            dia = 'Sexta'
        elif 'sábado' in str(event.raw_text).lower():
            dia = 'Sábado'
        elif 'domingo' in str(event.raw_text).lower():
            dia = 'Domingo'
        elif 'hoje' in str(event.raw_text).lower():
            dia = hoje.split('-')[0]
        else:
            dia = None
        
        
        if dia:

            # Envias as mensagens
            mensagens = mensagem_formatada(dia=dia, doc_key=doc_key, sheet_name=sheet_name)
            for mensagem in mensagens:
                await client.send_message(canal, mensagem)

            # Pega os ids do comando passado 
            ids = [mensagem.id async for mensagem in client.iter_messages(entidade) if dia.lower() in str(mensagem.raw_text)]
            await client.delete_messages(canal, ids)

    print('==> Iniciando o bot')
    client.start()
    client.run_until_disconnected()