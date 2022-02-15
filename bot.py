import discord
from discord.ext import commands
import lib
from dotenv import load_dotenv
import os

load_dotenv()


intents = discord.Intents().all()
prefix = "ping!"
client = commands.Bot(prefix, intents=intents, help_command=None)
token = os.environ.get("token")
curversion = "1.1.2"

terms_file = lib.load_mem("terms.json")


@client.event
async def on_ready():
    game = discord.Game("Github: https://github.com/Kuukyo/relay_bot")
    await client.change_presence(activity=game)
    print("Bot ready.")


@client.event
async def on_message(msg):
    if msg.content.startswith(prefix) or msg.author.bot:
        await client.process_commands(msg)
        return

    if msg.guild.id != int(os.environ.get("guild_id")):
        return
    for term in terms_file:
        if term in msg.content.lower():
            for user_id in terms_file[term]:
                channel = await client.fetch_user(user_id)
                await channel.send(f"Triggered term: `{term}`\n{msg.author.mention}: {msg.content}\n{msg.jump_url}")


@client.command(pass_context=True)
async def version(ctx):
    global curversion
    embed = discord.Embed(title="Version", color=0xb434eb)
    embed.add_field(name="Version", value=curversion)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def help(ctx):
    embed = discord.Embed(color=0xb434eb)
    embed.add_field(name=prefix + "list", value="Lists all the whitelisted terms of the user.", inline=False)
    embed.add_field(name=prefix + "add <terms>", value="Adds terms to the list of whitelisted terms of the user. Example: <ping!add apple banana> adds 'apple' and 'banana' to the whitelisted terms", inline=False)
    embed.add_field(name=prefix + "remove <terms>", value="Removes terms from list of whitelisted terms of the user.", inline=False)
    embed.add_field(name=prefix + "blacklist <id>", value="Adds user id to the blacklist.", inline=False)
    embed.add_field(name=prefix + "whitelist <id>", value="Removes user id from the blacklist.", inline=False)
    embed.add_field(name=prefix + "show_blacklist", value="Shows all blacklisted user ids", inline=False)
    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def add(ctx, *terms):
    user_id = ctx.message.author.id
    file = lib.load_mem("terms.json")
    for term in terms:
        if term.lower() not in file:
            file[term.lower()] = [user_id]
        else:
            if user_id not in file[term.lower()]:
                file[term.lower()].append(user_id)

    global terms_file
    terms_file = file
    lib.dump_mem(file, "terms.json")
    await ctx.send("Term(s) has/have been added.")


@client.command(pass_context=True)
async def remove(ctx, *terms):
    user_id = ctx.message.author.id
    file = lib.load_mem("terms.json")
    for term in terms:
        if term.lower() in file:
            file[term.lower()].remove(user_id)
            if len(file[term.lower()]) == 0:
                del file[term.lower()]

    global terms_file
    terms_file = file
    lib.dump_mem(file, "terms.json")
    await ctx.send("Term(s) have been removed.")


@client.command(pass_context=True)
async def list(ctx):
    user_id = ctx.message.author.id
    new_list = []
    for term in terms_file:
        if user_id in terms_file[term]:
            new_list.append(term)

    await ctx.send(new_list)


@client.command()
async def blacklist(ctx, id_str):
    if ctx.message.author.id != int(os.environ.get("op")):
        await ctx.send("You don't have permission to use this command.")
        return

    id = int(id_str)
    blacklist_data = lib.load_mem("blacklist.json")
    guild_id_str = str(ctx.message.guild.id)
    if guild_id_str not in blacklist_data:
        blacklist_data[guild_id_str] = {"blacklisted": []}
        lib.dump_mem(blacklist_data, "blacklist.json")
    blacklisted_ids = blacklist_data[guild_id_str]["blacklisted"]
    if id in blacklisted_ids:
        await ctx.send("ID already in blacklist.")
        return

    blacklist_data[guild_id_str]["blacklisted"].append(id)
    lib.dump_mem(blacklist_data, "blacklist.json")
    await ctx.send("ID has been added to blacklist.")


@client.command()
async def whitelist(ctx, id_str):
    if ctx.message.author.id != int(os.environ.get("op")):
        await ctx.send("You don't have permission to use this command.")
        return

    id = int(id_str)
    blacklist_data = lib.load_mem("blacklist.json")
    guild_id_str = str(ctx.message.guild.id)
    if guild_id_str not in blacklist_data:
        blacklist_data[guild_id_str] = {"blacklisted": []}
    blacklisted_ids = blacklist_data[guild_id_str]["blacklisted"]
    if id not in blacklisted_ids:
        await ctx.send("ID not in blacklist.")
        return

    blacklist_data[guild_id_str]["blacklisted"].remove(id)
    lib.dump_mem(blacklist_data, "blacklist.json")
    await ctx.send("ID has been removed from blacklist.")
    try:
        user = await client.fetch_user(id)
        await ctx.guild.unban(user)
        await ctx.send("Ban has been revoked.")
    except:
        pass


@client.command()
async def show_blacklist(ctx):
    if ctx.message.author.id != int(os.environ.get("op")):
        await ctx.send("You don't have permission to use this command.")

    blacklist_data = lib.load_mem("blacklist.json")
    guild_id_str = str(ctx.message.guild.id)
    if guild_id_str not in blacklist_data:
        blacklist_data[guild_id_str] = {"blacklisted": []}

    blacklisted_ids = blacklist_data[guild_id_str]["blacklisted"]

    await ctx.send(blacklisted_ids)


@client.event
async def on_member_join(member):
    blacklist_data = lib.load_mem("blacklist.json")
    server = member.guild
    guild_id_str = str(server.id)
    if guild_id_str not in blacklist_data:
        blacklist_data[guild_id_str] = {"blacklisted": []}

    blacklisted_ids = blacklist_data[guild_id_str]["blacklisted"]

    if member.id in blacklisted_ids:
        mention = member.mention
        await member.ban()
        op = await client.fetch_user(int(os.environ.get("op")))
        await member.send("You have been pre-emptively removed from this server due to suspicious activity. Please DM Nilla#5478 if you feel this is an error.")
        await op.send(f"{mention} has been banned.")


client.run(token, reconnect=True)
