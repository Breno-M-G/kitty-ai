"""Session state container with persistence helpers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from litellm.types.completion import ChatCompletionMessageParam as Message

from mybot.core.history import HistoryMessage

if TYPE_CHECKING:
    from mybot.core.agent import Agent
    from mybot.core.history import HistoryStore


@dataclass
class SessionState:
    """Pure conversation state + persistence."""

    session_id: str
    agent: "Agent"
    messages: list[Message]
    history_store: "HistoryStore"

    def add_message(self, message: Message) -> None:
        """Add message to in-memory list + persist."""
        self.messages.append(message)

        history_msg = HistoryMessage.from_message(message)
        self.history_store.save_message(self.session_id, history_msg)

    def build_messages(self) -> list[Message]:
        """Build messages list with system prompt."""
        system_prompt = self.agent.agent_def.agent_md
        
        # Debug: verificar encoding do system prompt
        try:
            system_prompt.encode('utf-8')
        except UnicodeEncodeError as e:
            print(f"DEBUG system_prompt encode error: {e}")
            system_prompt = system_prompt.encode('utf-8', errors='replace').decode('utf-8')

        # Debug: verificar encoding do SOUL
        soul = getattr(self.agent.agent_def, 'soul_md', '')
        if soul:
            try:
                soul.encode('utf-8')
            except UnicodeEncodeError as e:
                print(f"DEBUG soul encode error: {e}")

        messages: list[Message] = [{"role": "system", "content": system_prompt}]
        messages.extend(self.messages)
        return messages