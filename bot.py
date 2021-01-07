import discord
import random
import os
import youtube_dl
import wikipedia
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle
import sqlite3
from datetime import datetime
import time
import database
import json
import re
from discord.ext import commands
from database import *
import pkg_resources
import asyncio
import aiml


client = commands.Bot(command_prefix='*')
status = cycle(['Scrabble', 'Chess'])
players = {}


STARTUP_FILE = "std-startup.xml"

aiml_kernel = aiml.Kernel()
if os.path.isfile("bot_brain.brn"):
    aiml_kernel.bootstrap(brainFile="bot_brain.brn")
else:
    aiml_kernel.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
    aiml_kernel.saveBrain("bot_brain.brn")


@client.event
async def on_ready():
    # activity=discord.Game('Scrabble'))
    await client.change_presence(status=discord.Status.idle)
    change_status.start()
    print("Bot is ready!")


@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')


@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')


# @client.event
# async def on_message(message):
#     # if message.author.bot or str(message.channel) != channel_name:
#     #     return

#     if message.content is None:
#         print("Empty message received.")
#         return

#     print("Message: " + str(message.content))

#     if message.content.startswith('*'):
#         return
#     elif 'shutdown' in message.content and message.author.id == 173450781784145921:
#         await client.logout()
#     elif message.content.startswith('ask'):
#         aiml_response = aiml_kernel.respond(message.content[4:])
#         if aiml_response == '':
#             await message.channel.send("I don't have a response for that, sorry.")
#         else:
#             print(aiml_response)
#             await message.channel.send(aiml_response)


@client.command()
async def ask(ctx, *, question):
    '''
    - opens ai chatbot
    '''

    if question is None:
        print("Empty message received.")
        return

    print("Message: " + str(question))

    aiml_response = aiml_kernel.respond(question)
    if aiml_response == '':
        await ctx.send("I don't have a response for that, sorry.")
    else:
        print(aiml_response)
        await ctx.send(aiml_response)


@client.command()
async def ping(ctx):
    '''
    - Returns the Bot's response time.
    '''
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')


@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    '''
    - Magic 8-Ball trivia.
    '''
    responces = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes – definitely.',
                 'You may rely on it.',
                 'As I see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Yes.',
                 'Signs point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 "Don't count on it.",
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good.',
                 'Very doubtful.']

    await ctx.send(f':8ball:Question: {question}\n:8ball:Answer: {random.choice(responces)}')


# general error handler
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
        # await ctx.send('Invalid command used.')


@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    '''
    - Delete specified number of messages.
    '''
    await ctx.channel.purge(limit=amount)

# specific error handler


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an amount of messages to delete.')

'''
def is_it_me(ctx):
    return ctx.author.id == 604239299470426142 or 697136336582344786 or 451742374545195018
    # TEWARI - 604239299470426142
    # AKSHIT - 451742374545195018
'''


@client.command()
# @commands.check(is_it_me)
async def user(ctx):
    '''
    - Returns the username.
    '''
    await ctx.send(f'Hi! I am {ctx.author}')


@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    '''
    - Kick members from the server.
    '''
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')


@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    '''
    - Ban members from the server.
    '''
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')


@client.command()
async def unban(ctx, *, member):
    '''
    - Unban banned members from the server.
    '''
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)

            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            # same as ctx.send(f'Banned {user.mention}')
            return


@client.command()
async def load(ctx, extension):
    '''
    - Load the mentioned cogs file.
    '''
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} Loaded')


@client.command()
async def unload(ctx, extension):
    '''
    - Unload the mentioned cogs file.
    '''
    client.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} Unloaded')


@client.command()
async def reload(ctx, extension):
    '''
    - Reload the mentioned cogs file.
    '''
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} Reloaded')

# music player


@client.command(name='join', help='- Join the voice channel.')
async def join(ctx):

    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        return

    else:
        channel = ctx.message.author.voice.channel
        print(f"The bot has connected to {channel}\n")

    await channel.connect()


@client.command(pass_context=True)
async def leave(ctx):
    '''
    - Disconnect from the voice channel.
    '''

    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")


