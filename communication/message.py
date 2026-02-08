"""
Complete Message System Implementation
For communication/message.py
"""

from datetime import datetime
from typing import List, Union


class Message:
    """Message data structure for piece communications"""

    def __init__(self, sender: str, recipients: Union[str, List[str]],
                 content: str, emotion: str = 'NEUTRAL',
                 message_type: str = 'general', priority: int = 2):
        """
        Create a message

        Args:
            sender: ID of sending piece
            recipients: Single recipient ID or list of IDs ('ALL' for broadcast)
            content: Message content
            emotion: Sender's emotion
            message_type: Type of message (general, command, approval, denial, etc.)
            priority: Priority level (1-5, 5 highest)
        """
        self.sender = sender

        # Normalize recipients to list
        if isinstance(recipients, str):
            self.recipients = [recipients] if recipients != 'ALL' else ['ALL']
        else:
            self.recipients = recipients

        self.content = content
        self.emotion = emotion
        self.message_type = message_type
        self.priority = priority
        self.timestamp = datetime.now()
        self.read = False

    def mark_read(self):
        """Mark message as read"""
        self.read = True

    def is_broadcast(self) -> bool:
        """Check if this is a broadcast message"""
        return 'ALL' in self.recipients

    def is_for(self, piece_id: str) -> bool:
        """Check if message is for a specific piece"""
        return piece_id in self.recipients or self.is_broadcast()

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'sender': self.sender,
            'recipients': self.recipients,
            'content': self.content,
            'emotion': self.emotion,
            'message_type': self.message_type,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat(),
            'read': self.read
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message from dictionary"""
        msg = cls(
            sender=data['sender'],
            recipients=data['recipients'],
            content=data['content'],
            emotion=data.get('emotion', 'NEUTRAL'),
            message_type=data.get('message_type', 'general'),
            priority=data.get('priority', 2)
        )
        msg.timestamp = datetime.fromisoformat(data['timestamp'])
        msg.read = data.get('read', False)
        return msg

    def get_formatted_time(self) -> str:
        """Get formatted timestamp"""
        return self.timestamp.strftime("%H:%M:%S")

    def __repr__(self):
        return f"Message(from={self.sender}, to={self.recipients}, type={self.message_type})"

    def __str__(self):
        recipients_str = ', '.join(self.recipients)
        return f"[{self.get_formatted_time()}] {self.sender} → {recipients_str}: {self.content}"


class MessageQueue:
    """Queue for managing messages"""

    def __init__(self):
        self.messages: List[Message] = []

    def add(self, message: Message):
        """Add message to queue"""
        self.messages.append(message)

        # Sort by priority and timestamp
        self.messages.sort(key=lambda m: (m.priority, m.timestamp), reverse=True)

    def get_messages_for(self, piece_id: str, unread_only: bool = False) -> List[Message]:
        """Get messages for a specific piece"""
        messages = [m for m in self.messages if m.is_for(piece_id)]

        if unread_only:
            messages = [m for m in messages if not m.read]

        return messages

    def get_latest(self, count: int = 20) -> List[Message]:
        """Get latest N messages"""
        return self.messages[-count:] if len(self.messages) > count else self.messages

    def mark_read_for(self, piece_id: str):
        """Mark all messages for a piece as read"""
        for message in self.messages:
            if message.is_for(piece_id):
                message.mark_read()

    def clear_old_messages(self, keep_count: int = 100):
        """Remove old messages to save memory"""
        if len(self.messages) > keep_count:
            self.messages = self.messages[-keep_count:]

    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]