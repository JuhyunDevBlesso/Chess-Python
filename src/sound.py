import pygame
import os

class Sound:
    def __init__(self, base_path, file_path):
        self.path = os.path.join(base_path, file_path)
        self.sound = pygame.mixer.Sound(self.path)

    def play(self):
        pygame.mixer.Sound.play(self.sound)
