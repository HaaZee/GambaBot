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


def preventDoubleClaimAndUpdateLastGame(username, supabase, interaction):
     # check last game id in db
        # if none update to lastgameID
        # if same as current then return error
        # if not same as current then update and continue
    summonerData = requests.get("https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+username, headers=headers)
    summonerDataJson = summonerData.json()
    puuid = summonerDataJson['puuid']
    getMatches = requests.get("https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/"+str(puuid)+"/ids?start=0&count=20", headers=headers)
    lastGameID = getMatches.json()[0] # 0 is the last game played

    databaseLastGame = supabase.table('Users').select("previous_league_game_id").eq("id", interaction.user.id).execute().data[0]

    if (databaseLastGame["previous_league_game_id"] == lastGameID):
        return True

    newDbPrevGameStatus = {}
    newDbPrevGameStatus["previous_league_game_id"] = lastGameID
    supabase.table('Users').update(newDbPrevGameStatus).eq('id', interaction.user.id).execute()
    return False


def getUsernameFromUuid(uuid):
    response = requests.get("https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/"+uuid, headers=headers)
    username = response.json()
    return username["gameName"]

def updatePlayerCoins(supabase, interaction, riotData, coinsData):
    newPlayerCoinsValue = {}
    newPlayerCoinsValue["coins"] = int((riotData["gold"] * ((riotData["pentaKills"] / 10) + 0.1))) + coinsData[0]["coins"]
    supabase.table('Users').update(newPlayerCoinsValue).eq('id', interaction.user.id).execute()

class redeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="redeem", description="Redeem League win for points!")
    async def redeem(self, interaction : nextcord.Interaction):
        coinsData = self.supabase.table('Users').select("coins").eq("id", interaction.user.id).execute().data
        playerUuid = self.supabase.table('Users').select("league_uuid").eq("id", interaction.user.id).execute().data

        if (playerUuid[0]["league_uuid"] == None):
            await interaction.send("Error: Use /register <LeagueUsername> to register discord and league")
            return

        lolusername = getUsernameFromUuid(playerUuid[0]["league_uuid"])
        if (preventDoubleClaimAndUpdateLastGame(lolusername, self.supabase, interaction)):
            await interaction.send("Error: Can't Redeem the same game twice")
            return

        riotData = queryRiotForGameData(lolusername)[0]
        message = ""

        if (riotData["win"] == True):
            message = f"Awarding 10% of your {riotData['gold']} match gold for a win! \n New Balance is now " + str(int((riotData["gold"] * 0.1)) + coinsData[0]["coins"])
            updatePlayerCoins(self.supabase,interaction,riotData,coinsData)
        else:
            message = "You lost L"

        await interaction.send(message)

        

def setup(bot: commands.Bot):
    bot.add_cog(redeem(bot))