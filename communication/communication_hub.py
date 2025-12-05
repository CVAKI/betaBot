"""
Communication Hub - Central Message Routing System
"""

from .message import Message, MessageQueue
from .proximity_manager import ProximityManager
from typing import List, Optional


class CommunicationHub:
    """Central hub for all piece-to-piece communication"""

    def __init__(self):
        self.message_queue = MessageQueue()
        self.proximity_manager = ProximityManager()
        self.queen_channel = []  # Special broadcast channel
        self.king_queen_channel = []  # Private channel

    def send_message(self, sender, recipient, content: str,
                     emotion: str = 'NEUTRAL', message_type: str = 'suggestion',
                     priority: int = 2):
        """Send a message through the hub"""
        # Create message
        message = Message(sender, recipient, content, emotion,
                          message_type, priority)

        # Add to queue
        self.message_queue.add(message)

        # Deliver to recipient(s)
        if isinstance(recipient, list):
            for r in recipient:
                if hasattr(r, 'receive_message'):
                    r.receive_message(sender, content)
        else:
            if hasattr(recipient, 'receive_message'):
                recipient.receive_message(sender, content)

        return message

    def broadcast(self, sender, content: str, recipients: List = None,
                  emotion: str = 'NEUTRAL'):
        """Broadcast message to multiple recipients"""
        if recipients is None:
            # Broadcast to all
            return self.send_message(sender, 'ALL', content, emotion,
                                     'command', priority=3)

        return self.send_message(sender, recipients, content, emotion,
                                 'command', priority=3)

    def queen_broadcast(self, queen, content: str, emotion: str = 'CONFIDENT'):
        """Queen broadcasts to all pieces"""
        message = Message(queen, 'ALL', content, emotion,
                          'command', priority=4)
        self.queen_channel.append(message)
        self.message_queue.add(message)
        return message

    def king_to_queen(self, king, queen, content: str,
                      emotion: str = 'NEUTRAL', approved: bool = True):
        """King sends private message to Queen"""
        message_type = 'approval' if approved else 'denial'
        message = Message(king, queen, content, emotion,
                          message_type, priority=4)
        self.king_queen_channel.append(message)
        self.message_queue.add(message)
        return message

    def can_pieces_communicate(self, piece1, piece2, all_pieces: List) -> bool:
        """Check if two pieces can communicate"""
        return self.proximity_manager.can_communicate(piece1, piece2)

    def get_reachable_pieces(self, piece, all_pieces: List) -> List:
        """Get all pieces that can be reached from a piece"""
        return self.proximity_manager.get_nearby_pieces(piece, all_pieces)

    def get_messages_for(self, piece_id: str, unread_only: bool = False) -> List[Message]:
        """Get messages for a specific piece"""
        return self.message_queue.get_messages_for(piece_id, unread_only)

    def get_recent_messages(self, count: int = 20) -> List[Message]:
        """Get recent messages for chat display"""
        return self.message_queue.get_latest(count)

    def clear_old_messages(self, keep_count: int = 100):
        """Clear old messages to save memory"""
        if len(self.message_queue) > keep_count:
            self.message_queue.messages = self.message_queue.messages[-keep_count:]