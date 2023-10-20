from typing import Optional
import nextcord
from nextcord.interactions import Interaction
from nextcord.ui import *
from nextcord.ext import commands

class betInput(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Your Bet")
        
        self.betAmount = nextcord.ui.TextInput(
            label="Bet amount",min_length=1
        )
        
        self.add_item(self.betAmount)

        



class Gamba(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

            


    @nextcord.slash_command(name="gamba", description="Create a custom bet!")
    async def ex(self, 
                 interaction : nextcord.Interaction,
                 bettitle : str = nextcord.SlashOption(name="bet_title"),
                 outcome1 : str = nextcord.SlashOption(name="outcome_1"),
                 outcome2 : str = nextcord.SlashOption(name="outcome_2"), 
                 outcome3 : Optional[str] = nextcord.SlashOption(name="outcome_3")
                 
                 ):
        

        bet_creator = interaction.user.id
        bet_message_embed = nextcord.Embed(
            title="New Bet",
            description=f"Bet: {bettitle}",
            color=nextcord.Color.blue()
        )

        # Define the Yes and No buttons
        outcome1_button = Button(style=nextcord.ButtonStyle.success, label=outcome1, disabled=False)
        outcome2_button = Button(style=nextcord.ButtonStyle.danger, label=outcome2, disabled=False)
        outcome3_button = None
        lock_button = Button(emoji="🔐", disabled=False)
        
        
        # Create a view that contains the buttons
        view = View(timeout=120)
        view.add_item(outcome1_button)
        view.add_item(outcome2_button)
        view.add_item(lock_button)

        if outcome3 is not None:
            outcome3_button = Button(style=nextcord.ButtonStyle.blurple, label=outcome3, disabled=False)
            view.add_item(outcome3_button)

        # Send the bet message with the buttons
        await interaction.send(embed=bet_message_embed, view=view)



        
        async def yes_button_callback(interaction):
            betInputModal = betInput()
            await interaction.response.send_modal(betInputModal)                    
            
            
        async def no_button_callback(interaction):
            betInputModal = betInput()
            await interaction.response.send_modal(betInputModal)

        async def third_button_callback(interaction):
            betInputModal = betInput()
            await interaction.response.send_modal(betInputModal)


        async def lock_button_callback(interaction):
            outcome1_button.disabled = not outcome1_button.disabled
            outcome2_button.disabled = not outcome2_button.disabled
            await interaction.message.edit(embed = bet_message_embed, view=view)
            #if outcome3_button is not None:
               #outcome3_button.disabled = not outcome3_button.disabled
        

    
        outcome1_button.callback = yes_button_callback
        outcome2_button.callback = no_button_callback
        if outcome3 is not None:
            outcome3_button.callback = third_button_callback
        lock_button.callback = lock_button_callback


    



def setup(bot: commands.Bot):
    bot.add_cog(Gamba(bot))
