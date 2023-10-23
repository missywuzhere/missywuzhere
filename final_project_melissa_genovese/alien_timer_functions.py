import pygame
from random import randint

class TimerFunctions():

    def __init__(self):
        """Initialize timer functions"""
        self.alien_delay = 0
        self.last_alien_created_time = 0

    def set_next_alien_delay(self):
        """Set the delay time to a random int between 0.5 - 2 seconds"""
        self.alien_delay = randint(500, 2000)

    def time_to_create_another_alien(self):
        """Returns True if it's time to create an alien"""
        now = pygame.time.get_ticks()
        
        if now - self.last_alien_created_time >= self.alien_delay:
            self.last_alien_created_time = now
            self.set_next_alien_delay()
            return True
        else:
            return False