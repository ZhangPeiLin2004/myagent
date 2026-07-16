


# msg_bus

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
from backend.common.constants import MsgType

@dataclass
class AgentMessage:
    sender_id: str
    receiver_id: str
    task_id: str
    msg_type: MsgType
    content: Dict[str, Any]
    timestamp: str

class MessageBus:
    def __init__(self):
        self.agent_mailbox: Dict[str, List[AgentMessage]] = {}

    def register_agent(self, agent_id: str):
        if agent_id not in self.agent_mailbox:
            self.agent_mailbox[agent_id] = []

    def send(self, msg: AgentMessage):
        self.register_agent(msg.receiver_id)
        self.agent_mailbox[msg.receiver_id].append(msg)

    def receive(self, agent_id: str) -> Optional[AgentMessage]:
        box = self.agent_mailbox.get(agent_id, [])
        if not box:
            return None
        return box.pop(0)

    def to_dict(self, msg: AgentMessage) -> Dict[str, Any]:
        return asdict(msg)

