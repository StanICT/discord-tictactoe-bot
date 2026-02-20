from dotenv import load_dotenv
import os
import re
import traceback

import discord
from discord import app_commands

load_dotenv()

SIZE: int = 3
TURN: int = 0

WINNER: int = -1

GUILDS: list[int] = list(map(lambda x: int(x), re.split(",\\s*",os.getenv("GUILDS"))))

class Client(discord.Client):
    started: bool = False
    board: list[list[str]]

    players: tuple[tuple[discord.User, str], tuple[discord.User, str]]

    def create_board(self, size: int) -> list[list[str]]:
        return [[" " for _ in range(size)] for _ in range(size)]
    
    def board_to_str(self) -> str:
        return f"```{"\n".join([f"| {" | ".join(row)} |" for row in self.board])}```"
    
    def set_cell(self, cell_no: int, turn: int) -> None:
        # row = (cell_no - 1) // SIZE (len(board))
        # col = (cell_no - 1) % SIZE (len(board))
        size = len(self.board)
        row, col = (cell_no - 1) // size, (cell_no - 1) % size

        self.board[row][col] = self.turn_mark(turn)

    def has_mark(self, cell_no: int) -> bool:
        # row = (cell_no - 1) // SIZE (len(board))
        # col = (cell_no - 1) % SIZE (len(board))
        size = len(self.board)
        row, col = (cell_no - 1) // size, (cell_no - 1) % size

        return self.board[row][col] != " " # Space states that the cell is empty

    async def update_turn(self, channel: discord.channel.TextChannel | None = None):
        # n = len(self.players) = 2
        # TURN = 0 = (0 + 1) % n = 1 % n = 1
        # TURN = 1 = (1 + 1) % n = 2 % n = 0
        global TURN
        TURN = (TURN + 1) % len(self.players)

        if channel is not None:
            await self.send_message(channel, f"{self.turn_display(TURN)}'s Turn")

    def turn_display(self, turn: int) -> str:
        user, mark = self.players[turn]
        return f"[{mark}] <@{user.id}>"

    def turn_mark(self, turn: int) -> str:
        return f"{self.players[turn][0]}"


    def reset(self):
        global WINNER, BOARD, TURN

        WINNER = -1 # Reset the winner back to -1 (Draw)
        TURN = 0 # Reset turn to whatever turn you want
        BOARD = self.create_board(SIZE) # Re-create the board


    async def send_message(self, channel: discord.channel.TextChannel, message: str) -> discord.Message:
        return await channel.send(message)

    async def print_board(self, channel: discord.channel.TextChannel):
        await self.send_message(channel, self.board_to_str())

        
    def horizontal_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        global WINNER

        player_mark = self.turn_mark(turn)

        for row in self.board:
            matched = 0

            for cell in row:
                # If the cell is not the specified player's mark, break out of the loop
                if cell != player_mark:
                    break

                matched += 1

            if matched == len(row):
                WINNER = turn

                # for i in range(SIZE):
                #     row[i] = f"{GREEN_FG}{mark}{RESET}"

                return

    def vertical_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        global WINNER

        player_mark = self.turn_mark(turn)

        # [" ", " ", " "]
        # [" ", " ", " "]
        # [" ", " ", " "]

        for i in range(SIZE):
            matched = 0

            for j in range(SIZE):
                cell = self.board[j][i]
                if cell != player_mark:
                    break

                matched += 1

            if matched == SIZE:
                WINNER = turn

                # for j in range(SIZE):
                #     self.board[j][i] = f"{GREEN_FG}{mark}{RESET}"

                return

    def diagonal_check(self, turn: int):
        assert(turn >= 0 or turn < len(self.players)) # Turn is dependent on the number of self.players

        global WINNER

        player_mark = self.turn_mark(turn)

        # [" ", " ", " "]
        # [" ", " ", " "]
        # [" ", " ", " "]

        # Diagonal [i][i]
        matched = 0
        for i in range(SIZE):
            cell = self.board[i][i]
            if cell != player_mark:
                break

            matched += 1        

        if matched == SIZE:
            WINNER = turn

            # for i in range(SIZE):
            #     board[i][i] = f"{GREEN_FG}{mark}{RESET}"

            return

        # Anti-Diagonal [i][SIZE - (i + 1)]
        matched = 0
        for i in range(SIZE):
            cell = self.board[i][SIZE - (i + 1)]
            if cell != player_mark:
                break

            matched += 1

        if matched == SIZE:
            WINNER = turn

            # for i in range(SIZE):
            #     board[i][SIZE - (i + 1)] = f"{GREEN_FG}{mark}{RESET}"

            return

    def check_winner(self, turn: int):
        # Horizontal Check
        self.horizontal_check(turn)
        if WINNER != -1:
            return

        # Vertical Check
        self.vertical_check(turn)
        if WINNER != -1:
            return

        # Diagonal Check
        self.diagonal_check(turn)
        if WINNER != -1:
            return

    def has_empty_cells(self) -> bool:
        for row in self.board:
            for cell in row:
                if cell == " ":
                    return True

        return False


    async def display_winner(self, channel: discord.channel.TextChannel):
        await self.send_message(channel, f"**Winner: {self.turn_mark(WINNER)}**")
        
    async def start_game(self, channel: discord.channel.TextChannel, players: tuple[discord.User, discord.User]):
        global TURN, SIZE

        self.started = True
        self.board = self.create_board(SIZE)

        self.players = [(players[0], "X"), (players[1], "O")]

        await self.print_board(channel)
        await self.send_message(channel, f"{client.turn_display(TURN)}'s Turn")


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True


