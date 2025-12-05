class CommunicationHub:
    def __init__(self):
        self.message_queue = []

    def send_message(self, from_piece, to_piece, content):
        message = {
            'from': from_piece.id,
            'to': to_piece.id,
            'content': content,
            'emotion': from_piece.get_emotion(),
            'timestamp': time.time()
        }
        self.message_queue.append(message)
        to_piece.receive_message(from_piece, content)