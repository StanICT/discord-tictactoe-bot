import asyncio

import discord
from discord import app_commands
from client import client

tree = app_commands.CommandTree(client)

class TicTacToe(app_commands.Group):
    def __init__(self):
        super().__init__(name="tictactoe", description="TicTacToe")

    @app_commands.command(name="help", description="Forfeits from the game")
    async def help(self, interaction):
        await interaction.response.send_message("```Commands for playing TicTacToe Bot: 😉" \
        "\n❌ /tictactoe start - Start a game of TicTacToe with an online opponent."
        "\n⭕ /tictactoe cell - Place your specified mark from 1 - 9 on the provided cell." \
        "\n😶‍🌫️ /tictactoe surrender - Forfeits from the game.```")

    @app_commands.command(name="start", description="Starts a game of TicTacToe")
    @app_commands.describe(opponent="The opposing player to play against with", grid_size="The size of one side of the NxN grid")
    async def start(self, interaction: discord.Interaction, opponent: discord.Member, grid_size: int = 3):
        if client.started:
            await interaction.response.send_message("A game of TicTacToe is already on session",ephemeral=True)
            return
        
        if interaction.user.id == opponent.id:
            await interaction.response.send_message("You cannot play against yourself",ephemeral=True)
            return
        
        if opponent.bot:
            await interaction.response.send_message("You cannot play against a bot",ephemeral=True)
            return
        
        opponent = await interaction.guild.fetch_member(opponent.id)
        await asyncio.sleep(1)
        opponent = interaction.guild.get_member(opponent.id)

        if opponent.status != discord.Status.online and opponent.status != discord.Status.idle:
            await interaction.response.send_message(f"User {opponent.display_name} does not seem to be active at the moment",ephemeral=True)
            return
        
        await client.start_game(grid_size, (interaction.user, opponent))
        await interaction.response.send_message(f"Started a game of TicTacToe with <@{opponent.id}>\n{client.turn_display(client.turn)}'s Turn", view=client.view)

        return
    
    @app_commands.command(name="surrender", description="Forfeits from the game")
    async def surrender(self, interaction: discord.Interaction):
        global WINNER

        if not client.started:
            await interaction.response.send_message("There currently is no game of TicTacToe in session", ephemeral=True)
            return

        # Check if the user of the interaction is a player
        p_idx = -1
        for i, (player, _) in enumerate(client.players):
            if interaction.user.id == player.id:
                p_idx = i

        if p_idx == -1:
            await interaction.response.send_message("You are not a player in the currently on-going game of TicTacToe", ephemeral=True)
            return

        await interaction.response.send_message(f"<@{interaction.user.id}> has surrendered")

        WINNER = (p_idx + 1) % len(client.players)

        client.started = False
        await client.display_winner(interaction.channel)
        client.reset()

    # @app_commands.command(name="cell", description="Places your specified mark on the provided cell")
    # @app_commands.describe(cell="The cell number to place the mark")
    # async def cell(self, interaction: discord.Interaction, cell: int):
    #     channel = interaction.channel

    #     if not client.started:
    #         await interaction.response.send_message(f"You are currently not part of a game of TicTacToe.",ephemeral=True)
    #         return

    #     member, _ = client.players[client.turn]
    #     if interaction.user.id != member.id:
    #         await interaction.response.send_message(f"Player {member.display_name}'s turn",ephemeral=True)
    #         return

    #     try:
    #         # Range checker to avoid invalid cell numbers
    #         if cell < 1 or cell > (self.size ** 2):
    #             await interaction.response.send_message(f"Invalid cell number: {cell}",ephemeral=True)
    #             return

    #         # Check if the cell already has a mark
    #         if (client.has_mark(cell)):
    #             await interaction.response.send_message(f"Cell number {cell} already has a mark!",ephemeral=True)
    #             return

    #         await interaction.response.send_message(f"Mark {client.turn_mark(client.turn)} has been placed on cell {cell}")

    #         client.set_cell(cell, client.turn)
    #         client.check_winner(client.turn) # Check winner immediately

    #         await client.print_board(channel)

    #         if not client.has_empty_cells() or WINNER != -1:
    #             await client.display_winner(channel)
    #             client.reset()
    #             return
            
    #         await client.update_turn(channel)

    #     except Exception as exc:
    #         await interaction.response.send_message(channel, f"Invalid cell number!\n{exc}",ephemeral=True)
    #         return
        
            
for guild_id in client.guild_ids:
    tree.add_command(TicTacToe(), guild=discord.Object(id=guild_id))