client = Client(intents = intents)
tree = app_commands.CommandTree(client)

class TicTacToe(app_commands.Group):
    def __init__(self):
        super().__init__(name="tictactoe", description="TicTacToe")

    @app_commands.command(name="start", description="Starts a game of TicTacToe")
    @app_commands.describe(opponent="The opposing player to play against with")
    async def start(self, interaction: discord.Interaction, opponent: discord.Member):
        if client.started:
            await interaction.response.send_message("A game of TicTacToe is already on session")
            return
        
        if opponent.status != discord.Status.online and opponent.status != discord.Status.idle:
            await interaction.response.send_message(f"User {opponent.display_name} does not seem to be active at the moment")
            return
        
        await interaction.response.send_message("Started a game of TicTacToe")
        await client.start_game(interaction.channel, interaction.user, opponent)

        return 

    @app_commands.command(name="cell", description="Places your specified mark on the provided cell")
    @app_commands.describe(cell="The cell number to place the mark")
    async def cell(self, interaction: discord.Interaction, cell: int):
        channel = interaction.channel

        if not client.started:
            await interaction.response.send_message(f"You are currently not part of a game of TicTacToe.")
            return

        try:
            # Range checker to avoid invalid cell numbers
            if cell < 1 or cell > (SIZE ** 2):
                await interaction.response.send_message(f"Invalid cell number: {cell}")
                return

            # Check if the cell already has a mark
            if (client.has_mark(cell)):
                await interaction.response.send_message(f"Cell number {cell} already has a mark!")
                return

            await interaction.response.send_message(f"Mark {client.turn_mark(TURN)} has been placed on cell {cell}")

            client.set_cell(cell, TURN)
            client.check_winner(TURN) # Check winner immediately

            await client.print_board(channel)

            if not client.has_empty_cells() or WINNER != -1:
                client.started = False
                await client.display_winner(channel)
                return
            
            await client.update_turn(channel)

        except Exception as exc:
            await client.send_message(channel, f"Invalid cell number!\n{exc}")
            traceback.print_exc()
            return
            
for guild_id in GUILDS:
    tree.add_command(TicTacToe(), guild=discord.Object(id=guild_id))


@client.event
async def on_ready():
    for guild_id in GUILDS:
        await tree.sync(guild=discord.Object(id=guild_id))

    print(f"Logged on as {client.user}!")

client.run(os.getenv("DISCORD_BOT_TOKEN"))

