# This example requires the 'message_content' intent.
import asyncio


import discord
from api import api, bot_token
from request import test_request_risk, test_request

# api_key = bot_token
api_key = api

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# lista


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    risk_level_test = 'Moderate'
    if message.author == client.user:
        return

    if message.content.startswith('!ojo'):
        await message.channel.send('Por favor, proporciona el nivel de riesgo (por ejemplo, `Moderate`):')

        def check(m):
            return m.author == message.author and m.channel == message.channel

        try:
            response = await client.wait_for('message', check=check)  # Espera la respuesta por 30 segundos
            risk_level = response.content.strip()
            risk_level_test = risk_level
            await message.channel.send(f'Ojo con el riesgo. Nivel de riesgo actual:{risk_level}')
        except asyncio.TimeoutError:
            await message.channel.send('Tiempo de espera agotado. Por favor, intenta de nuevo.')

    try:
        await message.channel.send('Por favor espere')

        test_request_risk(risk_level_test)
        report = test_request()

        spy_message = f"**SPY Portfolio**\n"
        spy_message += f"Start Period: {report['SPY']['StartPeriod']}\n"
        spy_message += f"End Period: {report['SPY']['EndPeriod']}\n"
        spy_message += f"RiskFreeRate: {report['SPY']['RiskFreeRate']}\n"
        spy_message += f"TimeInMarket: {report['SPY']['TimeInMarket']}\n"
        spy_message += f"CumulativeReturn: {report['SPY']['CumulativeReturn']}\n"

        portfolio_message = f"**User Portfolio**\n"
        portfolio_message += f"Start Period: {report['Portfolio']['StartPeriod']}\n"
        portfolio_message += f"End Period: {report['Portfolio']['EndPeriod']}\n"
        portfolio_message += f"RiskFreeRate: {report['Portfolio']['RiskFreeRate']}\n"
        portfolio_message += f"TimeInMarket: {report['Portfolio']['TimeInMarket']}\n"
        portfolio_message += f"CumulativeReturn: {report['Portfolio']['CumulativeReturn']}\n"
        await message.channel.send(spy_message)
        await message.channel.send(portfolio_message)

    except asyncio.TimeoutError:
        await message.channel.send('Tiempo de espera agotado. Por favor, intenta de nuevo.')


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game('Tirando notas'))


client.run(api_key)
