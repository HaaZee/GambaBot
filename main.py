import nextcord
from nextcord.ext import commands
import time
import os
from supabase import create_client

class SupabaseClient(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(url, key)
    
    def getClient(self):
        return self.supabase

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, command_prefix="/") # Doesn't work?
bot.add_cog(SupabaseClient(bot))
supabase = bot.get_cog('SupabaseClient').getClient()

extensions = [
    "commands.bal",
    "commands.baltop",
    "commands.cf",
    "commands.pay",
    "commands.stats",
    "commands.help" # FIXME: This doesn't return any commands when ti runs
]

bot.load_extensions(extensions)

@bot.event
async def on_ready():
    print("Bot is logged in successfully. Running on servers:\n")
    [(lambda g: print("  - %s (%s)" % (g.name, g.id)))(g) for g in bot.guilds]
    await bot.change_presence(activity=nextcord.Game(name=f"/help"))

@bot.event
async def on_member_join(member):
    TryAddMemberToDB(member)
    if not member.bot:
        memberData = {'id': member.id, 'created_at': time.localtime}
        supabase.table('Users').upsert(memberData).execute()

@bot.event
async def on_message(message):
    TryAddMemberToDB(message.author) # Store a local cache so you dont have to query on every message? 

def TryAddMemberToDB(member):
    if not member.bot:
        data = supabase.table('Users').select("*").eq("id", member.id).execute()
        if len(data.data) > 0:
            return False
        
        created_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        memberData = {'id': member.id, 'created_at': created_at}
        supabase.table('Users').insert(memberData).execute()
        
bot.run(os.getenv("DISCORD_TOKEN"))

