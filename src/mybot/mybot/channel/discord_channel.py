"""Discord channel implementation."""

import asyncio
from dataclasses import dataclass
import logging
from typing import Callable, Awaitable

import discord

from mybot.core.events import EventSource
from mybot.channel.base import Channel
from mybot.utils.config import DiscordConfig

logger = logging.getLogger(__name__)


@dataclass
class DiscordEventSource(EventSource):
    """Source for Discord-originated events."""

    _namespace = "platform-discord"
    user_id: str
    channel_id: str

    def __str__(self) -> str:
        return f"platform-discord:{self.user_id}:{self.channel_id}"

    @classmethod
    def from_string(cls, s: str) -> "DiscordEventSource":
        _, user_id, channel_id = s.split(":")
        return cls(user_id=user_id, channel_id=channel_id)

    @property
    def platform_name(self) -> str:
        return "discord"


class DiscordChannel(Channel[DiscordEventSource]):
    """Discord platform implementation using discord.py."""

    platform_name = "discord"

    def __init__(self, config: DiscordConfig):
        """Initialize DiscordChannel."""
        self.config = config
        self.client: discord.Client | None = None
        self._running_task: asyncio.Task | None = None

    async def run(
        self, on_message_callback: Callable[[str, DiscordEventSource], Awaitable[None]]
    ) -> None:
        """Run the Discord channel. Blocks until stop() is called."""
        if self._running_task is not None:
            raise RuntimeError("DiscordChannel already running")

        logger.info(f"Channel enabled with platform: {self.platform_name}")

        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        self.client = discord.Client(intents=intents)

        @self.client.event
        async def on_ready() -> None:
            logger.info(f"Discord gateway connected as {self.client.user}")

        @self.client.event
        async def on_message(message: discord.Message) -> None:
            """Handle incoming Discord message."""
            if self.client and message.author == self.client.user:
                return

            if (
                self.config.channel_ids
                and str(message.channel.id) not in self.config.channel_ids
            ):
                return

            if not message.content:
                return

            if self.client and self.client.user not in message.mentions:
                return

            user_id = str(message.author.id)
            channel_id = str(message.channel.id)
            content = message.content

            logger.info(
                f"Received Discord message from user {user_id} in channel {channel_id}"
            )

            source = DiscordEventSource(user_id=user_id, channel_id=channel_id)

            try:
                await on_message_callback(content, source)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")

        self._running_task = asyncio.create_task(
            self.client.start(self.config.bot_token)
        )

        logger.info("DiscordChannel started")
        await self._running_task

    def is_allowed(self, source: DiscordEventSource) -> bool:
        """Check if sender is whitelisted."""
        if not self.config.allowed_user_ids:
            return True
        return source.user_id in self.config.allowed_user_ids

    async def reply(self, content: str, source: DiscordEventSource) -> None:
        """Reply to incoming message in the same channel."""
        if not self.client:
            raise RuntimeError("DiscordChannel not started")

        try:
            channel = self.client.get_channel(int(source.channel_id))
            if not channel:
                raise ValueError(f"Channel {source.channel_id} not found")

            await channel.send(content)  # type: ignore[union-attr]
            logger.debug(f"Sent Discord reply to {source.channel_id}")
        except Exception as e:
            logger.error(f"Failed to send Discord reply: {e}")
            raise

    async def stop(self) -> None:
        """Stop Discord bot and cleanup."""
        if self.client is None:
            logger.debug("DiscordChannel not running, skipping stop")
            return

        await self.client.close()

        if self._running_task and not self._running_task.done():
            try:
                await asyncio.wait_for(self._running_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Running task did not complete in time")
            except Exception:
                pass

        self.client = None
        self._running_task = None
        logger.info("DiscordChannel stopped")
