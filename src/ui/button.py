from typing import Callable, Awaitable

import discord
from discord.ui import Button

class TicTacToeButton(Button):
    def __init__(self, row: int, col: int, size: int, callback: Callable[[TicTacToeButton, discord.Interaction], Awaitable[None]]):
        # Calculate position number (1 to size^2)
        position = row * size + col + 1
        super().__init__(
            # label=" ",  # Empty square
            label="_",  # Empty square
            style=discord.ButtonStyle.secondary,
            row=row  # This determines which row in Discord's layout
        )

        self.row = row
        self.col = col
        self.position = position

        self.__callback = callback

    async def callback(self, interaction: discord.Interaction):
        await self.__callback(self, interaction)