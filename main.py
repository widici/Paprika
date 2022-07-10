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


class Help(commands.MinimalHelpCommand):
		async def send_pages(self):
				destination = self.get_destination()
				for page in self.paginator.pages:
						emby = discord.Embed(description=page, color = discord.Color.red())
						await destination.send(embed=emby)
		async def send_command_help(self, command):
				embed = discord.Embed(title=self.get_command_signature(command), color = discord.Color.red())
				embed.add_field(name="Help", value=command.help)
				alias = command.aliases
				if alias:
					embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

				channel = self.get_destination()
				await channel.send(embed=embed)

client.help_command = Help()

@client.command(name="posts", help="Shows number of posts client has recorded", aliases=["submissions"])
async def posts(ctx):
	posts = db["posts"]
	postembed = discord.Embed(title = f"{posts}", color = discord.Color.red())
	await ctx.channel.send(embed = postembed)

@client.command(name="stats", help="Shows statistics about client's performance", aliases=["statistics", "cpu", "ram", "ping", "runtime", "uptime"])
async def stats(ctx):
	timepassed = (round(time.time() - starttime))
	seconds = timepassed % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	totaltime = ("%d:%02d:%02d" % (hour, minutes, seconds))

	ramtext = f" (□□□□□□□□□□), {psutil.virtual_memory().percent}% ({round(psutil.virtual_memory().percent / 100, 2) * 1024} MB)"
	ramtext = ramtext.replace("□", "■", round(psutil.virtual_memory().percent / 10))

	cpu_percent = psutil.cpu_percent()
	cputext = f" (□□□□□□□□□□), {cpu_percent}%"
	cputext = cputext.replace("□", "■", round(cpu_percent / 10))
	
	statembed = discord.Embed(color = discord.Color.red())
	statembed.add_field(name = "CPU Usage", value = cputext, inline = False)
	statembed.add_field(name = "RAM Usage", value = ramtext, inline = False)
	statembed.add_field(name = "Runtime", value = totaltime, inline = False)
	statembed.add_field(name = "Ping", value = f"{round(client.latency * 1000)} ms", inline = False)
	await ctx.channel.send(embed = statembed)

@client.command(help="Changes client status")
async def status(ctx, *args):
	if ctx.message.author.id == 532561774013054976:
		text = (' '.join(ctx.message.content.split()[1:]))
		db["status"] = text
		await client.change_presence(status=discord.Status.idle, activity=discord.Game(db["status"]))
		statusembed = discord.Embed(title = f"Client status has been set to [ {text} ]", color = discord.Color.red())
		await ctx.send(embed = statusembed)
	else:
		await ctx.send(embed = permissionembed)

@client.command(help="Shuts down client")
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