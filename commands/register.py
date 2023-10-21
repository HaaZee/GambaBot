import nextcord
from nextcord.ext import commands
import requests
import os

headers={"X-Riot-Token": str(os.getenv("RIOT_KEY")),
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://developer.riotgames.com"} 

def getPlayerPuuid(username):
    summonerData = requests.get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+username, headers=headers)
    summonerDataJson = summonerData.json()

    if "status" in summonerDataJson:
        if (summonerDataJson["status"]["status_code"] == 404):
            return 404 # when username not found it returns 404, so we create an error
        
    puuid = summonerDataJson['puuid']
    return puuid

class register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="register", description="Register Discord with League Account!")
    async def register(self, interaction : nextcord.Interaction, lolusername: str = nextcord.SlashOption(name="lolusername")):
        playerPuuid = getPlayerPuuid(lolusername)

        if(playerPuuid == 404):
            await interaction.send("Error: Username not found, try again with correct Username")
            return

        databaseEntryLeagueId = self.supabase.table('Users').select("league_uuid").eq("id", interaction.user.id).execute().data

        if (databaseEntryLeagueId[0]["league_uuid"] == None):
            updatedDbCol = {}
            updatedDbCol["league_uuid"] = playerPuuid
            self.supabase.table('Users').update(updatedDbCol).eq('id', interaction.user.id).execute()
            await interaction.send("Registered uuid: " + playerPuuid)
        else:
            await interaction.send("Error: You are already Registered!")


def setup(bot: commands.Bot):
    bot.add_cog(register(bot))