import discord 
from discord.ext import commands 
from discord import app_commands
import asyncio
import os
import wavelink
import datete


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!",intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Successfully logged in as {bot.user.name}")
    await bot.tree.sync()

    await bot.change_presence(status=discord.Status.dnd, activity=None)

# Message filter
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    bad_words = ("bsdk", "mc", "bc","randi","chut","bhosdiwala","madarchod","jhatu","ma ki chut","ma ka bhosda","ma chuda")

    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"🚫 Hey {message.author.mention}, don’t use bad words!")

    await bot.process_commands(message)


@bot.tree.command(name="ping", description="Check the bot's connection latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # Convert seconds → ms
    bot_pfp = bot.user.display_avatar.url  # Bot’s profile picture URL

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"My current latency is **{latency}ms** ⚡",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=bot_pfp)
    embed.set_footer(text=f"Requested by {interaction.user.name}")

    await interaction.response.send_message(embed=embed)
	

# Slash command: /announce
@bot.tree.command(name="announce", description="Announce a message in a specific channel")
@app_commands.describe(channel="Select a channel", message="Type your announcement message", thumbnail="select a thumbnail", role="select a role to tag")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, *, message: str, thumbnail: discord.Attachment=None, role: discord.Role=None):
    embed = discord.Embed(title="📣 **Announcement**", description=f"{message}", color=discord.Color.orange())
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    tag = ""
           
    if thumbnail:
        embed.set_thumbnail(url=thumbnail.url)
    if role:
        if role.name =="@everyone":
            tag = "@everyone"
            
        else:
            tag = role.mention
    try:
        await channel.send(content=tag,
    embed=embed)
        await interaction.response.send_message(f"✅ Announcement sent to {channel.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to send message in that channel")


@bot.tree.command(name="dm", description="DM a message to a user")
@app_commands.describe(user="Select a user", message="Enter the message to send")
async def dm(interaction: discord.Interaction, user: discord.User, *, message: str):
    embed = discord.Embed(
        title=f"📩 Message from {interaction.user.name}",
        description=message,
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Sent from {interaction.guild.name}")

    try:
        # Send the DM
        await user.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Successfully sent a DM to {user.mention}.",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            f"⚠️ Couldn't DM {user.mention} — they might have DMs turned off or blocked me.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"🚫 Error occurred: `{e}`",
            ephemeral=True
        ) 
        
        
	
	
@bot.tree.command(name="clear", description="Deletes messages from the current channel")
@app_commands.describe(amount="Enter how many messages you want to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    # Check user permission manually too
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            "🚫 You don't have permission to delete messages.",
            ephemeral=True
        )
        return  # stop execution here

    # Prevent interaction timeout
    await interaction.response.defer(ephemeral=True)

    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(
            f"🧹 Successfully deleted **{len(deleted)}** messages!",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "🚫 I don't have permission to delete messages.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(
            f"⚠️ Error occurred: `{e}`",
            ephemeral=True
        )
        
        
	
#show help menu
@bot.tree.command(name="greet",description="It will greet back the user")
async def help_menu(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}, how are you dude 🏋️")


# adds a role to selected user
@bot.tree.command(name="add_role", description="Add a selected role to a user")
@app_commands.describe(user="Select a user", role="Select a role to assign")
@app_commands.checks.has_permissions(manage_roles=True)
async def add_role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        # Try to add the role
        await user.add_roles(role)
        await interaction.response.send_message(
            f"✅ {role.name} successfully added to {user.mention}",
            ephemeral=True
        )

        # Try to DM the user
        embed = discord.Embed(
            title="📌 Role Update",
            description=f"You've been given the {role.mention} role in **{interaction.guild.name}**!",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Moderator: {interaction.user.name}")

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(
                f"⚠️ Couldn't DM {user.mention} — they have DMs disabled.",
                ephemeral=True
            )

    except discord.Forbidden:
        await interaction.response.send_message(
            "🚫 I don't have permission to manage that role. Please check my role hierarchy.",
            ephemeral=True
        )
        
        
	        
#timeout command
@bot.tree.command(name="timeout",description="gives timeout to selected user")
@app_commands.describe(user="select a user", duration="select a duration in hour", reason="enter the reason")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "no reason provided"):
    time = datetime.timedelta(hours=duration)
    try:
         await user.timeout(time, reason=reason)
         await interaction.response.send_message(f'Succsessfully muted {user.mention} for {reason}',ephemeral=True)
         embed = discord.Embed(title="⚔️ Moderation Action",
         description = f"You were muted in {interaction.guild.name} for {reason} time: {time}", 
         color = discord.Color.purple())
         embed.set_footer(text=f"action performed by {interaction.user.name}")
         await user.send(embed=embed)
    except discord.Forbidden:
         await interaction.response.send_message(f"I don't have permission to mute {user.mention}",ephemeral=True)
    except Exception as e:    
        interaction.response.send_message(f"Error occured\n",
         f"{e}",ephemeral=True)
         
        
            