@client.command(pass_context=True)
async def play(ctx, url):
    '''
    - Play YouTube audio using URL.
    '''

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send("Getting everything ready now")

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"),
               after=lambda e: print("Song done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.1

    nname = name.rsplit("-", 2)
    await ctx.send(f"Playing: {nname[0]}")
    print("playing\n")


@client.command(pass_context=True)
async def pause(ctx):
    '''
    - Pause the playing audio.
    '''

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.command(pass_context=True)
async def resume(ctx):
    '''
    - Resume the paused audio.
    '''
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
    else:
        print("Music is not paused")
        await ctx.send("Music is not paused")


@client.command(pass_context=True)
async def stop(ctx):
    '''
    - Stop the playing audio.
    '''
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


@client.event
async def on_reaction_add(reaction, user):
    if(check_leaderboard(reaction.message.id, user.id)):
        if(reaction.emoji == u"\u25B6"):
            page, last_user_count = get_leaderboard_page(
                reaction.message.id, user.id)
            if(last_user_count < page * 10):
                return
            rows = get_users(page+1)
            embed = discord.Embed(title="Leaderboard", color=0x8150bc)
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = client.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + \
                        " | " + str(user_name)
                    embed.add_field(
                        name=user_name, value='{:,}'.format(row[2]), inline=False)
                    last_user_count += 1

            update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if(last_user_count > (page+1) * 10):
                await reaction.message.add_reaction(u"\u25B6")

        if(reaction.emoji == u"\u25C0"):
            page, last_user_count = get_leaderboard_page(
                reaction.message.id, user.id)
            if(page == 1):
                return
            rows = get_users(page-1)
            embed = discord.Embed(title="Leaderboard", color=0x8150bc)
            if(last_user_count <= page * 10):
                last_user_count -= 10 + (last_user_count-1) % 10
            else:
                last_user_count -= 20

            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = client.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + \
                        " | " + str(user_name)
                    embed.add_field(
                        name=user_name, value='{:,}'.format(row[2]), inline=False)
                    last_user_count += 1

            update_leaderboard(page - 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed=embed)
            await reaction.message.clear_reactions()
            if(page - 1 > 1):
                await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction(u"\u25B6")

    if(reaction.emoji == u"\U0001F44D"):
        roles = user.roles

        permission = False

        for role in roles:
            if(role.name == "Manager" or role.permissions.administrator):
                permission = True

        if(permission and check_requests(reaction.message.id) and not user.bot):
            users, points = get_users_requests(reaction.message.id)
            split_users = users.split()
            for user_id in split_users:
                add_points(user_id, points)

            update_requests(reaction.message.id, 1)
            await reaction.message.add_reaction('\U00002705')


@client.command(pass_context=True)
async def points(ctx, command=None, username=None, point=None):
    """- Add and remove points."""
    # print(username)
    if(command == None or point == None or username == None):
        if(command == None and point == None and username == None):
            points = get_user_point(ctx.message.author.id)
            await ctx.send("You have " + str(points) + " points")
            return
        else:
            await ctx.send("Invalid command, please check the documentation: \n!points [add/remove] <username> <points>")
            return

    roles = ctx.message.author.roles
    permission = False

    for role in roles:
        if(role.name == "Manager" or role.permissions.administrator):
            permission = True

    if(not permission):
        await request_points(ctx)
        # await ctx.send("No permission")
        return

    if(command.lower() == "add"):
        if(point.isdigit()):
            username_id = username[2:]
            username_id = username_id[:-1]
            username_id = username_id.replace("!", "")
            if(username_id.isdigit()):
                add_points(username_id, point)
            else:
                from_server = ctx.guild
                user = from_server.get_member_named(username)
                if(user == None):
                    await ctx.send("Invalid user")
                    return
                else:
                    add_points(user.id, point)
            await ctx.send("Points added!")
        else:
            await request_points()
    else:
        if(command.lower() == "remove"):
            if(point.isdigit()):
                username_id = username[2:]
                username_id = username_id[:-1]
                username_id = username_id.replace("!", "")
                if(username_id.isdigit()):
                    remove_points(username_id, point)
                else:
                    from_server = ctx.guild
                    user = from_server.get_member_named(username)
                    if(user == None):
                        await ctx.send("Invalid user")
                        return
                    else:
                        remove_points(user.id, point)
                await ctx.send("Points removed!")
            else:
                await ctx.send("Invalid points number!")
        else:
            await ctx.send("Invalid command, please check the documentation: \n!points [add/remove] <username> <points>")


@client.command(pass_context=True)
async def leaderboard(ctx):
    """- Displays the score and rank based on points system."""
    rows = get_users(1)
    embed = discord.Embed(title="Leaderboard", color=0x8150bc)
    count = 1
    for row in rows:
        if(row[1] != None and row[2] != None):
            user = client.get_user(int(row[1]))
            user = "#" + str(count) + " | " + str(user)
            embed.add_field(
                name=user, value='{:,}'.format(row[2]), inline=False)
            count += 1

    msg_sent = await ctx.send(embed=embed)
    add_leaderboard(ctx.message.author.id, msg_sent.id, count)
    if(count == 11):
        await msg_sent.add_reaction(u"\u25B6")


@client.event
async def on_message_edit(before, after):
    if(check_requests(after.id)):
        update_requests(after.id, -1)


@client.event
async def on_command_error(ctx, error):
    try:
        await request_points(ctx)
    except Exception as e:
        print("Some shit happened: " + str(error))
        print("Error from try catch : " + str(e))


@client.command(pass_context=True)
async def reset(ctx):
    """- Resets the database."""
    permission = False
    roles = ctx.message.author.roles
    for role in roles:
        if(role.permissions.administrator):
            permission = True

    if(permission):
        await reset_database()
        await ctx.send("Database was reset!")
    else:
        await ctx.send("No permision!")


async def format_user(user_name):
    for i in range(len(user_name)):
        if(user_name[i] != ' '):
            break
        else:
            user_name = user_name[1:]

    for i in user_name[::-1]:
        if(i != " "):
            break
        else:
            user_name = user_name[:-1]
    return user_name


async def request_points(ctx):
    #print("here it go")
    message_sent = ctx.message.content
    if(message_sent[:12] == "*points add "):
        message_sent = message_sent[12:]
        split_message = re.split('\s+', message_sent)
        users = ''
        # print(split_message)
        for i in range(0, len(split_message) - 1):
            users += split_message[i]
            users += ' '

        users = users[:-1]
        # print(users)
        split_users = users.split(',')
        saved_users = ''
        # print(split_users)
        for user in split_users:
            user = await format_user(user)
            # print(user)
            if(user[:1] == '"' and user[-1:] == '"'):
                user = user[1:]
                user = user[:-1]
                # print(user)
                user_id = ctx.guild.get_member_named(user)
                if(user_id == None):
                    await ctx.send("The following user does not exist: " + str(user) + "\nPlease do not use white spaces between users and commas")
                    return

                saved_users += str(user_id.id)
                saved_users += ' '
            elif(user[:1] == "<"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!", "")
                if(user.isdigit()):
                    found = client.get_user(int(user))
                else:
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                if(found == None):
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                saved_users += str(user)
                saved_users += ' '
            elif(user[-1:] == ">"):
                user = user.strip()
                user = user[2:]
                user = user[:-1]
                user = user.replace("!", "")
                if(user.isdigit()):
                    found = client.get_user(int(user))
                else:
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return

                found = client.get_user(user)
                if(found == None):
                    await ctx.send("The following user does not exist : " + str(user) + "\nPlease use comma between users!")
                    return
                saved_users += str(user)
                saved_users += ' '
            else:
                # print("Ja")
                user_id = ctx.guild.get_member_named(user)
                if(user_id == None):
                    await ctx.send("The following user does not exist : " + str(user))
                    return
                saved_users += str(user_id.id)
                saved_users += ' '

        insert_points_requests(ctx.message.id, saved_users, split_message[len(
            split_message) - 1], 0, ctx.message.author.id)

        roles = ctx.message.author.roles
        permission = False

        for role in roles:
            if(role.name == "Manager" or role.permissions.administrator):
                permission = True

        if(not permission):
            await ctx.message.add_reaction(u"\U0001F44D")
        else:
            users_req = saved_users.split()
            for user in users_req:
                add_points(user, split_message[len(split_message) - 1])
            await ctx.send("Points added")


@tasks.loop(seconds=200)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

# Insert Your Token Here (from Discord Developer Portal  https://discord.com/developers/applications)
client.run("")
