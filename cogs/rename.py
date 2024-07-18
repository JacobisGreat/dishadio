import discord
import random
from discord import app_commands
from discord.ext import commands

def load_usernames(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        usernames = file.readlines()
    return [username.strip() for username in usernames]

usernames = load_usernames('data/usernames.txt')

async def rename(interaction: discord.Interaction):
    guild = interaction.guild
    member = interaction.user

    statuses = [discord.Status.online, discord.Status.idle, discord.Status.dnd]
    members_to_rename = [member for member in guild.members if member.status in statuses and not member.bot]

    if not members_to_rename:
        await interaction.response.send_message("No members to rename.")
        return

    await interaction.response.send_message(f"Renaming {len(members_to_rename)} members...", ephemeral=True)

    for member in members_to_rename:
        current_name = member.display_name
        random_name = random.choice(usernames)
        
        if random_name != current_name:
            try:
                await member.edit(nick=random_name)
            except discord.Forbidden:
                pass
            except Exception as e:
                pass

    await interaction.followup.send("Renaming completed.")

async def setup(bot):
    bot.tree.add_command(app_commands.Command(name="rename", description="Rename members", callback=rename))
