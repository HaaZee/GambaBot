import asyncio
import random
import nextcord
from nextcord.ext import commands
from nextcord.ui import *

class Bet(nextcord.ui.Modal):
    def __init__(self, placedOn, supabase):
        super().__init__("Your bet")

        self.placedOn = placedOn
        self.supabase = supabase

        self.bet = nextcord.ui.TextInput(label="Your bet amount")
        self.add_item(self.bet)
    
    async def callback(self, interaction: nextcord.Interaction):
        betValue = int(self.bet.value)
        insertRouletteData = {'id': interaction.user.id, self.placedOn: betValue}
        existingUsersData = self.supabase.table('Users').select("coins").eq("id", interaction.user.id).execute().data[0]
        if existingUsersData["coins"] < betValue:
            await interaction.send("Your bet was not made. Insufficient funds.")
            return
        
        newCoinBalance = existingUsersData["coins"] - betValue
        updateUsersData = {"coins": newCoinBalance}
        self.supabase.table('Users').update(updateUsersData).eq("id", interaction.user.id).execute().data

        existingRouletteData = self.supabase.table('Roulette').select("*").eq("id", interaction.user.id).execute().data
        if len(existingRouletteData) > 0:
            updatRouletteeData = {self.placedOn: int(existingRouletteData[0][self.placedOn]) + betValue}
            self.supabase.table('Roulette').update(updatRouletteeData).eq('id', interaction.user.id).execute()
            return
        self.supabase.table('Roulette').upsert(insertRouletteData).execute()

