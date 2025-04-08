import queue


class AudioQueue:
    def __init__(self):
        self.queue = queue.Queue()

    def push(self, audio_bytes):
        self.queue.put(audio_bytes)

    def pop(self):
        return self.queue.get()

    def empty(self):
        return self.queue.empty()

    def clear(self):
        while not self.queue.empty():
            self.queue.get()
