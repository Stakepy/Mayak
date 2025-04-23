import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import datetime
import requests
import sqlite3

conn = sqlite3.connect("users.db")  # или путь к твоей базе, если он другой
cur = conn.cursor()

# cur.execute("ALTER TABLE users ADD COLUMN country TEXT")
conn.commit()
conn.close()

print("Готово!")

from config import TOKEN, GUILD_ID, VOICE_CHANNEL_ID, TEXT_CHANNEL_ID, MP3_FILE, OPENWEATHERMAP_API_KEY
from db import init_db, set_user_city, get_user_city, get_all_users
from weather import get_weather

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

voice_client = None

@bot.event
async def on_ready():
    print(f"✅ Запущен как {bot.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    init_db()

    await connect_to_voice()
    await play_sound()

    hourly_weather_loop.start()

async def connect_to_voice():
    global voice_client
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            if bot.voice_clients:
                await bot.voice_clients[0].disconnect(force=True)
            voice_client = await channel.connect()
            await asyncio.sleep(1)
            await play_sound()
        except Exception as e:
            print(f"Ошибка при подключении к голосовому каналу: {e}")

async def play_sound():
    global voice_client
    if voice_client and voice_client.is_connected():
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(MP3_FILE))

# Переподключение при кике или перемещении
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        if after.channel is None or after.channel.id != VOICE_CHANNEL_ID:
            await asyncio.sleep(1)
            await connect_to_voice()

# Ограничение: только в указанном текстовом канале
def is_in_designated_text_channel(interaction: discord.Interaction) -> bool:
    return interaction.channel.id == TEXT_CHANNEL_ID

# Команда: установить город и страну
@tree.command(name="city", description="Установить ваш город и страну", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(city="Введите название города", country="Введите страну")
async def set_city(interaction: discord.Interaction, city: str, country: str):
    if not is_in_designated_text_channel(interaction):
        await interaction.response.send_message("❌ Вы можете использовать эту команду только в указанном текстовом канале.", ephemeral=True)
        return

    set_user_city(interaction.user.id, city, country)  # Теперь работает с тремя аргументами
    await interaction.response.send_message(f"✅ Ваш город установлен как **{city}, {country}**.", ephemeral=True)


# Команда: текущая погода
@tree.command(name="weather", description="Показать текущую погоду", guild=discord.Object(id=GUILD_ID))
async def show_weather(interaction: discord.Interaction):
    if not is_in_designated_text_channel(interaction):
        await interaction.response.send_message("❌ Вы можете использовать эту команду только в указанном текстовом канале.", ephemeral=True)
        return

    city, country = get_user_city(interaction.user.id)
    if not city or not country:
        await interaction.response.send_message("❌ Сначала установите город и страну командой `/city <город> <страна>`.", ephemeral=True)
        return

    forecast = await get_weather(city, country)
    await play_sound()
    await interaction.response.send_message(f"📡 Погода для **{city}, {country}**:\n{forecast}", ephemeral=True)

# Отправка прогноза каждый час
@tasks.loop(seconds=1)
async def hourly_weather_loop():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)  # МСК
    if now.minute == 0 and now.second == 0:
        await play_sound()

        users = get_all_users()
        channel = bot.get_channel(TEXT_CHANNEL_ID)

        for user_id, city, country in users:
            forecast = await get_weather(city, country)
            try:
                await channel.send(f"\n────────⋆⋅☆⋅⋆────────")
                await channel.send(f"<@{user_id}> 🗼 Погода для **{city}, {country}**:\n{forecast}")
                await channel.send(f"\n────────⋆⋅☆⋅⋆────────")
            except Exception as e:
                print(f"Ошибка при отправке погоды пользователю {user_id}: {e}")

bot.run(TOKEN)
