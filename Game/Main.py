import pygame
import Utility.Constants as Constants
from SceneManager import SceneManager, HubScene
from DatingSim import isaacDatingSim
from RussianRoullette.exsplodeAllOverIsaac import RussianRouletteScene
from blackjack.blackjack_game import BlackjackScene
from Slots.Slots import SlotsScene
from Roulette.Roulette import RouletteScene

if __name__ == "__main__":
    # 1. Initialize all imported pygame modules
    pygame.init()

    # 2. Create the actual display surface using the size from Constants
    screen = pygame.display.set_mode(Constants.Screen_Size)
    pygame.display.set_caption("Game of Chance")

    # 3. Create a clock object to control frame rate
    clock = pygame.time.Clock()

    # 4. Initialize Manager with the actual screen and clock OBJECTS
    game = SceneManager(screen, clock)

    # 5. Register and start your scenes
    game.add_scene("HUB", HubScene())
    game.add_scene("DATING", isaacDatingSim.DatingSimScene(player_name="Player"))
    game.add_scene("RUSSIANROULETTE", RussianRouletteScene(screen, clock))
    game.add_scene("SLOTS", SlotsScene(screen, clock))
    game.add_scene("BLACKJACK", BlackjackScene(screen))
    game.add_scene("ROULETTE", RouletteScene(screen, clock))
    game.switch_scene("HUB")
    
    # 6. Start the game loop
    game.run()

    pygame.quit()