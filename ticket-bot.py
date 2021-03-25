# -*- coding: utf-8 -*-

"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2020-2025 mEDE
:license: MIT, see LICENSE for more details.

"""

import discord
from discord.ext import commands, tasks
import time
from discord.utils import get
import random
import asyncio
import requests
import os
import json
import datetime
import pymongo
import pandas as pd

with open("config.json", encoding="utf-8") as file:
    config = json.load(file)

colors = [0x0062ff, 0x00ff33, 0xffd500, 0xff0000, 0x00d9ff, 0xc800ff]
TOKEN = config['token']
intents = discord.Intents().all()
client = commands.Bot(command_prefix=config['prefix'], intents=intents)
client.remove_command('help')

# DataBase Parts

@client.event
async def on_ready():
    check_cdowns.start()
    # await client.change_presence(status=discord.Status.online, activity=discord.Game(name=f'Ticket Bot'))
    print('Bot Running....')


@tasks.loop(seconds=1)
async def check_cdowns():
    with open('command_cooldown.json') as file:
        cdowns = json.load(file)
    for _id in cdowns:
        if cdowns[_id] == 0:
            continue
        else:
            cdowns[_id] -= 1
    with open('command_cooldown.json', 'w') as file:
        json.dump(cdowns, file)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        pass
    await client.process_commands(message)


@client.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    emoji = payload.emoji
    with open("config.json", encoding="utf-8") as file:
        config = json.load(file)
    static_message = config['static_message']
    if message_id == static_message:
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, client.guilds)
        current_channel = discord.utils.find(
            lambda c: c.id == payload.channel_id, guild.text_channels)
        member = discord.utils.find(
            lambda m: m.id == payload.user_id, guild.members)
        if emoji.name == '📩':
            with open('command_cooldown.json') as file:
                cdowns = json.load(file)
            if cdowns[str(payload.user_id)] == 0:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    member: discord.PermissionOverwrite(view_channel=True)
                }
                config['channel_count'] += 1
                with open('config.json', 'w') as file:
                    json.dump(config, file)
                channel = await guild.create_text_channel(f'ticket-{config["channel_count"]}', overwrites=overwrites)
                embed = discord.Embed(color=random.choice(
                    colors), description=f'**Şikayetini yazmak için {channel.mention} kanalına gidiniz.**')
                info_msg = await current_channel.send(embed=embed)
                msg = await current_channel.fetch_message(payload.message_id)
                await msg.remove_reaction(payload.emoji, member)
                cdowns[str(payload.user_id)] += 1200
                with open('command_cooldown.json', 'w') as file:
                    json.dump(cdowns, file)
                admin = discord.utils.find(
                    lambda m: m.id == 799003719982907422, guild.roles)
                await channel.send(f"**{member.mention}|{admin.mention} Merhaba Destek ekibi seninle en kısa sürede ilgilencektir.**")
                embed = discord.Embed(color=random.choice(
                    colors), description=f'Şikayet')
                await asyncio.sleep(10)
                await info_msg.delete()
            else:
                channel = client.get_channel(payload.channel_id)
                msg = await channel.fetch_message(payload.message_id)
                await msg.remove_reaction(payload.emoji, member)
        else:
            channel = client.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            await msg.remove_reaction(payload.emoji, member)


@client.event
async def on_member_join(member):
    with open('command_cooldown.json') as file:
        cdowns = json.load(file)
    cdowns[member.id] = 0
    with open('command_cooldown.json', 'w') as file:
        json.dump(cdowns, file)


@client.command()
async def msg(ctx):
    await ctx.message.delete()
    embed = discord.Embed(color=random.choice(colors), title='Destek Talebi',
                          description='**Destek talebi oluşturmak için lütfen emojiye tıklayın [:envelope_with_arrow:]**')
    message = await ctx.send(embed=embed)
    await message.add_reaction('📩')
    with open("config.json", encoding="utf-8") as file:
        config = json.load(file)
    config['static_message'] = message.id
    with open('config.json', 'w') as file:
        json.dump(config, file)


@client.command()
async def test(ctx):
    with open('command_cooldown.json') as file:
        cdowns = json.load(file)
    guild = discord.utils.find(lambda g: g.id == ctx.guild.id, client.guilds)
    for member in guild.members:
        cdowns[member.id] = 0
    else:
        with open('command_cooldown.json', 'w') as file:
            json.dump(cdowns, file)

client.run(TOKEN)
