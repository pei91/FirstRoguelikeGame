import tcod as libtcod

import textwrap

class Message:
    def __init__(self, text, color=libtcod.white):
        self.text =text
        self.color = color

class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message):
        # Split the message if necessary, among multiple lines
        new_msh_lines = textwrap.wrap(message.text, self.width)

        for line in new_msh_lines:
            # If the buffer is full, remove the first line to make room tor the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(Message(line, message.color))
