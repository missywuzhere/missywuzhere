#Melissa Genovese 4/9/2021

import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

import random
from alien_timer_functions import TimerFunctions

class AlienInvasion:
    """Overall class to manage game assests and behavior."""

    def __init__(self):
        """Initialize the game and create game resources."""
        pygame.init()
        self.settings = Settings()

        #I added the background music.
        pygame.mixer.music.load('./sounds/Wave After Wave! v0_9.mp3')
        pygame.mixer.music.play(-1)
        
        #Generate aliens at random times.
        self.timer = TimerFunctions()
        self.timer.set_next_alien_delay()
        
        #Screen settings
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption('Alien Invasion')
        
        #Create an instance to store game statistics,
        #and create a scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        #Set background color.
        self.bg_color = (230, 230, 230)

        #Make the Play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            #Watch for keyboard and mouse events.
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._create_fleet()
                self._update_bullets()
                self._update_aliens()
                
            self._update_screen()

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        #Update bullet positions.
        self.bullets.update()

        #Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()


    def _update_aliens(self):
        """update the positions of all aliens in the fleet."""
        self.aliens.update()

        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed

        #Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()


    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            #Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            #Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            #Center the ship.
            self.ship.center_ship()

            #Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.top >= screen_rect.bottom:

                #Get rid of aliens that have disappeared.
                for alien in self.aliens.sprites():
                    self.aliens.remove(alien)
                    break

       #print(len(self.aliens)) 


    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
            """Start a new game when the player clicks Play."""
            button_clicked = self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.stats.game_active:
                #Reset the game settings.
                self.settings.initialize_dynamic_settings()
                
                #Reset the game statistics.
                self.stats.reset_stats()
                self.stats.game_active = True
                self.sb.prep_score()
                self.sb.prep_level()
                self.sb.prep_ships()

                #Get rid of any remaining aliens and bullets.
                self.aliens.empty()
                self.bullets.empty()

                #Create a new fleet and center the ship.
                self._create_fleet()
                self.ship.center_ship()

                #Hide the mouse cursor.
                pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _create_fleet(self):
        """Create the fleet of aliens."""
        #Create an alien and have them appear randomly.
        #Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien_width = alien.rect.width
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        #Create aliens randomly.
        alien_number = random.randint(0, number_aliens_x)
        
        if self.timer.time_to_create_another_alien():
            self._create_alien(alien_number, 0)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the game."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)


    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        #Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
               self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

            if not self.aliens:
                #Destroy existing bullets and create new fleet.
                self.bullets.empty()
                self._create_fleet()
                self.settings.increase_speed()

                #Increase level.
                self.stats.level += 1
                self.sb.prep_level()


    def _update_screen(self):
        """Update images on screen, and flip to the new screen"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        #Draw the score information.
        self.sb.show_score()

        #Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

if __name__ == '__main__':
    #Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()