@bot.tree.command(name="remove_timeout",description="removes the timeout of a user")
@app_commands.describe(user="select a user")
@app_commands.checks.has_permissions(moderate_members=True)
async def remove_timeout(interaction: discord.Interaction, user: discord.Member):
    try:
        await user.timeout(None)
        await interaction.response.send_message(
            f"✅ Removed timeout from {user.mention}.",
            ephemeral=True
        ) 
    
        embed = discord.Embed(
    title= "Timeout Removed",
    description= "fYour timeout in **{interaction.guild.name}** has been removed.",
    color=discord.Color.orange())
    
        try:
             await user.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(
                f"⚠️ Could not DM {user.mention} (DMs might be off).",
                ephemeral=True
            )
    except discord.Forbidden:
         await interaction.response.send_message(f"🚫 I don’t have permission to untimeout {user.mention}.",
            ephemeral=True
        )
	        
	        
	        
	        
#Ban
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(
    user="Select the user to ban",
    reason="Reason for banning the user"
)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    # Prevent banning the bot or server owner
    if user == interaction.user:
        await interaction.response.send_message("❌ You can’t ban yourself, genius.", ephemeral=True)
        return
    if user == interaction.guild.owner:
        await interaction.response.send_message("👑 You can’t ban the server owner.", ephemeral=True)
        return
    if user == bot.user:
        await interaction.response.send_message("😅 I can’t ban myself.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # DM the user before banning
        embed = discord.Embed(
            title="🚫 You’ve been banned!",
            description=f"You were banned from **{interaction.guild.name}**\n**Reason:** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Banned by {interaction.user.name}")

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass  # ignore if DMs are closed

        # Actually ban the user
        await user.ban(reason=f"{reason} | Action by {interaction.user.name}")

        # Confirm to moderator
        confirm_embed = discord.Embed(
            title="✅ User Banned",
            description=(
                f"**User:** {user.mention}\n"
                f"**Moderator:** {interaction.user.mention}\n"
                f"**Reason:** {reason}"
            ),
            color=discord.Color.orange()
        )
        confirm_embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send(
            "🚫 I don’t have permission to ban that user. Check my role position.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"⚠️ Unexpected error: `{e}`", ephemeral=True)
 
#invite
@bot.tree.command(name="link", description="Get the invite link to add this bot to your server")
async def link(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Invite GuardianX",
        description=(
            "Click the link below to invite **GuardianX** to your server:\n\n"
            "[➡️ Invite Link](https://discord.com/oauth2/authorize?client_id=1467519941661036678&permissions=8&integration_type=0&scope=bot+applications.commands)"
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="GuardianX — always on duty ⚔️")
    await interaction.response.send_message(embed=embed, ephemeral=True)

 
 
#kick
@bot.tree.command(name="kick", description="Kick a user from the server")
@app_commands.describe(user="Select a user", reason="Provide a reason for the kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    # Safety checks
    if user == interaction.user:
        await interaction.response.send_message("❌ You can’t kick yourself, genius.", ephemeral=True)
        return
    if user == interaction.guild.owner:
        await interaction.response.send_message("👑 You can’t kick the server owner.", ephemeral=True)
        return
    if user == bot.user:
        await interaction.response.send_message("😅 I can’t kick myself.", ephemeral=True)
        return

    # Permission check for user
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("🚫 You don’t have permission to kick members.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    try:
        # DM the user before kicking
        embed = discord.Embed(
            title="🦶 You’ve been kicked!",
            description=f"You were kicked from **{interaction.guild.name}**\n**Reason:** {reason}",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Kicked by {interaction.user.name}")

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            pass  # Ignore if their DMs are off

        # Kick the user
        await user.kick(reason=f"{reason} | Action by {interaction.user.name}")

        # Confirmation message for moderator
        confirm_embed = discord.Embed(
            title="✅ User Kicked",
            description=(
                f"**User:** {user.mention}\n"
                f"**Moderator:** {interaction.user.mention}\n"
                f"**Reason:** {reason}"
            ),
            color=discord.Color.orange()
        )
        confirm_embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send("🚫 I don’t have permission to kick that user.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Unexpected error: `{e}`", ephemeral=True)
            
            
#remove role
@bot.tree.command(name="remove_role",description="by using this command you can remove a role from a selected user")
@app_commands.describe(user="select a user",role="select a role")
@app_commands.checks.has_permissions(moderate_members=True)
async def remove_role(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    try:
        await user.remove_roles(role)
        await interaction.response.send_message("fsuccessfully removed {role.mention} from {user.mention}")
        embed = discord.Embed(
            title="📌 Role Update",
            description=f"Youre {role.name} have been removed in **{interaction.guild.name}**!",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Moderator: {interaction.user.name}")
        try:
            await user.send(embed=embed)
        except discord.Forbidden:
              await interaction.followup.send(
                f"⚠️ Couldn't DM {user.mention} — they have DMs disabled.",
                ephemeral=True
            )
      
    except discord.Forbidden:
        await interaction.response.send_message(
            "🚫 I don't have permission to manage that role. Please check my role hierarchy.",
            ephemeral=True
        )
        
       
@bot.tree.command(name="lock", description="Lock the current channel for everyone except admins")
async def lock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("🚫 You don't have permission to lock channels.", ephemeral=True)
        return

    channel = interaction.channel
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)

    try:
        await channel.set_permissions(guild.default_role, send_messages=False,
        reason = f"Requested by {interaction.user.name}")
        await interaction.followup.send("🔒 Channel locked for everyone except admins.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("🚫 I don't have permission to lock this channel.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: `{e}`", ephemeral=True)
 
 

@bot.tree.command(name="unlock", description="UnLock the current channel for everyone except admins")
async def unlock(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("🚫 You don't have permission to unlock channels.", ephemeral=True)
        return

    channel = interaction.channel
    guild = interaction.guild
    await interaction.response.defer(ephemeral=True)

    try:
        await channel.set_permissions(guild.default_role, send_messages=True,
        reason= f"Requested by {interaction.user.name}")
        await interaction.followup.send("🔒 Channel unlocked for everyone", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("🚫 I don't have permission to unlock this channel.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: `{e}`", ephemeral=True)
	        
	        
#create role
@bot.tree.command(name="create_role",description="you can create a role by using this command")
@app_commands.describe(name="enter the name of the role")
async def create_role(interaction: discord.Interaction, name: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "🚫 You don't have permission to create roles.",
            ephemeral=True
        )
        return
     
    try:
        await interaction.guild.create_role(name=name,
  reason=f"created by {interaction.user.name}")
    except discord.Forbidden:
        await interaction.followup.send("🚫 I don't have permission to Create Roles",ephemeral=True)
       
    except Exception as e:
        await interaction.followup.send(f"🚫 Error occured `{e}`")
 
 
@bot.tree.command(name="slowmode",description="Set slowmode duration for the current channel")
@app_commands.describe(seconds="Enter slowmode duration in seconds (0 to disable)")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("🚫 You don’t have permission to manage channels.", ephemeral=True)
        return
        
    if seconds < 0 or seconds > 21600:
        await interaction.response.send_message("⚠️ Slowmode must be between 0 and 21600 seconds (6 hours).", ephemeral=True)
        return
        
    await interaction.response.defer(ephemeral=True)
    
    try:
        await interaction.channel.edit(slowmode_delay = seconds)
        
        if seconds == 0:
            msg = "🟢 Slowmode disabled for this channel."
        else:
            msg = f"🐢 Slowmode set to **{seconds} seconds** for this channel."

        await interaction.followup.send(msg, ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send("🚫 I don’t have permission to change channel settings.", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"⚠️ Unexpected error: `{e}`", ephemeral=True)
        
        
# ------------------ /warn ------------------
@bot.tree.command(name="warn", description="Warn a user (3 warns = kick)")
@app_commands.describe(user="Select a user to warn", reason="Reason for the warning")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    guild = interaction.guild
    bot_member = guild.me

    # Safety checks
    if user.top_role >= bot_member.top_role:
        await interaction.response.send_message("🚫 I can’t warn this user because their role is higher or equal to mine.", ephemeral=True)
        return
    if user == interaction.user:
        await interaction.response.send_message("😅 You can’t warn yourself.", ephemeral=True)
        return

    # Load and update warnings
    warnings = load_warnings()
    guild_id = str(guild.id)
    user_id = str(user.id)
    warnings.setdefault(guild_id, {})
    warnings[guild_id][user_id] = warnings[guild_id].get(user_id, 0) + 1
    user_warns = warnings[guild_id][user_id]
    save_warnings(warnings)

    # DM Embed for user
    warn_embed = discord.Embed(
        title="⚠️ Warning Received",
        description=f"You were warned in **{guild.name}**.\n**Reason:** {reason}\n**Warnings:** {user_warns}/3",
        color=discord.Color.orange()
    )
    warn_embed.set_footer(text=f"Issued by {interaction.user.name}")

    try:
        await user.send(embed=warn_embed)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ Could not DM {user.mention} (DMs off).", ephemeral=True)

    # Moderator message
    await interaction.response.send_message(
        f"⚠️ {user.mention} warned for `{reason}`. They now have **{user_warns}/3 warnings.**",
        ephemeral=True
    )

    # Kick on 3 warnings
    if user_warns >= 3:
        try:
            kick_embed = discord.Embed(
                title="🚨 You’ve Been Kicked",
                description=f"You were kicked from **{guild.name}** after reaching **3 warnings.**",
                color=discord.Color.red()
            )
            kick_embed.set_footer(text=f"Action by {interaction.user.name}")

            try:
                await user.send(embed=kick_embed)
            except discord.Forbidden:
                pass  # ignore DM fail

            await user.kick(reason=f"Auto-kick: reached 3 warnings. Warned by {interaction.user.name}")
            warnings[guild_id][user_id] = 0
            save_warnings(warnings)

            await interaction.followup.send(f"🚨 {user.mention} was kicked for reaching 3 warnings.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("🚫 I don’t have permission to kick that user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Unexpected error: `{e}`", ephemeral=True)



# ------------------ /unwarn ------------------
@bot.tree.command(name="unwarn", description="Remove one warning from a user")
@app_commands.describe(user="Select a user to remove a warning from")
@app_commands.checks.has_permissions(moderate_members=True)
async def unwarn(interaction: discord.Interaction, user: discord.Member):
    warnings = load_warnings()
    guild_id = str(interaction.guild.id)
    user_id = str(user.id)

    if guild_id not in warnings or user_id not in warnings[guild_id]:
        await interaction.response.send_message(f"⚠️ {user.mention} has no warnings to remove.", ephemeral=True)
        return

    if warnings[guild_id][user_id] <= 0:
        await interaction.response.send_message(f"⚠️ {user.mention} already has 0 warnings.", ephemeral=True)
        return

    # Remove one warning
    warnings[guild_id][user_id] -= 1
    remaining = warnings[guild_id][user_id]
    save_warnings(warnings)

    # Embed for moderator
    embed = discord.Embed(
        title="🧹 Warning Removed",
        description=f"Removed one warning from {user.mention}.\nCurrent total: `{remaining}/3`",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Action by {interaction.user.name}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # DM the user
    dm_embed = discord.Embed(
        title="✅ Warning Reduced",
        description=f"Your warning count in **{interaction.guild.name}** was reduced by one.\nCurrent total: `{remaining}/3`",
        color=discord.Color.green()
    )
    dm_embed.set_footer(text=f"Moderator: {interaction.user.name}")

    try:
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ Could not DM {user.mention} (DMs off).", ephemeral=True)

bot.run(os.getenv("TOKEN"))
