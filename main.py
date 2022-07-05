import asyncpraw
import time
import re
import discord
from discord.ext import commands, tasks
import os
import sys
from replit import db
from keep_alive import keep_alive
import psutil
chars = ["[", "]", "(", ")"]
reddit_id = os.environ['reddit_id']
reddit_token = os.environ['reddit_token']

reddit = asyncpraw.Reddit(
		client_id = reddit_id,
    client_secret = reddit_token,
		user_agent = "widici",
    heck_for_async = False
)

client = commands.Bot(command_prefix='?')
global permissionembed
permissionembed = discord.Embed(title = "Sorry you can't use this command", color = discord.Color.red())

@client.event
async def on_ready():
		global starttime
		starttime = time.time()
		print("Hello world! :D")
		await client.change_presence(status=discord.Status.idle, activity=discord.Game(db["status"]))
		
@client.command()
async def runtime(ctx):
	timepassed = (round(time.time() - starttime))
	seconds = timepassed % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
      
	totaltime = ("%d:%02d:%02d" % (hour, minutes, seconds))
	
	timeembed = discord.Embed(title = totaltime, color = discord.Color.red())
	await ctx.channel.send(embed = timeembed)

@client.command()
async def ping(ctx):
	pingembed = discord.Embed(title = f"{round(client.latency * 1000)} ms", color = discord.Color.red())
	await ctx.channel.send(embed = pingembed)

@client.command()
async def posts(ctx):
	posts = db["posts"]
	postembed = discord.Embed(title = f"{posts}", color = discord.Color.red())
	await ctx.channel.send(embed = postembed)

@client.command()
async def stats(ctx):
	statembed = discord.Embed(color = discord.Color.red())
	statembed.add_field(name = "CPU Usage", value = f"{psutil.cpu_percent()}%", inline = False)
	statembed.add_field(name = "RAM Usage", value = f"{psutil.virtual_memory().percent}%", inline = False)
	await ctx.channel.send(embed = statembed)

@client.command()
async def status(ctx, *args):
	if ctx.message.author.id == 532561774013054976:
		text = (' '.join(ctx.message.content.split()[1:]))
		db["status"] = text
		await client.change_presence(status=discord.Status.idle, activity=discord.Game(db["status"]))
		statusembed = discord.Embed(title = f"Client status has been set to [ {text} ]", color = discord.Color.red())
		await ctx.send(embed = statusembed)
	else:
		await ctx.send(embed = permissionembed)

@client.command()
async def shutdown(ctx):
	if ctx.message.author.id == 532561774013054976:
		shutdownembed = discord.Embed(title = "Client shutting down...", color = discord.Color.red())
		await ctx.channel.send(embed = shutdownembed)
		sys.exit(1)
	else:
		await ctx.send(embed = permissionembed)

@tasks.loop(minutes = 15)
async def search():
		await client.wait_until_ready()
		subreddit = await reddit.subreddit("FreeGameFindings")
		async for submission in subreddit.new(limit=10):
				minutes = (time.time() - submission.created_utc) / 60
				if minutes <= 15:

						has_all = all([char in submission.title for char in chars])

						if has_all:

								db["posts"] = db["posts"] + 1

								txt = submission.title

								split = txt.split(") ")

								txt = txt.replace("[", "txt")
								txt = txt.replace("]", "txt")
								txt = txt.replace("(", "txt")
								txt = txt.replace(")", "txt")

								res = re.findall("txt(.*?)txt", txt, re.DOTALL)

								store = res[0]
								type = res[1]
								game = split[1]

								channel = client.get_channel(986982843882291260)

								embed = discord.Embed(title = game, color = discord.Color.red(), url = submission.url)
								embed.set_thumbnail(url = ("https://www.tidningenhalsa.se/wp-content/uploads/2022/03/paprika-nyttigt.jpg"))

								embed.add_field(name = "Game info:", value = f"Store: {store}, Type: {type}", inline = False)
								
								embed.add_field(name = "Post info:", value = f"Credit: u/{submission.author}, Upvotes: {submission.score}", inline = False)
				
								await channel.send(embed = embed)

search.start()
keep_alive()
try:
	client.run(os.environ['token'])
except:
	print("Client has restarted")
	os.system("python restarter.py")
	os.system("kill 1")