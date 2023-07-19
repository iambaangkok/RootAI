import pygame
from pygame import Color, Vector2, Surface, Rect

from src.config import Config, Colors
from src.game.Building import Building
from src.game.FactionBoard import FactionBoard
from src.utils import text_utils

BUILDING_COST = [0, 1, 2, 3, 3, 4]
BUILDING_REWARD_VP = {
    Building.SAWMILL: [0, 1, 2, 3, 4, 5],
    Building.WORKSHOP: [0, 2, 2, 3, 4, 5],
    Building.RECRUITER: [0, 1, 2, 3, 3, 4]
}

BUILDING_REWARD_CARD = {
    Building.SAWMILL: [0, 0, 0, 0, 0, 0],
    Building.WORKSHOP: [0, 0, 0, 0, 0, 0],
    Building.RECRUITER: [0, 0, 1, 1, 2, 2]
}
BUILDING_TRACKER_NAME = [Building.SAWMILL, Building.WORKSHOP, Building.RECRUITER]

MARQUISE_ACTIONS = {
    'Birdsong': ['Next'],
    'Daylight': {
        '1': ['Craft', 'Next'],
        '2': ['Battle', 'March', 'Recruit', 'Build', 'Overwork', 'Next']
    },
    'Evening': ['Next/Skip'],
    'None': []
}

UPDATE_ARROW = {
    pygame.K_UP: Vector2(0, -1),
    pygame.K_DOWN: Vector2(0, 1),
    pygame.K_LEFT: Vector2(-1, 0),
    pygame.K_RIGHT: Vector2(1, 0)
}


class MarquiseBoard(FactionBoard):
    def __init__(self, name: str, color: Color, reserved_warriors: int, starting_point: Vector2):
        super().__init__(name, color, reserved_warriors, starting_point)

        self.building_trackers: {Building, int} = {
            Building.SAWMILL: 2,
            Building.WORKSHOP: 5,
            Building.RECRUITER: 3
        }

        self.marquise_action = self.MarquiseActionBoard(Vector2(0.75 * Config.SCREEN_WIDTH, 0.0 * Config.SCREEN_HEIGHT))

    def update_phase(self, phase, sub_phase):
        self.marquise_action.update_phase(phase, sub_phase)

    def move_arrow(self, direction):
        self.marquise_action.move_arrow(direction)

    def draw(self, screen: Surface):
        super().draw(screen)

        for i in range(3):
            self.draw_tracker(screen, BUILDING_TRACKER_NAME[i],
                              self.starting_point + Vector2(5, 45 * (i + 6) + 25 + self.text_surface.get_height() + 20))

        self.marquise_action.draw(screen)

    def draw_tracker(self, screen: Surface, title: Building, starting_point: Vector2):

        # Text
        title_text = Config.FONT_SM_BOLD.render(str(title), True, Colors.ORANGE)
        shift: Vector2 = Vector2(10, 10)

        screen.blit(title_text, starting_point + shift)

        img_size: Vector2 = Vector2(40, 40)

        alpha = 200
        img = pygame.image.load("../assets/images/marquise/{}.png".format(title))
        img = pygame.transform.scale(img, img_size)
        img.set_alpha(alpha)
        alpha = 128
        new_img = img.copy()
        new_img.set_alpha(alpha)

        gap = 10
        offset_x = 100

        for j in range(6):
            if j < self.building_trackers[title]:
                draw_img = new_img
            else:
                draw_img = img
            screen.blit(draw_img,
                        (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if BUILDING_REWARD_VP[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(BUILDING_REWARD_VP[title][j]), True, (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.GREY_DARK_2)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x, starting_point.y))

            if BUILDING_REWARD_CARD[title][j] > 0:
                reward = Config.FONT_SM_BOLD.render("+" + str(BUILDING_REWARD_CARD[title][j]), True, (206, 215, 132))
                reward = text_utils.add_outline(reward, 2, Colors.BLUE)

                screen.blit(reward, (starting_point.x + (img_size.x + gap) * j + gap + offset_x,
                                     starting_point.y + img_size.y - Config.FONT_SM_BOLD.get_height()))

    class MarquiseActionBoard:
        arrow_index = Vector2(0, 0)

        row_width = 30
        col_width = 175
        col = 2
        phase = ''
        sub_phase = ''

        def __init__(self, starting_point: Vector2):
            self.hasRecruited = False
            self.starting_point = starting_point
            pass

        def update_phase(self, phase, sub_phase):
            self.phase = phase
            self.sub_phase = sub_phase

        def get_action(self):
            return MARQUISE_ACTIONS[self.phase][self.sub_phase]

        def draw(self, screen: Surface):

            phase = Config.FONT_MD_BOLD.render("{}".format(self.phase), True, Colors.ORANGE)
            shift = Vector2(10, 0.05 * Config.SCREEN_HEIGHT)
            screen.blit(phase, self.starting_point + shift)

            self.draw_arrow(screen)
            self.draw_actions(screen)

        def move_arrow(self, direction):

            row = len(MARQUISE_ACTIONS[self.phase][self.sub_phase]) // 2 + 1;

            if direction in UPDATE_ARROW.keys():
                new_arrow_index = self.arrow_index + UPDATE_ARROW[direction]
                if len(MARQUISE_ACTIONS[self.phase][self.sub_phase]) > new_arrow_index[0] + new_arrow_index[1] * self.col >= 0 \
                        and self.col > new_arrow_index[0] >= 0 \
                        and row > new_arrow_index[1] >= 0:
                    self.arrow_index = new_arrow_index

        def draw_arrow(self, screen):
            arrow = Config.FONT_MD_BOLD.render(">", True, Colors.WHITE)
            shift = Vector2(10, 0.09 * Config.SCREEN_HEIGHT)
            screen.blit(arrow, self.starting_point + shift + Vector2(self.arrow_index[0] * self.col_width, self.arrow_index[1] * self.row_width))

        def draw_actions(self, screen):
            shift = Vector2(10 + 0.02 * Config.SCREEN_WIDTH, 0.09 * Config.SCREEN_HEIGHT)

            actions = MARQUISE_ACTIONS[self.phase][self.sub_phase]

            ind = 0
            for action in actions:
                action_text = Config.FONT_MD_BOLD.render(action, True, Colors.WHITE)
                screen.blit(action_text, self.starting_point + shift + Vector2(ind % self.col * self.col_width, ind // self.col * self.row_width))
                ind = ind + 1
