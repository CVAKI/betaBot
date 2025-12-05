"""
Chat Logger
Logs all communications for display and analysis
"""

import json
import os
from datetime import datetime
from typing import List, Optional
import config


class ChatLogger:
    """Logs and manages chat message history"""

    def __init__(self, game_id: Optional[str] = None):
        """
        Initialize chat logger

        Args:
            game_id: Unique identifier for this game session
        """
        self.game_id = game_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.messages = []
        self.log_file = os.path.join(
            config.CHAT_LOGS_DIR,
            f"chat_{self.game_id}.txt"
        )

        # Ensure directory exists
        os.makedirs(config.CHAT_LOGS_DIR, exist_ok=True)

        # Initialize log file
        self._write_header()

    def _write_header(self):
        """Write log file header"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"β-bot Chess AI - Chat Log\n")
            f.write(f"Game ID: {self.game_id}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

    def log_message(self, message):
        """
        Log a message

        Args:
            message: Message object to log
        """
        self.messages.append(message)

        # Write to file
        formatted = self._format_message_for_file(message)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(formatted + "\n")

    def _format_message_for_file(self, message) -> str:
        """Format message for file logging"""
        timestamp = message.timestamp.strftime("%H:%M:%S")
        emoji = self._get_emoji(message.emotion)

        sender = message.sender
        recipients = ", ".join(message.recipients)

        formatted = f"[{timestamp}] {sender} → {recipients}\n"
        formatted += f"  {emoji} {message.content}\n"
        formatted += f"  (Type: {message.message_type}, Priority: {message.priority})\n"

        return formatted

    def _get_emoji(self, emotion: str) -> str:
        """Convert emotion to emoji"""
        emoji_map = {
            'HAPPY': '😊',
            'SAD': '😢',
            'SCARED': '😰',
            'CONFIDENT': '😤',
            'ANGRY': '😠',
            'NEUTRAL': '😐',
            'ANXIOUS': '😟',
            'PROUD': '😎',
            'RESIGNED': '😔'
        }
        return emoji_map.get(emotion, '😐')

    def get_chat_history(self, count: Optional[int] = None) -> List:
        """
        Get chat history

        Args:
            count: Number of recent messages (None for all)

        Returns:
            List of messages
        """
        if count is None:
            return self.messages[:]
        return self.messages[-count:]

    def get_messages_by_sender(self, sender_id: str) -> List:
        """Get all messages from a specific sender"""
        return [m for m in self.messages if m.sender == sender_id]

    def get_messages_by_recipient(self, recipient_id: str) -> List:
        """Get all messages to a specific recipient"""
        return [m for m in self.messages if recipient_id in m.recipients]

    def get_messages_by_type(self, message_type: str) -> List:
        """Get all messages of a specific type"""
        return [m for m in self.messages if m.message_type == message_type]

    def get_messages_in_timerange(self, start_time: datetime,
                                  end_time: datetime) -> List:
        """Get messages within a time range"""
        return [m for m in self.messages
                if start_time <= m.timestamp <= end_time]

    def filter_by_emotion(self, emotion: str) -> List:
        """Get messages with specific emotion"""
        return [m for m in self.messages if m.emotion == emotion]

    def search_content(self, query: str) -> List:
        """Search messages by content"""
        query_lower = query.lower()
        return [m for m in self.messages
                if query_lower in m.content.lower()]

    def get_conversation(self, piece1_id: str, piece2_id: str) -> List:
        """Get conversation between two pieces"""
        return [m for m in self.messages
                if (m.sender == piece1_id and piece2_id in m.recipients) or
                (m.sender == piece2_id and piece1_id in m.recipients)]

    def get_statistics(self) -> dict:
        """Get chat statistics"""
        if not self.messages:
            return {}

        stats = {
            'total_messages': len(self.messages),
            'start_time': self.messages[0].timestamp,
            'end_time': self.messages[-1].timestamp,
            'duration': (self.messages[-1].timestamp -
                         self.messages[0].timestamp).total_seconds(),
            'messages_by_sender': {},
            'messages_by_type': {},
            'messages_by_emotion': {}
        }

        # Count by sender
        for msg in self.messages:
            stats['messages_by_sender'][msg.sender] = \
                stats['messages_by_sender'].get(msg.sender, 0) + 1
            stats['messages_by_type'][msg.message_type] = \
                stats['messages_by_type'].get(msg.message_type, 0) + 1
            stats['messages_by_emotion'][msg.emotion] = \
                stats['messages_by_emotion'].get(msg.emotion, 0) + 1

        return stats

    def export_to_json(self, filename: Optional[str] = None):
        """Export chat history to JSON"""
        if filename is None:
            filename = os.path.join(
                config.CHAT_LOGS_DIR,
                f"chat_{self.game_id}.json"
            )

        data = {
            'game_id': self.game_id,
            'message_count': len(self.messages),
            'messages': [m.to_dict() for m in self.messages]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_summary(self) -> str:
        """Generate a text summary of the chat"""
        stats = self.get_statistics()

        if not stats:
            return "No messages logged"

        summary = f"Chat Summary for Game {self.game_id}\n"
        summary += "=" * 60 + "\n\n"
        summary += f"Total Messages: {stats['total_messages']}\n"
        summary += f"Duration: {stats['duration']:.1f} seconds\n\n"

        summary += "Messages by Sender:\n"
        for sender, count in sorted(stats['messages_by_sender'].items(),
                                    key=lambda x: x[1], reverse=True):
            summary += f"  {sender}: {count}\n"

        summary += "\nMessages by Emotion:\n"
        for emotion, count in sorted(stats['messages_by_emotion'].items(),
                                     key=lambda x: x[1], reverse=True):
            emoji = self._get_emoji(emotion)
            summary += f"  {emoji} {emotion}: {count}\n"

        return summary

    def clear(self):
        """Clear all messages (keeps log file)"""
        self.messages.clear()

    def __len__(self):
        return len(self.messages)

    def __repr__(self):
        return f"ChatLogger(game_id={self.game_id}, messages={len(self.messages)})"