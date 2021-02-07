# Quote Discord Bot

Made to handle quote files made by some eggdrop quote script from IRC (each line is a quote)

## Commands
* `!quote <query>` returns a random quote matching the query, if no query is provided, will choose a random quote from the file.
* `!addquote <quote>` adds a quote to the quote file
* `!delquote <query>` deletes a matching quote from the quote file. Only works when it matches a single quote, otherwise it will show the matching quotes up to 6, otherwise it will just error out. You will need manage messages permissions to use this comamnd.


## Running
`python3 bot.py` after you've added the `DISCORD_TOKEN` to the bot file


## TODO
Not sure if embeds are cool for IRC quotes, maybe should just convert back to the old style of `Quote: quote here...`. It's a small change in any case.