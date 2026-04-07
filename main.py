import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from MSV import server_on
from datetime import datetime, time


LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))      # ID ห้องบันทึกเหตุการณ์

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f'✅ บอท {bot.user.name} ออนไลน์แล้ว!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)

# --- คำสั่งจัดการข้อความ (Slash Command) ---
@bot.tree.command(name="ลงแซ่", description="ลบข้อความตามจำนวนที่ระบุ")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ ลบข้อความไปทั้งหมด {len(deleted)} ข้อความเรียบร้อย!", ephemeral=True)

# ---  คำสั่งดูข้อมูลเซิร์ฟเวอร์ ---
@bot.tree.command(name="ข้อมูลวังหลวง", description="ดูข้อมูลสรุปของวังหลวง")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"ข้อมูลวังหลวง: {guild.name}", color=discord.Color.blue())
    embed.add_field(name="เจ้าของวังหลวง", value=guild.owner.mention, inline=True)
    embed.add_field(name="ข้าราชบริวารทั้งหมด", value=guild.member_count, inline=True)
    embed.add_field(name="สถาปนาวังหลวงเมื่อ", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await interaction.response.send_message(embed=embed)

# --- คำสั่งเตะผู้ใช้ (Kick) ---
@bot.tree.command(name="เนรเทศ", description="เตะสมาชิกออกจากวังหลวง")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "ไม่มีระบุ"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"เนรเทศ{member.name} สำเร็จ เหตุผล: {reason}")
    
    # ส่ง Log เข้าห้องบันทึก
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"🛡️ **LOG:** {interaction.user.name} ได้ขับไล่{member.name} | เหตุผล: {reason}")


@bot.tree.command(name="ประกาศกฎ", description="แสดงกฎระเบียบของวังหลวง")
@app_commands.checks.has_permissions(administrator=True)
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📜 กฎระเบียบวังหลวง",
        description="เพื่อให้วังหลวงมีความสงบเรียบร้อย ขอให้ทุกท่านปฏิบัติตามดังนี้:",
        color=discord.Color.red()
    )
    embed.add_field(name="ข้อที่ 1", value="ไทเฮาหอมเป็นใหญ่", inline=False)
    embed.add_field(name="ข้อที่ 2", value="รอร่างกฎหมายอยู่", inline=False)
    embed.set_footer(text="ฝ่าฝืนอาจโดนเนรเทศ")
    
    await interaction.response.send_message(embed=embed)

@bot.command()
@commands.is_owner() # เฉพาะเจ้าของบอทเท่านั้นที่ใช้ได้
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ ซิงค์คำสั่ง Slash Command เรียบร้อยแล้ว!")
    
# --- ระบบแจ้งเตือน Error ---
@clear.error
@kick.error
async def admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        # เช็คว่าถ้าเคยตอบรับไปแล้ว (defer) ให้ใช้ followup
        if interaction.response.is_done():
            await interaction.followup.send("❌ ท่านไม่มีสิทธิ์ในการใช้คำสั่งนี้ (ต้องมีสิทธิ์จัดการข้อความ/สมาชิก)!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ ท่านไม่มีสิทธิ์ในการใช้คำสั่งนี้!", ephemeral=True)


server_on()
try:
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print(f"❌ บอทไม่ยอมออนไลน์เพราะ: {e}")
