import discord
from discord.ext import commands
import random
import asyncio


DISCORD_TOKEN = "discord_token_here"

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

@bot.event
async def on_ready():
    # change the presence
    await bot.change_presence(activity=discord.Game(f"Recording quotes..."))

@bot.command(name="quote")
async def handle_get_quote(ctx, *, expr=None):
    # let's make it look like the bot is working
    await ctx.channel.trigger_typing()

    # open file to memory
    with open("quotes.txt") as quote_file:
        quote_list = [line.strip() for line in quote_file]

    # select matching quotes
    if not expr:
        selected_quotes = quote_list
    else:
        selected_quotes = [quote for quote in quote_list if expr.lower() in quote.lower()]

        # exit early if we had no matching quote
        if len(selected_quotes) == 0:
            await ctx.channel.send("Error: Unable to find quote!")
            return
    
    # send a matching quote at random
    embed = discord.Embed(title="Quote", description=random.choice(selected_quotes), color=random.randint(0, 0xffffff))
    await ctx.channel.send(embed=embed)


@bot.command(name="addquote")
async def handle_add_quote(ctx, *, quote):
    # let's make it look like the bot is working
    await ctx.channel.trigger_typing()

    # append quote to end of file
    with open("quotes.txt", 'a') as quote_file:
        quote_file.write(f"{quote}\n")
    await ctx.channel.send("Quote added!")


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

    # open file to memory
    with open("quotes.txt") as quote_file:
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

        # let's confirm if we want to delete the quote
        embed = discord.Embed(title="Are you sure you want to delete this quote?", description=selected_quotes[0][1], color=0xff0000)
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
            with open("quotes.txt", "w") as quote_file:
                for quote in quote_list:
                    quote_file.write(f"{quote}\n")

            await ctx.channel.send("Quote deleted!")

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