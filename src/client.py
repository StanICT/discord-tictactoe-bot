from dotenv import load_dotenv
import os
import re

import discord

from ui.view import TicTacToeView
from ui.button import TicTacToeButton

load_dotenv()


class Client(discord.Client):
    started: bool = False

    size: int = 3
    board: list[list[str]]

    winner: int = -1
    turn: int = 0

    guild_ids: list[int] = list(map(lambda x: int(x), re.split(",\\s*",os.getenv("GUILDS"))))

    players: tuple[tuple[discord.User, str], tuple[discord.User, str]]

    # UI
    view: TicTacToeView

    def create_board(self) -> list[list[str]]:
        # Create user interface view
        self.view = TicTacToeView(self.size, self.create_btn_callback())

        return [[" " for _ in range(self.size)] for _ in range(self.size)]
    
    
    def board_to_str(self) -> str:
        return f"```{"\n".join([f"| {" | ".join(row)} |" for row in self.board])}```"
    
    def set_cell(self, cell_no: int, turn: int) -> None:
        # row = (cell_no - 1) // self.size (len(board))
        # col = (cell_no - 1) % self.size (len(board))
        size = len(self.board)
        row, col = (cell_no - 1) // size, (cell_no - 1) % size

        self.board[row][col] = self.turn_mark(turn)

    def has_mark(self, cell_no: int) -> bool:
        # row = (cell_no - 1) // self.size (len(board))
        # col = (cell_no - 1) % self.size (len(board))
        size = len(self.board)
        row, col = (cell_no - 1) // size, (cell_no - 1) % size

        return self.board[row][col] != " " # Space states that the cell is empty

    def update_turn(self):
        # n = len(self.players) = 2
        # self.turn = 0 = (0 + 1) % n = 1 % n = 1
        # self.turn = 1 = (1 + 1) % n = 2 % n = 0
        self.turn = (self.turn + 1) % len(self.players)

    def turn_display(self, turn: int) -> str:
        user, mark = self.players[turn]
        return f"[{mark}] <@{user.id}>"

    def turn_mark(self, turn: int) -> str:
        return f"{self.players[turn][1]}"


    def reset(self):
        self.started = False

        self.winner = -1 # Reset the winner back to -1 (Draw)
        self.turn = 0 # Reset turn to whatever turn you want
        self.board = self.create_board() # Re-create the board


    async def send_message(self, channel: discord.channel.TextChannel, message: str) -> discord.Message:
        return await channel.send(message)

    async def print_board(self, channel: discord.channel.TextChannel):
        await self.send_message(channel, self.board_to_str())


    async def display_board(self):
        pass

        
    def horizontal_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        player_mark = self.turn_mark(turn)

        for row in self.board:
            matched = 0

            for cell in row:
                # If the cell is not the specified player's mark, break out of the loop
                if cell != player_mark:
                    break

                matched += 1

            if matched == len(row):
                self.winner = turn

                # for i in range(self.size):
                #     row[i] = f"{GREEN_FG}{mark}{RESET}"

                return

    def vertical_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        player_mark = self.turn_mark(turn)

        # [" ", " ", " "]
        # [" ", " ", " "]
        # [" ", " ", " "]

        for i in range(self.size):
            matched = 0

            for j in range(self.size):
                cell = self.board[j][i]
                if cell != player_mark:
                    break

                matched += 1

            if matched == self.size:
                self.winner = turn

                # for j in range(self.size):
                #     self.board[j][i] = f"{GREEN_FG}{mark}{RESET}"

                return

    def diagonal_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        player_mark = self.turn_mark(turn)

        # [" ", " ", " "]
        # [" ", " ", " "]
        # [" ", " ", " "]

        # Diagonal [i][i]
        matched = 0
        for i in range(self.size):
            cell = self.board[i][i]
            if cell != player_mark:
                break

            matched += 1        

        if matched == self.size:
            self.winner = turn

            # for i in range(self.size):
            #     board[i][i] = f"{GREEN_FG}{mark}{RESET}"

            return

        # Anti-Diagonal [i][self.size - (i + 1)]
        matched = 0
        for i in range(self.size):
            cell = self.board[i][self.size - (i + 1)]
            if cell != player_mark:
                break

            matched += 1

        if matched == self.size:
            self.winner = turn

            # for i in range(self.size):
            #     board[i][self.size - (i + 1)] = f"{GREEN_FG}{mark}{RESET}"

            return

    def check_winner(self, turn: int):
        # Horizontal Check
        self.horizontal_check(turn)
        if self.winner != -1:
            return

        # Vertical Check
        self.vertical_check(turn)
        if self.winner != -1:
            return

        # Diagonal Check
        self.diagonal_check(turn)
        if self.winner != -1:
            return

    def has_empty_cells(self) -> bool:
        for row in self.board:
            for cell in row:
                if cell == " ":
                    return True

        return False


    async def display_winner(self, channel: discord.channel.TextChannel):
        if self.winner == -1:
            await self.send_message(channel, f"**DRAW**")
        else:
            await self.send_message(channel, f"**Winner: <@{self.players[self.winner][0].id}> [{self.turn_mark(self.winner)}]**")
        
    async def start_game(self, channel: discord.channel.TextChannel, grid_size: int, players: tuple[discord.User, discord.User]):
        self.started = True
        self.size = grid_size
        self.board = self.create_board()

        self.players = [(players[0], "X"), (players[1], "O")]

        
    def create_btn_callback(self):
        async def __btn_callback__(button: TicTacToeButton, interaction: discord.Interaction):
                row, col = button.row, button.col

                member, _ = self.players[self.turn]
                if interaction.user.id != member.id:
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send(f"Player {member.display_name}'s turn",ephemeral=True)
                    return
                
                await interaction.response.defer()
                
                button.disabled = True
                button.label = client.turn_mark(self.turn)

                client.set_cell(row * client.size + (col + 1), client.turn)
                client.check_winner(client.turn) # Check winner immediately

                client.update_turn()
                await interaction.edit_original_response(content=f"{client.turn_display(client.turn)}'s Turn", view=client.view)

                if not client.has_empty_cells() or client.winner != -1:
                    await client.display_winner(interaction.channel)
                    client.reset()

                    # Disable all buttons
                    for btn in client.view.children:
                        btn.disabled = True # Assuming that all children are buttons

                    return

        return __btn_callback__ 


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True


client = Client(intents = intents)
