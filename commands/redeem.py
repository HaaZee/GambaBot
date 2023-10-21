import nextcord
from nextcord.ext import commands
import requests
import os

headers={"X-Riot-Token": str(os.getenv("RIOT_KEY")),
                                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                                    "Accept-Language": "en-US,en;q=0.9",
                                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                                    "Origin": "https://developer.riotgames.com"} 

def queryRiotForGameData(username):
    summonerData = requests.get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+username, headers=headers)
    summonerDataJson = summonerData.json()
    puuid = summonerDataJson['puuid']
    getMatches = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+str(puuid)+"/ids?start=0&count=20", headers=headers)
    lastGameID = getMatches.json()[0] # 0 is the last game played
    lastGameStats = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/"+lastGameID, headers=headers)
    stats = filter(lambda participant : participant["puuid"] == puuid,lastGameStats.json()["info"]["participants"])
    return list(map(lambda stat : {"gold": stat["goldEarned"], "win": stat["win"], "pentaKills": stat["pentaKills"] },stats))

class redeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="redeem", description="Redeem League win for points!")
    async def redeem(self, interaction : nextcord.Interaction, lolusername: str = nextcord.SlashOption(name="lolusername")):
        coinsData = self.supabase.table('Users').select("coins").eq("id", interaction.user.id).execute().data
        riotData = queryRiotForGameData(lolusername)[0]
        comment = ""
        if (riotData["win"] == True):
            comment = "Awarding 10% of your match gold for a win! \n New Balance is now " + str(int((riotData["gold"] * 0.1)) + coinsData[0]["coins"])
            x = self.supabase.table('Users').update(int((riotData["gold"] * ((riotData["pentaKills"] / 10) + 0.1))) + coinsData[0]["coins"]).eq('id', interaction.user.id).execute() # This isnt updating table?
        else:
            comment = "You lost L"

        await interaction.send(comment)

def setup(bot: commands.Bot):
    bot.add_cog(redeem(bot))