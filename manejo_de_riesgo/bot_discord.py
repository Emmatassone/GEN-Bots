# This example requires the 'message_content' intent.
import discord
from api import api
from main import report
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# lista


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!ojo'):
#        table_markdown = report.to_markdown()

#        await message.channel.send('Ojo con el riesgo')
        #await message.channel.send(report)
        await message.channel.send(report)


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game('Tirando notas'))


client.run(api)