class roulette(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.board = ""
        self.categories = {}
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="roulette", description="Start a roulette round!")
    async def roulette(self, interaction : nextcord.Interaction):
        rouletteData = self.supabase.table('Roulette').select(f"id").neq("id", 0).execute().data
        if len(rouletteData) >= 1:
            await interaction.send("Cannot start a new roulette as one is alreday on going.")
            return

        self.SetBoardAndCategories()
        channelName = interaction.channel.name
        channel = nextcord.utils.get(interaction.guild.channels, name=channelName)
        # Add buttons
        view = View()
        first12Button = Button(style=nextcord.ButtonStyle.green, label="1st 12",row=1,custom_id="first12")
        view.add_item(first12Button)
        second12Button = Button(style=nextcord.ButtonStyle.green, label="2nd 12",row=1,custom_id="second12")
        view.add_item(second12Button)
        third12Button = Button(style=nextcord.ButtonStyle.green, label="3rd 12",row=1,custom_id="third12")
        view.add_item(third12Button)

        twoToOneAButton = Button(style=nextcord.ButtonStyle.green, label="2:1a",row=2,custom_id="twoToOneA")
        view.add_item(twoToOneAButton)
        twoToOneBButton = Button(style=nextcord.ButtonStyle.green, label="2:1b",row=2,custom_id="twoToOneB")
        view.add_item(twoToOneBButton)
        twoToOneCButton = Button(style=nextcord.ButtonStyle.green, label="2:1c",row=2,custom_id="twoToOneC")
        view.add_item(twoToOneCButton)
        first18Button = Button(style=nextcord.ButtonStyle.green, label="1-18",row=2,custom_id="first18")
        view.add_item(first18Button)
        second18Button = Button(style=nextcord.ButtonStyle.green, label="19-36",row=2,custom_id="second18")
        view.add_item(second18Button)

        evenButton = Button(style=nextcord.ButtonStyle.green, label="Even",row=3,custom_id="even")
        view.add_item(evenButton)
        redButton = Button(style=nextcord.ButtonStyle.red, label="Red",row=3,custom_id="red")
        view.add_item(redButton)
        blackButton = Button(style=nextcord.ButtonStyle.gray, label="Black",row=3,custom_id="black")
        view.add_item(blackButton)
        oddButton = Button(style=nextcord.ButtonStyle.green, label="Odd",row=3,custom_id="odd")
        view.add_item(oddButton)

        betSpecificNumberButton = Button(style=nextcord.ButtonStyle.primary, label="Specific Number",row=4,custom_id="specificNum")
        view.add_item(betSpecificNumberButton)

        message = await interaction.send(self.board, view=view)
        async def RunRoulette(interaction):
            await channel.send(f"Roulette starting in 30 seconds...")
            await asyncio.sleep(20)
            await channel.send(f"Roulette starting in 10 seconds...")
            await asyncio.sleep(10)
            # Disable all buttons
            first12Button.disabled = True
            second12Button.disabled = True
            third12Button.disabled = True
            twoToOneAButton.disabled = True
            twoToOneBButton.disabled = True
            twoToOneCButton.disabled = True
            first18Button.disabled = True
            evenButton.disabled = True
            redButton.disabled = True
            blackButton.disabled = True
            oddButton.disabled = True
            second18Button.disabled = True
            betSpecificNumberButton.disabled = True
            await message.edit(view=view)
            await channel.send(f"No more bets!")
            await asyncio.sleep(1)
            # Simulate roll
            drawn = random.randint(1,36) 
            # Calculate what columns are getting paid out
            winning_categories = [category for category, numbers in self.categories.items() if drawn in numbers]
            winning_colour = "red" if "red" in winning_categories else "black"
            await channel.send(f"The wheel rolled {winning_colour} {str(drawn)} \nWinning categories: \n{winning_categories}")
            await channel.send("Paying winners!")
            # Calculate winners
            for category in winning_categories:
                winnerData = self.supabase.table('Roulette').select(f"id, {category}").neq(category, 0).execute().data
                for winner in winnerData:
                    userData = self.supabase.table('Users').select("id, coins").eq("id", winner['id']).execute().data[0]
                    wager = winner[category]
                    updateData = {}
                    updateData["coins"] = userData["coins"] + (wager*2)
                    self.supabase.table('Users').update(updateData).eq("id", winner['id']).execute()
                    await channel.send(f"{(await self.bot.fetch_user(winner['id'])).mention} won {wager} with a winning bet on {category}. New balance: {updateData['coins']}")

            # Clear DB
            self.board = ""
            self.categories = {}
            response = self.supabase.table('Roulette').delete().neq("id", 0).execute()
            return
        
        self.bot.loop.create_task(RunRoulette(interaction))
            
        async def betButtonCallback(interaction):
            modal = Bet(interaction.data["custom_id"], self.supabase)
            await interaction.response.send_modal(modal)

        async def betSpecificNumberButtonCallback(interaction):
            # UNFINISHED.
            await interaction.send("Unfinished feature. Sorry :)")
            return
        
        first12Button.callback = betButtonCallback
        second12Button.callback = betButtonCallback
        third12Button.callback = betButtonCallback
        twoToOneAButton.callback = betButtonCallback
        twoToOneBButton.callback = betButtonCallback
        twoToOneCButton.callback = betButtonCallback
        first18Button.callback = betButtonCallback
        evenButton.callback = betButtonCallback
        redButton.callback = betButtonCallback
        blackButton.callback = betButtonCallback
        oddButton.callback = betButtonCallback
        second18Button.callback = betButtonCallback
        betSpecificNumberButton.callback = betSpecificNumberButtonCallback

    def SetBoardAndCategories(self):
        self.board = """```fix
  _____________________________________________________________________
 / |    |    |    |    |    |    |    |    |    |    |    |    ||      |
|  | (3)|  6 | (9)|(12)| 15 |(18)|(21)| 24 |(27)|(30)| 33 |(36)|| 2:1a |
|  |    |    |    |    |    |    |    |    |    |    |    |    ||      |
|  |____|____|____|____|____|____|____|____|____|____|____|____||______|
|  |    |    |    |    |    |    |    |    |    |    |    |    ||      |
|0 |  2 | (5)|  8 | 11 |(14)| 17 | 20 |(23)| 26 | 29 |(32)| 35 || 2:1b |
|  |    |    |    |    |    |    |    |    |    |    |    |    ||      |
|  |____|____|____|____|____|____|____|____|____|____|____|____||______|
|  |    |    |    |    |    |    |    |    |    |    |    |    ||      |
|  | (1)|  4 | (7)| 10 | 13 |(16)|(19)| 22 |(25)| 28 | 31 |(34)|| 2:1c |
|  |    |    |    |    |    |    |    |    |    |    |    |    ||      |
 \_|____|____|____|____|____|____|____|____|____|____|____|____||______|
      |                   |                   |                   |
      |       1st 12      |       2nd 12      |       3rd 12      |
      |                   |                   |                   |
      |___________________|___________________|___________________|
      |         |         |         |         |         |         |
      |  1 - 18 |   Even  |  (Red)  |  Black  |   Odd   | 19 - 36 |
      |         |         |         |         |         |         |
      |_________|_________|_________|_________|_________|_________|
```"""
        self.categories = {
            "first12": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "second12": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
            "third12": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
            "twoToOneA": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
            "twoToOneB": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            "twoToOneC": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
            "first18": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
            "even": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
            "red": [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36],
            "black": [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35],
            "odd": [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35],
            "second18": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        }

def setup(bot: commands.Bot):
    bot.add_cog(roulette(bot))
