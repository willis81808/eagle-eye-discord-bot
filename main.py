import os
import discord
from discord import (
    TextChannel,
    DMChannel,
    GroupChannel,
    PartialMessageable,
)
from discord.message import Message
from discord.ext import commands
from typing import List, cast
from dotenv import load_dotenv
from openai import OpenAI
from openai.types import (
    ModerationMultiModalInputParam,
    ModerationTextInputParam,
    ModerationImageURLInputParam,
)

from src.models import Config, ModerationResult, ViolationField
from src.utils import sum_dicts

load_dotenv()


DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if DISCORD_BOT_TOKEN == "":
    print("Missing environment variable DISCORD_BOT_TOKEN")
    exit(1)

if OPENAI_API_KEY == "":
    print("Missing environment variable OPENAI_API_KEY")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)
moderator = OpenAI(api_key=OPENAI_API_KEY)


config = Config.load()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: Message):
    if message.author.bot or message.author == bot.user:
        return
    if not message.guild or not message.channel:
        return
    await analyze_message(message)


@bot.command(name="set-reports-channel")
async def set_reports_channel(
    ctx: commands.Context,
    channel_id: int,
):
    if not ctx.guild:
        await ctx.reply("This command must be used in a server")
        return
    channel = ctx.guild.get_channel(channel_id)
    if channel and isinstance(channel, TextChannel):
        global config
        config.set_report_channel(guild_id=ctx.guild.id, channel_id=channel.id)
        await ctx.reply(f"I will now send reports to: {channel.mention}")
    else:
        await ctx.reply("Invalid channel ID or channel type")


async def analyze_message(message: Message):
    results: List[ModerationResult] = list()
    for part in msg_to_moderation_input(message=message):
        result = moderator.moderations.create(
            model="omni-moderation-latest",
            input=[part],
        ).results[0]
        results.append(ModerationResult(result, part))

    if any([result.flagged for result in results]):
        await flag_message(message, results)


async def flag_message(message: Message, results: List[ModerationResult]):
    assert message.channel
    assert message.guild

    global config
    channel_id = config.report_channels.get(message.guild.id) or message.channel.id
    channel = message.guild.get_channel(channel_id)

    assert isinstance(channel, TextChannel)

    # construct embed
    moderation_results_embed = discord.Embed(
        title="Message Flagged!",
        description=(f"[Jump To Message]({message.jump_url})"),
        color=discord.Color.red(),
    )
    moderation_results_embed.set_author(
        name=f"{message.author.display_name} {message.author.mention}",
        icon_url=message.author.display_avatar,
    )

    # add user info
    moderation_results_embed.add_field(
        name="User",
        value=message.author.mention,
        inline=False,
    )

    # include link to channel message was sent in
    if (
        not isinstance(message.channel, DMChannel)
        and not isinstance(message.channel, PartialMessageable)
        and not isinstance(message.channel, GroupChannel)
    ):
        moderation_results_embed.add_field(
            name="Channel",
            value=message.channel.mention,
            inline=False,
        )

    # include suspect message
    text_results = [result for result in results if result.type == "text"]
    if text_results:
        result = text_results[0]
        moderation_results_embed.add_field(
            name="Message" + (" (flagged)" if result.flagged else ""),
            value=f"\n{message.content}\n",
            inline=False,
        )
    images = [
        result.content + (" (flagged)" if result.flagged else "")
        for result in results
        if result.type == "image_url"
    ]
    if images:
        moderation_results_embed.add_field(
            name="Images",
            value="\n".join(images),
            inline=False,
        )

    # add violation fields
    fields: List[ViolationField] = list()
    flagged_results = sum_dicts([result.category_scores for result in results])
    for k, v in flagged_results.items():
        percentage = round(cast(float, v) * 100)
        if percentage >= 10:
            fields.append(ViolationField(name=k, value=percentage))
    for field in sorted(fields, key=lambda x: x.value, reverse=True):
        field.add_field(embed=moderation_results_embed)

    # reply with moderation summary
    await channel.send(embed=moderation_results_embed, silent=True)


def msg_to_moderation_input(message: Message) -> List[ModerationMultiModalInputParam]:
    result: List[ModerationMultiModalInputParam] = list()

    text: ModerationTextInputParam = {"type": "text", "text": message.content}
    result.append(text)

    for attachment in message.attachments:
        if not attachment.content_type:
            continue
        if not attachment.content_type.startswith("image/"):
            continue
        print(attachment.url)
        image: ModerationImageURLInputParam = {
            "type": "image_url",
            "image_url": {"url": attachment.url},
        }
        result.append(image)

    return result


bot.run(DISCORD_BOT_TOKEN)
