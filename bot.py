import discord
from discord.ext import commands
import random
import asyncio


DISCORD_TOKEN = "discord_token_here"
QUOTES_FILE = "quotes.txt"

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

@bot.event
async def on_ready():
    # change the presence
    await bot.change_presence(activity=discord.Game(f"Recording history..."))

@bot.command(name="quote")
async def handle_get_quote(ctx, *, expr=None):
    # let's make it look like the bot is working
    await ctx.channel.trigger_typing()

    quote_list = []
    # open file to memory & select matching quotes
    if not expr: 
        with open(QUOTES_FILE) as quote_file:
            quote_list = [line.strip() for line in quote_file]
    else:
        with open(QUOTES_FILE) as quote_file:
            quote_list = [line.strip() for line in quote_file if expr.lower() in line.strip().lower()]


    # exit early if we had no matching quote
    if len(quote_list) == 0:
        await ctx.channel.send("Error: Unable to find quote!")
        return
    
    # send a matching quote at random
    quote = random.choice(quote_list).replace("\\n", "\n")
    await ctx.channel.send(f"{quote}")


@bot.command(name="addquote")
async def handle_add_quote(ctx, *, quote):

    # parse newlines
    quote = "\\n".join(quote.split("\n"))

    # append quote to end of file
    with open(QUOTES_FILE, 'a') as quote_file:
        quote_file.write(f"{quote}\n")
    await ctx.message.add_reaction("✅")



@commands.has_permissions(manage_messages=True)
@bot.command(name="delquote")
async def handle_del_quote(ctx, *, quote_to_delete=None):

    # define emoji check
    def check(reaction, user):
        return user == ctx.message.author and str(reaction.emoji) == "✅"

    # let's make it look like the bot is working
    await ctx.channel.trigger_typing()

    # exit early if passed no argument
    if not quote_to_delete:
        await ctx.channel.send("Error: no quote given!")
        return

    # parse newlines
    quote_to_delete = "\\n".join(quote_to_delete.split("\n"))

    # open file to memory
    with open(QUOTES_FILE) as quote_file:
        quote_list = [line.strip() for line in quote_file]

    # search for quotes matching criteria
    selected_quotes = []
    for index, quote in enumerate(quote_list):
        if quote_to_delete.lower() in quote.lower():
            selected_quotes.append((index, quote))
    
    # no quote found
    if len(selected_quotes) == 0:
        await ctx.channel.send("No quote was found!")
    
    # found the exact quote we want
    elif len(selected_quotes) == 1:

        # parse newlines
        selected_quote = "\n".join(selected_quotes[0][1].split("\\n"))

        # let's confirm if we want to delete the quote
        embed = discord.Embed(title="Are you sure you want to delete this quote?", description=selected_quote, color=0xff0000)
        sent = await ctx.channel.send(embed=embed)
        await sent.add_reaction("✅")

        try:
            await bot.wait_for("reaction_add", timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await sent.delete()
            await ctx.channel.send("Delete canceled: timed out.")
        else:
            await sent.delete()

            quote_list.pop(selected_quotes[0][0])

            # rewrite the quote file (yikes! but it's ok because using this command is rare (hopefully))
            with open(QUOTES_FILE, "w") as quote_file:
                for quote in quote_list:
                    quote_file.write(f"{quote}\n")

            await ctx.message.add_reaction("✅")

    # found multiple quotes
    elif len(selected_quotes) <= 5:
        embed = discord.Embed(title="Multiple quotes found", color=random.randint(0, 0xffffff))
        for index, quote in enumerate(selected_quotes):
            embed.add_field(name=f"Quote {index+1}", value=quote[1])
        await ctx.channel.send(embed=embed)

    # found a LOT of quotes
    else:
        await ctx.channel.send("Too many quotes matched!")

# reconnect=True for auto reconnect
bot.run(DISCORD_TOKEN, reconnect=True)