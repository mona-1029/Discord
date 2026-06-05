import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.environ["DISCORD_TOKEN"]

TARGET_VC_ID = 1511816784104132873

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

pomodoro_message = None
pomodoro_task = None

work_time = 50
break_time = 10
loop_count = 3

running = False
status_text = "停止中"


def create_embed():
    embed = discord.Embed(
        title="🍅 ポモドーロタイマー",
        color=discord.Color.red()
    )

    embed.add_field(
        name="作業時間",
        value=f"{work_time}分",
        inline=True
    )

    embed.add_field(
        name="休憩時間",
        value=f"{break_time}分",
        inline=True
    )

    embed.add_field(
        name="ループ回数",
        value=f"{loop_count}回",
        inline=True
    )

    embed.add_field(
        name="状態",
        value=status_text,
        inline=False
    )

    return embed


async def update_panel():
    global pomodoro_message

    if pomodoro_message:
        try:
            await pomodoro_message.edit(
                embed=create_embed(),
                view=PomodoroView()
            )
        except:
            pass


async def run_pomodoro():
    global running
    global status_text
    global pomodoro_task

    try:
        for i in range(loop_count):

            status_text = f"作業中 ({i+1}/{loop_count})"
            await update_panel()

            await asyncio.sleep(work_time * 60)

            if not running:
                return

            if pomodoro_message:
                await pomodoro_message.channel.send(
                    f"🍅 作業終了！ {break_time}分休憩です"
                )

            status_text = f"休憩中 ({i+1}/{loop_count})"
            await update_panel()

            await asyncio.sleep(break_time * 60)

            if not running:
                return

        status_text = "完了"
        running = False

        await update_panel()

        if pomodoro_message:
            await pomodoro_message.channel.send(
                "🍅 ポモドーロ完了！お疲れさまでした"
            )

    except asyncio.CancelledError:
        pass

    finally:
        pomodoro_task = None


class PomodoroView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="作業-10", style=discord.ButtonStyle.secondary, row=0)
    async def work_minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global work_time

        if running:
            await interaction.response.defer()
            return

        work_time = max(10, work_time - 10)

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="作業+10", style=discord.ButtonStyle.secondary, row=0)
    async def work_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global work_time

        if running:
            await interaction.response.defer()
            return

        work_time += 10

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="休憩-5", style=discord.ButtonStyle.secondary, row=1)
    async def break_minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global break_time

        if running:
            await interaction.response.defer()
            return

        break_time = max(5, break_time - 5)

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="休憩+5", style=discord.ButtonStyle.secondary, row=1)
    async def break_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global break_time

        if running:
            await interaction.response.defer()
            return

        break_time += 5

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="ループ-1", style=discord.ButtonStyle.primary, row=2)
    async def loop_minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global loop_count

        if running:
            await interaction.response.defer()
            return

        loop_count = max(1, loop_count - 1)

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="ループ+1", style=discord.ButtonStyle.primary, row=2)
    async def loop_plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        global loop_count

        if running:
            await interaction.response.defer()
            return

        loop_count += 1

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="開始", style=discord.ButtonStyle.success, row=3)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global running
        global pomodoro_task
        global status_text

        if running:
            await interaction.response.defer()
            return

        running = True
        status_text = "開始準備中"

        pomodoro_task = asyncio.create_task(
            run_pomodoro()
        )

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )

    @discord.ui.button(label="停止", style=discord.ButtonStyle.danger, row=3)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global running
        global status_text
        global pomodoro_task

        running = False
        status_text = "停止中"

        if pomodoro_task:
            pomodoro_task.cancel()

        await interaction.response.edit_message(
            embed=create_embed(),
            view=PomodoroView()
        )


@bot.event
async def on_ready():
    print(f"{bot.user} でログインしました")


@bot.event
async def on_message(message):
    global pomodoro_message

    if message.author.bot:
        return

    if message.content != "ポモドーロ":
        return

    if not isinstance(message.channel, discord.abc.Messageable):
        return

    if running:
        await message.channel.send(
            "既にポモドーロが実行中です"
        )
        return

    sent = await message.channel.send(
        embed=create_embed(),
        view=PomodoroView()
    )

    pomodoro_message = sent


bot.run(TOKEN)
