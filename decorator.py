from discord.ext import commands

# List of allowed user IDs
ALLOWED_USER_IDS = [1129480407629434970, 1262810154563534931]  # Replace with actual user IDs

def is_allowed_user():
    def predicate(ctx):
        if ctx.author.id in ALLOWED_USER_IDS:
            return True
        else:
            return False
    return commands.check(predicate)
