import nextcord
from nextcord.interactions import Interaction
from nextcord.ui import *
from nextcord.ext import commands

class betInput(nextcord.ui.Modal):
    def __init__(self, choice, supabase):
        super().__init__(
            "Your Bet")
        
        self.choice = choice
        self.supabase = supabase

        self.betAmount = nextcord.ui.TextInput(
            label="Bet amount",min_length=1
        )
        
        self.add_item(self.betAmount)

    async def callback(self, interaction : nextcord.Interaction):
        betValue = int(self.betAmount.value)
        insertGambleData = {'id': interaction.user.id, self.choice: betValue}
        existingUsersData = self.supabase.table('Users').select("coins").eq("id", interaction.user.id).execute().data[0]
        if existingUsersData["coins"] < betValue:
            await interaction.send("Your bet was not made. Insufficient funds.", ephemeral=True)
            return
        if self.supabase.table('customGamble').select('id').eq("owner", True).execute().data[0]['id'] == interaction.user.id:
            await interaction.send("Your bet was not made, you created this gamble!", ephemeral=True)
            return
        newCoinBalance = existingUsersData["coins"] - betValue
        updateUsersData = {"coins": newCoinBalance}
        self.supabase.table('Users').update(updateUsersData).eq("id", interaction.user.id).execute().data
        self.supabase.table('customGamble').upsert(insertGambleData).execute()
            

class Dropdown(nextcord.ui.Select):
    def __init__(self, supabase):
        self.supabase = supabase
        
        self.selectOptions = [
            nextcord.SelectOption(label="YES", description="Select if Yes won"),
            nextcord.SelectOption(label="NO", description="Select if No won")
        ]
        super().__init__(placeholder="Cashout Options", min_values=1, max_values=1, options=self.selectOptions)
    
    async def callback(self, interaction : Interaction):
        fetchWinners = self.supabase.table('customGamble').select(f"id, {self.values[0]}").neq(self.values[0], 0).execute().data
        totalWon = 0
        for winner in fetchWinners:
            userData = self.supabase.table('Users').select("id, coins").eq("id", winner['id']).execute().data[0]
            updateData = {}
            updateData['coins'] = int(userData['coins'])+ int(winner[self.values[0]])*2
            totalWon = totalWon + int((winner[self.values[0]]))
            self.supabase.table('Users').update(updateData).eq("id", winner['id']).execute()
        self.supabase.table('customGamble').delete().neq("id", 0).execute()
        await interaction.message.edit(content=f"Total Money won on this bet: {totalWon}!", view=None)
        
        
class dropdownView(nextcord.ui.View, Interaction):
    def __init__(self, supabase):
        self.supabase = supabase
        super().__init__()
        self.dropdownMenu = Dropdown(self.supabase)
        self.add_item(self.dropdownMenu)


class gamba(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supabase = self.bot.get_cog('SupabaseClient').getClient()

    @nextcord.slash_command(name="gamba", description="Create a custom bet!")
    async def ex(self, 
                 interaction : nextcord.Interaction,
                 bettitle : str = nextcord.SlashOption(name="bet_title"),
                 ):
        
        ownerInitial = {'id': interaction.user.id, 'owner' : True}
        self.supabase.table('customGamble').upsert(ownerInitial).execute()
        
        bet_message_embed = nextcord.Embed(
            title="New Bet",
            description=f"Bet: {bettitle}",
            color=nextcord.Color.blue()
        )

        # Define the Yes and No buttons
        outcome1_button = Button(style=nextcord.ButtonStyle.success, label="Yes!", disabled=False, custom_id="YES")
        outcome2_button = Button(style=nextcord.ButtonStyle.danger, label="No!", disabled=False, custom_id="NO")
        
        lock_button = Button(emoji="🔐", disabled=False, custom_id='lock')
        # Create a view that contains the buttons
        view = View(timeout=None)

        view.add_item(outcome1_button)
        view.add_item(outcome2_button)
        view.add_item(lock_button)
      
        # Send the bet message with the buttons
        unlockButton = Button(emoji="🔐", disabled=False, custom_id="unlock")
        payoutButton = Button(label="Payout", custom_id="payout")
        submitButton = Button(label="submit", disabled=True, custom_id="submit")
        
        lockedView = View(timeout=None)
        lockedView.add_item(unlockButton)
        lockedView.add_item(payoutButton)
        payoutView = dropdownView(self.supabase)
        

        await interaction.send(embed=bet_message_embed, view=view)
        
        
        async def unlock_button_callback(interaction):
            await interaction.message.edit(embed = bet_message_embed, view=view)

        async def lock_button_callback(interaction):
            if self.supabase.table('customGamble').select('id').eq("owner", True).execute().data[0]['id'] != interaction.user.id:
                await interaction.send("You cannot lock this gamble, since you didn't create it!", ephemeral=True)
                return
            await interaction.message.edit(embed = bet_message_embed, view=lockedView)

        async def payoutButton_callback(interaction):
            if self.supabase.table('customGamble').select('id').eq("owner", True).execute().data[0]['id'] != interaction.user.id:
                await interaction.send("You cannot payout this gamble, since you didn't create it!", ephemeral=True)
                return
            await interaction.message.edit(embed=bet_message_embed, view=payoutView)

        async def buttonCallback(interaction : Interaction):
            modal = betInput(interaction.data["custom_id"], self.supabase)
            await interaction.response.send_modal(modal)

        outcome1_button.callback = buttonCallback
        outcome2_button.callback = buttonCallback
        lock_button.callback = lock_button_callback
        unlockButton.callback = unlock_button_callback
        payoutButton.callback = payoutButton_callback
        submitButton.callback = payoutView.dropdownMenu.callback



def setup(bot: commands.Bot):
    bot.add_cog(gamba(bot))
