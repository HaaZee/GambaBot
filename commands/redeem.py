import nextcord
from nextcord.ext import commands
import requests
import os

headers={"X-Riot-Token": str(os.getenv("RIOT_KEY")),
                                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                                    "Accept-Language": "en-US,en;q=0.9",
                                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                                    "Origin": "https://developer.riotgames.com"} 

def apiHelper(username):
    res = requests.get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+username, headers=headers)
    resJson = res.json()
    puuid = resJson['puuid']
    getMatches = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+str(puuid)+"/ids?start=0&count=20", headers=headers)
    lastGameID = getMatches.json()[0] # 0 is the last game played
    lastGameStats = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+lastGameID, headers=headers)
    stats = filter(lambda participant : participant["puuid"] == puuid,lastGameStats.json()["info"]["participants"])
    return map(lambda stat : ("Kills"+ stat["kills"] + " :: Deaths " + stat["deaths"] + " => +500 for Win ") ,stats)

class redeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="redeem", description="Redeem League win for points!")
    async def redeem(self, interaction : nextcord.Interaction, lolusername: str = nextcord.SlashOption(name="lolusername")):
        apiHelper(lolusername)
        await interaction.send("Hi")

def setup(bot: commands.Bot):
    bot.add_cog(redeem(bot))