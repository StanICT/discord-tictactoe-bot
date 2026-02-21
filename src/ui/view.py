from typing import Callable, Awaitable

import discord
from discord.ui import View

from ui.button import TicTacToeButton

class TicTacToeView(View):
    def __init__(self, size: int, callback: Callable[[TicTacToeButton, discord.Interaction], Awaitable[None]]):
        super().__init__(timeout=300)  # 5 minute timeout
        # self.size = size

        # Create the grid of buttons
        for row in range(size):
            for col in range(size):
                self.add_item(TicTacToeButton(row, col, size, callback))
