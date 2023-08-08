import pygame, sys
from abc import ABC, abstractmethod
import copy
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')               # log

class ChessGame: 
    title = "ChessGame"
    def __init__(self, width, height):
        self.width = width
        self.height = height
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.window.fill((255, 255, 255))
        self.initial = Initial_interface(self.window, self.width, self.height)  # before start interface
        self.clock = pygame.time.Clock()  # timer
        self.fps = 60        # frame
        self.turn_time = 60  # time for one turn
    #----------------------------before start------------------------
    def run_initial_interface(self):
        self.initial.draw_initial_text()
        self.initial.draw_start_button()
        pygame.display.flip()

        waiting_for_start = True
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.initial.if_start(mouse_pos):
                        waiting_for_start = False
        self.run()
    #---------------------------------------start--------------------------------
    def run(self):
        running = True
        #----------------------------------Initialization-------------------------------
        current_player = 'white'       # start from white
        time_left = self.turn_time
        self.cell_size = self.width // 9        # chessboard cells size
        self.user_space = 100                   # UI space
        self.label_width = self.cell_size/2

        game_logic = Game_logic(None, current_player, time_left, self.turn_time)
        game_render = Game_renderer(self.window, self.width, self.height, self.cell_size, self.user_space, self.label_width, game_logic)
        while running:
            self.window.fill((255, 255, 255))
            self.mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:             # quit game
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:  # mouse clicked event
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_row = (self.mouse_pos[1] - self.user_space - self.label_width) // int(self.cell_size)
                    clicked_col = (self.mouse_pos[0] - self.label_width) // int(self.cell_size)
                    clicked_position = (int(clicked_row), int(clicked_col))                                           # get clicked position of chessboard ( row, col )
                    game_logic.En_passant(clicked_position)                                                           # liasten to the En passant event
                    game_logic.handle_click(clicked_position)                                                         # normal click operation
                    game_render.render_promote_button(pygame.MOUSEBUTTONDOWN)                                         # render promote botton
                    game_render.render_regret_button(pygame.MOUSEBUTTONDOWN)                                          # render regret button

            past_time = self.clock.tick(self.fps)    
            game_logic.update_timer(past_time)      # time update
            game_render.render()                    # Render interface and game

            pygame.display.flip()
        pygame.quit()

class Initial_interface:
    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height
        self.start_game = False
        self.padding = 10
        self.button_font = pygame.font.Font(None, 36)
        self.button_text = self.button_font.render("Start Game", True, (0, 0, 0))
        self.button_rect = self.button_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.button_rect.inflate_ip(self.padding * 2, self.padding * 2)
        self.draw_start_button()
        self.draw_initial_text()

    def draw_initial_text(self):
        font = pygame.font.Font(None, 48)
        text = font.render("Chess Game", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.window.blit(text, text_rect)

    def draw_start_button(self):
        pygame.draw.rect(self.window, (200, 200, 200), self.button_rect) 
        self.window.blit(self.button_text, self.button_rect.move(self.padding, self.padding))

    def if_start(self, mouse_pos):  
        return self.button_rect.collidepoint(mouse_pos)

class Game_renderer:
    def __init__(self, window, width, height, cell_size, user_space, label_width, game_logic):
        self.window = window
        self.width = width                      
        self.height = height
        self.cell_size = cell_size
        self.user_space = user_space
        self.label_width = label_width
        self.board_width = width - self.label_width*2                          
        self.board_height = height - self.user_space*2 - self.label_width*2
        self.game_logic = game_logic            # game state
        self.buttons = None
        self.UI_y2 = self.user_space/2
        self.UI_y1 = self.height - self.user_space // 2

        self.chessboard_coordinate = {(x, y): None for x in range(8) for y in range(8)}  # Center coordinates for each cell
        for row in range(8):
            for col in range(8):
                x = self.label_width + (col + 0.5) * self.cell_size
                y = self.user_space + self.label_width + (row + 0.5) * self.cell_size
                self.chessboard_coordinate[(row, col)] = (x, y)

    def render(self):                           # render  ( timer | label | board | pieces | movable route | regret button | check warn | promote button )
        self.render_timer()
        self.render_label()
        self.render_board()
        self.render_pieces()
        self.render_movable_route()             # render movable route (when piece be selected)
        self.render_regret_button(None)
        self.render_check()
        self.render_promote_button(None)
        pygame.display.flip()

    def render_timer(self):               # timer
        x1 = self.width // 8
        y1 = self.UI_y1
        x2 = self.width*7 // 8
        y2 = self.UI_y2
        font = pygame.font.Font(None, 36)
        pygame.draw.rect(self.window, (0, 0, 0), (0, 0, self.width, self.user_space))
        pygame.draw.rect(self.window, (255, 255, 255), (0, self.height-self.user_space, self.width, self.user_space))
        timer_text1 = pygame.font.Font(None, 36).render(f"Time Left: {int(self.game_logic.time_left)}",True,(0, 0, 0))
        timer_text2 = pygame.font.Font(None, 36).render(f"Time Left: {int(self.game_logic.time_left)}",True,(255, 255, 255))
        text_rect1 = timer_text1.get_rect(center=(x1, y1))
        text_rect2 = timer_text2.get_rect(center=(x2, y2))
        if self.game_logic.current_player == 'white':
            self.window.blit(timer_text1, text_rect1)
        elif self.game_logic.current_player == 'black':
            self.window.blit(timer_text2, text_rect2)

    def render_label(self):                # label
        pygame.draw.rect(self.window, (47, 45, 42), (0, self.user_space, self.width, self.height - self.user_space*2))
        font = pygame.font.Font(None, 24)
        xlabels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ylabels = ['1', '2', '3', '4', '5', '6', '7', '8']
        for col, xlabel in enumerate(xlabels):
            x = self.label_width + col * self.cell_size + self.cell_size // 2
            y = self.user_space + self.label_width/2
            label_text = font.render(xlabel, True, (255, 255, 255))
            text_rect1 = label_text.get_rect(center=(x, y))
            text_rect2 = label_text.get_rect(center=(x, y + self.board_height + self.label_width))
            self.window.blit(label_text, text_rect1)
            self.window.blit(label_text, text_rect2)

        for row, ylabel in enumerate(ylabels):
            x = self.label_width // 2
            y = self.user_space + self.label_width + (7.5 - row)*self.cell_size
            label_text = font.render(ylabel, True, (255, 255, 255))
            text_rect1 = label_text.get_rect(center=(x, y))
            text_rect2 = label_text.get_rect(center=(x + self.board_width + self.label_width, y))
            self.window.blit(label_text, text_rect1)
            self.window.blit(label_text, text_rect2)

    def render_board(self):        # chessboard
        for row in range(8):
            for col in range(8):
                x = self.label_width + col * self.cell_size
                y = self.user_space + self.label_width + row * self.cell_size
                if (row + col) % 2 == 0:
                    pygame.draw.rect(self.window, (212, 164, 122), (x, y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.window, (175, 132, 95), (x, y, self.cell_size, self.cell_size))

    def render_pieces(self):       # pieces
        for row in range(8):
            for col in range(8):
                x = self.label_width + col * self.cell_size
                y = self.user_space + self.label_width + row * self.cell_size
                # rander pieces image
                piece = self.game_logic.chessboard[(row, col)]
                if piece and piece.image:
                    scaled_image = pygame.transform.scale(piece.image, (self.cell_size / 2 - 10, self.cell_size * 3 / 4))
                    self.window.blit(scaled_image, (x + self.cell_size / 4 + 4, y + self.cell_size / 6 - 4))

    def render_movable_route(self):    # movable route
        if self.game_logic.selected_piece is not None:
            movable_list = self.game_logic.selected_piece.find_movable_route(self.game_logic.chessboard)
            for row in range(8):
                for col in range(8):
                    if movable_list[row][col] == True:
                        pygame.draw.circle(self.window, (160, 14, 14), self.chessboard_coordinate[(row, col)], 5)

    def render_regret_button(self, event_type):     # regret button
        button_width = 60
        button_height = 40
        x1 = self.width // 2 - button_width
        y1 = self.UI_y1 - button_height // 2
        x2 = self.width // 2 + button_width // 2
        y2 = self.UI_y2 - button_height // 2
        self.regret_buttons = [
            Regret_button(x1 - 1.5 * button_width, y1, button_width, button_height, 'regret'),
            Regret_button(x2 + 1.5 * button_width, y2, button_width, button_height, 'regret'),
        ]

        for button in self.regret_buttons:
                button.draw(self.window)
                if(event_type == pygame.MOUSEBUTTONDOWN):
                    mouse_pos = pygame.mouse.get_pos()
                    if button.x < mouse_pos[0] < button.x + button.width and button.y < mouse_pos[1] < button.y + button.height:
                        button.click(self.game_logic)
                        return

    def render_check(self):         # check warn
        text_size = 40
        x1 = self.width // 2 - text_size //2
        y1 = self.UI_y2
        x2 = self.width // 2 + text_size // 2
        y2 = self.UI_y1
        font = pygame.font.Font(None, text_size)
        check_text = pygame.font.Font(None, 36).render(f"checked!!!",True,(252, 85, 49))
        text_rect1 = check_text.get_rect(center=(x1, y1))
        text_rect2 = check_text.get_rect(center=(x2, y2))
        if self.game_logic.check[0] == True:
            self.window.blit(check_text, text_rect1)
        if self.game_logic.check[1] == True:
            self.window.blit(check_text, text_rect2)

    def render_promote_button(self, event_type):        # pawn promotion button
        if self.game_logic.promote_piece is not None:
            button_width = 60
            button_height = 40
            button_gap = 20
            if self.game_logic.promote_piece.color == 'white':
                self.button_x = self.width * 3 // 4
                self.button_y = self.user_space + self.label_width*2 + self.board_height + (self.user_space - button_height) // 2
            elif self.game_logic.promote_piece.color == 'black':
                self.button_x = self.width // 6
                self.button_y = (self.user_space - button_height) // 2

            self.promote_buttons = [
                Promote_button(self.button_x - 1.5 * button_width - 0.5 * button_gap, self.button_y, button_width, button_height, 'Rook'),
                Promote_button(self.button_x - 0.5 * button_width, self.button_y, button_width, button_height, 'Knight'),
                Promote_button(self.button_x + 0.5 * button_width + 0.5 * button_gap, self.button_y, button_width, button_height, 'Bishop'),
                Promote_button(self.button_x + 1.5 * button_width + 1.0 * button_gap, self.button_y, button_width, button_height, 'Queen'),
            ]
            for button in self.promote_buttons:
                button.draw(self.window)
                if(event_type == pygame.MOUSEBUTTONDOWN):
                    mouse_pos = pygame.mouse.get_pos()
                    if button.x < mouse_pos[0] < button.x + button.width and button.y < mouse_pos[1] < button.y + button.height:
                        button.click(self.game_logic)
                        return

class Button(ABC):
    def __init__(self, x, y, width, height, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = (73, 73, 73)
        self.highlighted_color = (189, 189, 189)

    def draw(self, window):
        mouse = pygame.mouse.get_pos()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            pygame.draw.rect(window, self.highlighted_color, (self.x, self.y, self.width, self.height), 0)    # mouse_overハイライト
        else:
            pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)
        if self.text:
            font = pygame.font.SysFont('', 25)
            text = font.render(self.text, 1, (255,255,255))
            window.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    @abstractmethod
    def click(self, game_logic):
        pass

class Promote_button(Button):
    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height, text)

    def click(self, game_logic):
        if self.text == 'Rook':
            game_logic.promote_piece = Rook(game_logic.promote_piece.color, game_logic.promote_piece.position, game_logic.chessboard)
        elif self.text == 'Knight':
            game_logic.promote_piece = Knight(game_logic.promote_piece.color, game_logic.promote_piece.position, game_logic.chessboard)
        elif self.text == 'Bishop':
            game_logic.promote_piece = Bishop(game_logic.promote_piece.color, game_logic.promote_piece.position, game_logic.chessboard)
        elif self.text == 'Queen':
            game_logic.promote_piece = Queen(game_logic.promote_piece.color, game_logic.promote_piece.position, game_logic.chessboard)

        game_logic.chessboard[(game_logic.promote_piece.position)] = game_logic.promote_piece
        game_logic.promote_piece = None
        game_logic.selected_piece = None
        game_logic.is_pawn_event = False
        game_logic.reverse_player()
        game_logic.update_state()
        game_logic.if_check()
        game_logic.into_history_stack()

class Regret_button(Button):
    def __init__(self, x, y, width, height, text):
        super().__init__(x, y, width, height, text)

    def click(self, game_logic):
        try:
            logging.debug("Attempting to handle a regret action")
            if len(game_logic.history) > 1:                               # keep initial state
                logging.debug("History stack has more than one state")
                print("悔棋")
                game_logic.history.pop()                                  # pop current state
                previous_chessboard, previous_player, previous_promote_piece, previous_passant_piece, previous_is_pawn_event, previous_check = copy.deepcopy(game_logic.history[-1])  # get previous state's copy
                game_logic.chessboard = previous_chessboard
                game_logic.current_player = previous_player
                game_logic.promote_piece = previous_promote_piece
                game_logic.passant_piece = previous_passant_piece
                if game_logic.is_pawn_event == True and previous_is_pawn_event == False:
                    game_logic.time_left = game_logic.turn_time
                elif game_logic.is_pawn_event == False and previous_is_pawn_event == True:
                    game_logic.time_left = game_logic.pawn_time
                game_logic.is_pawn_event = previous_is_pawn_event
                game_logic.check = previous_check
                game_logic.selected_piece = None
                game_logic.update_state()
                game_logic.if_check()
                logging.info("Successfully restored the previous game state")
            else:
                logging.warning("Only the initial state remains in the history stack")
        except Exception as e:
            logging.error(f"Error occurred while handling regret action: {e}")

class Game_logic:
    def __init__(self, selected_piece, current_player, time_left, turn_time):
        self.chessboard = {(row, col): None for row in range(8) for col in range(8)}
        self.selected_piece = selected_piece
        self.current_player = current_player
        self.time_left = time_left
        self.turn_time = turn_time
        self.pawn_time = 10
        self.promote_piece = None
        self.passant_piece = {'left': None, 'right': None} 
        self.is_pawn_event = False
        self.check = [False, False]             #(black, white)
        self.initialize_pieces()
        self.king = {'black': None, 'white': None}                   # (black_king,  white_king)
        self.lose = {'black': False, 'white': False}                 # if lose
        self.history = []                       # stack
        self.if_check()
        self.into_history_stack()               # push initial state

    def initialize_pieces(self):     # initial position for pieces
        self.chessboard[(0, 0)] = Rook('black', (0, 0), self.chessboard)
        self.chessboard[(0, 1)] = Knight('black', (0, 1), self.chessboard)
        self.chessboard[(0, 2)] = Bishop('black', (0, 2), self.chessboard)
        self.chessboard[(0, 3)] = King('black', (0, 3), self.chessboard)
        self.chessboard[(0, 4)] = Queen('black', (0, 4), self.chessboard)
        self.chessboard[(0, 5)] = Bishop('black', (0, 5), self.chessboard)
        self.chessboard[(0, 6)] = Knight('black', (0, 6), self.chessboard)
        self.chessboard[(0, 7)] = Rook('black', (0, 7), self.chessboard)

        self.chessboard[(7, 0)] = Rook('white', (7, 0), self.chessboard)
        self.chessboard[(7, 1)] = Knight('white', (7, 1), self.chessboard)
        self.chessboard[(7, 2)] = Bishop('white', (7, 2), self.chessboard)
        self.chessboard[(7, 3)] = King('white', (7, 3), self.chessboard)
        self.chessboard[(7, 4)] = Queen('white', (7, 4), self.chessboard)
        self.chessboard[(7, 5)] = Bishop('white', (7, 5), self.chessboard)
        self.chessboard[(7, 6)] = Knight('white', (7, 6), self.chessboard)
        self.chessboard[(7, 7)] = Rook('white', (7, 7), self.chessboard)

        for col in range(8):
            self.chessboard[(1, col)] = Pawn('black', (1, col), self.chessboard)
            self.chessboard[(6, col)] = Pawn('white', (6, col), self.chessboard)

    def into_history_stack(self):               # always keep the initial state and push state per motion
        current_state = (copy.deepcopy(self.chessboard), self.current_player, copy.deepcopy(self.promote_piece), copy.deepcopy(self.passant_piece), self.is_pawn_event, copy.deepcopy(self.check))
        self.history.append(current_state)
#---------------------------------------------for debug----------------------------------------------
    # def print_state(self):
    #     i = 1
    #     while i <= len(self.history):
    #         print("Stack", -i, "  ", len(self.history))
    #         self.print_board()
    #         i += 1

    # def print_board(self):
    #     for row in range(8):
    #         for col in range(8):
    #             piece = self.chessboard[(row, col)]
    #             if piece is None:
    #                 print('..', end=' ')
    #             else:
    #                 if isinstance(piece, King):
    #                     print('Ki', end=' ')
    #                 if isinstance(piece, Queen):
    #                     print('Qu', end=' ')
    #                 if isinstance(piece, Rook):
    #                     print('Ro', end=' ')
    #                 if isinstance(piece, Bishop):
    #                     print('Bi', end=' ')
    #                 if isinstance(piece, Knight):
    #                     print('Kn', end=' ')
    #                 if isinstance(piece, Pawn):
    #                     print('Pa', end=' ')
    #         print()

    def update_state(self):            # update movable_list, 
        for row in range(8):
            for col in range(8):
                piece = self.chessboard[(row, col)]
                if piece:
                    piece.chessboard = self.chessboard
                    piece.update_movable_list()
                    if isinstance(piece, Pawn):
                        piece.image = pygame.image.load(f"game\image\{piece.color}_pawn.png")

    def update_timer(self, past_time):
        self.time_left -= past_time / 1000      # calculate time left
        if self.time_left <= 0:
            self.promote_piece = None
            self.passant_piece = None
            self.selected_piece = None
            self.reverse_player()
            self.is_pawn_event = False
            self.into_history_stack()

    def reverse_player(self):
        if self.current_player == 'black':
            self.current_player = 'white'
        elif self.current_player == 'white':
            self.current_player = 'black'
        self.time_left = self.turn_time

    def is_pawn_time(self, color, event):
        if event == 'promotion':
            self.is_pawn_event = True
            self.promote_piece.image = pygame.image.load(f"game\image\pawn_event.png")
            self.current_player = color
            self.time_left = self.pawn_time
            self.selected_piece = None
        elif event == 'En passant':
            self.is_pawn_event = True
            if self.passant_piece['left']:
                self.passant_piece['left'].image = pygame.image.load(f"game\image\pawn_event.png")
            if self.passant_piece['right']:
                self.passant_piece['right'].image = pygame.image.load(f"game\image\pawn_event.png")
            self.current_player = color
            self.time_left = self.pawn_time
            self.selected_piece = None

    def move_piece(self, selected_piece, clicked_position):
        self.chessboard[selected_piece.position] = None
        selected_piece.position = clicked_position
        if self.king['black'] == self.chessboard[clicked_position]:
            self.king['black'] = None
            self.check[0] = None
        elif self.king['white'] == self.chessboard[clicked_position]:
            self.king['white'] = None
            self.check[1] = None
        self.chessboard[clicked_position] = selected_piece
        self.update_state()

    def handle_click(self, clicked_position):
        if 0 <= clicked_position[0] < 8 and 0 <= clicked_position[1] < 8:
            clicked_piece = self.chessboard[clicked_position]
            if self.is_pawn_event == False and self.selected_piece is None:  # no selected -> select
                if clicked_piece is not None and clicked_piece.color == self.current_player: 
                    self.selected_piece = clicked_piece         # select
                    self.selected_position = clicked_position
            else:  # if there be piece selected
                if clicked_piece == self.selected_piece:    # piece selected were clicked
                    pass                                    # do nothing
                elif self.is_pawn_event == False and clicked_piece is not None and clicked_piece.color == self.current_player:  # clicked an unselected piece
                    self.selected_piece = clicked_piece     # reselect
                    self.selected_position = clicked_position
                # clicked the cell which on selected piece's movable route 
                elif self.is_pawn_event == False and self.selected_piece.movable_list[int(clicked_position[0])][int(clicked_position[1])] == 1:
                    passant_judge  = abs(self.selected_position[0] - clicked_position[0]) # if pawn move 2cells -> judge En passant
                    self.move_piece(self.selected_piece, clicked_position)       # move
                    if isinstance(self.selected_piece, Pawn):
                        pawn = self.selected_piece
                        if pawn.first_move == True: # pawn first step
                            if passant_judge == 2:       # pawn Enpassant
                                row = pawn.position[0]
                                col = pawn.position[1]
                                if 0 <= col - 1 <= 7 and isinstance(self.chessboard[(row, col - 1)], Pawn) and self.chessboard[(row, col - 1)].color != self.current_player: # if En passant posible and opponent's piece
                                    self.passant_piece['left'] = self.chessboard[(row, col - 1)]
                                if 0 <= col + 1 <= 7 and isinstance(self.chessboard[(row, col + 1)], Pawn) and self.chessboard[(row, col + 1)].color != self.current_player: # if En passant posible and opponent's piece
                                    self.passant_piece['right'] = self.chessboard[(row, col + 1)]
                                if self.passant_piece['left']:
                                    self.is_pawn_time(self.passant_piece['left'].color, 'En passant')
                                elif self.passant_piece['right']:
                                    self.is_pawn_time(self.passant_piece['right'].color, 'En passant')
                            pawn.first_move = False
                        if pawn.color == 'white' and pawn.position[0] == 0 or pawn.color == 'black' and pawn.position[0] == 7: # pawn promotion
                            self.promote_piece = pawn
                            self.is_pawn_time(self.promote_piece.color, 'promotion')
                        else:
                            self.reverse_player()
                    else:
                        self.reverse_player()
                    self.if_check()
                    self.into_history_stack()           # push the state after movement
                    self.selected_piece = None
                    self.selected_position = None

    def En_passant(self, clicked_position):
            goal_position = None
            if self.is_pawn_event == True:
                if 0 <= clicked_position[0] < 8 and 0 <= clicked_position[1] < 8:
                    clicked_piece = self.chessboard[clicked_position]
                    if self.passant_piece['left']:
                        if clicked_piece == self.passant_piece['left']:
                            if clicked_piece.color == 'white':
                                goal_position = (clicked_position[0] - 1, clicked_position[1] + 1)
                            elif clicked_piece.color == 'black':
                                goal_position = (clicked_position[0] + 1, clicked_position[1] + 1)
                    if self.passant_piece['right']:
                        if clicked_piece == self.passant_piece['right']:
                            if clicked_piece.color == 'white':
                                goal_position = (clicked_position[0] - 1, clicked_position[1] - 1)
                            elif clicked_piece.color == 'black':
                                goal_position = (clicked_position[0] + 1, clicked_position[1] - 1)
                    if(goal_position):
                        self.move_piece(clicked_piece, goal_position)
                    self.is_pawn_event = False
                    self.passant_piece = {'left': None, 'right': None}
                    self.update_state()
                    self.if_check()
                    self.into_history_stack()           # push the state after movement

    def update_real_time_king(self):          # get real time king (black_king, white_king)
        for row in range(8):
            for col in range(8):
                piece = self.chessboard[(row, col)]
                if  piece and isinstance(piece, King):   # find each players king
                    if piece.color == 'black':
                        self.king['black'] = piece
                    elif piece.color == 'white':
                        self.king['white'] = piece
    
    def if_check(self):
        self.update_real_time_king()
        print()
        self.check[0] = self.if_be_checked('black')
        self.check[1] = self.if_be_checked('white')
    
    def if_be_checked(self, player):
        print(player)
        for row in range(8):
            for col in range(8):
                piece = self.chessboard[(row, col)]
                if piece and piece != self.king[player] and piece.color != player: # if there be piece on (row, col)  find movable position
                    for x in range(8):
                        for y in range(8):
                            if piece.movable_list[x][y] == True:     # movable position
                                if isinstance(piece, Bishop):
                                    print(piece, piece.position, (x, y))
                                if self.chessboard[(x, y)] and self.chessboard[(x, y)] == self.king[player]:        # if king on the movable position
                                    return True
        return False                  # can't be checked by all opponent's pieces

class Piece(ABC):
    def __init__(self, color, position, chessboard):
        self.color = color
        self.position = position
        self.image = None
        self.chessboard = chessboard
        self.movable_list = [[False for _ in range(8)] for _ in range(8)]   # the movable cell on chessboard

    def load_image(self, image_path):
        self.image = pygame.image.load(image_path)

    def update_movable_list(self):
        self.movable_list = self.find_movable_route(self.chessboard)

    @abstractmethod
    def find_movable_route(self, chessboard):
        self.chessboard = chessboard
        self.movable_list = [[False for _ in range(8)] for _ in range(8)]   # when chessboard update, reset movable_list

    def __deepcopy__(self, memo):
        cls = self.__class__             # get the piece's (child) class
        new_piece = cls(self.color, self.position, self.chessboard)     # creat the copy instance
        #--------------------------------copy attribute for the instance-------------------------------------
        new_piece.color = copy.deepcopy(self.color, memo)
        new_piece.position = copy.deepcopy(self.position, memo)
        new_piece.movable_list = copy.deepcopy(self.movable_list, memo)
        new_piece.image = self.image                           # surface attribute
        return new_piece

class King(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        image_path = f"game\image\{color}_king.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route( chessboard)
        for i in range(3):
            for j in range(3):
                x = int(self.position[0]-1 + i)
                y = int(self.position[1]-1 + j)
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if chessboard[(x, y)] is None or chessboard[(x, y)].color != self.color:
                        self.movable_list[x][y] = True
        return self.movable_list

class Queen(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        image_path = f"game\image\{color}_queen.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route(chessboard)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dx, dy in directions:
            x = int(self.position[0] + dx)
            y = int(self.position[1] + dy)
            while(0 <= x <= 7 and 0 <= y <= 7):
                if chessboard[(x, y)] is None:
                    self.movable_list[x][y] = True
                elif chessboard[(x, y)].color != self.color:
                    self.movable_list[x][y] = True
                    break
                else:
                    break
                x += dx
                y += dy
        return self.movable_list

class Rook(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        image_path = f"game\image\{color}_rook.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route(chessboard)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            x = int(self.position[0] + dx)
            y = int(self.position[1] + dy)
            while(0 <= x <= 7 and 0 <= y <= 7):
                if chessboard[(x, y)] is None:
                    self.movable_list[x][y] = True
                elif chessboard[(x, y)].color != self.color:
                    self.movable_list[x][y] = True
                    break
                else:
                    break
                x += dx
                y += dy
        return self.movable_list

class Bishop(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        image_path = f"game\image\{color}_bishop.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route(chessboard)
        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for dx, dy in directions:
            x = int(self.position[0] + dx)
            y = int(self.position[1] + dy)
            while(0 <= x <= 7 and 0 <= y <= 7):
                if chessboard[(x, y)] is None:
                    self.movable_list[x][y] = True
                elif chessboard[(x, y)].color != self.color:
                    self.movable_list[x][y] = True
                    break
                else:
                    break
                x += dx
                y += dy
        return self.movable_list

class Knight(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        image_path = f"game\image\{color}_knight.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route(chessboard)
        directions = [(1, 2), (2, 1), (-1, 2), (-2, 1), (-1, -2), (-2, -1), (1, -2), (2, -1)]
        for dx, dy in directions:
            x = int(self.position[0] + dx)
            y = int(self.position[1] + dy)
            if 0 <= x <= 7 and 0 <= y <= 7:
                if chessboard[(x, y)] is None or chessboard[(x, y)].color != self.color:
                    self.movable_list[x][y] = True
        return self.movable_list

class Pawn(Piece):
    def __init__(self, color, position, chessboard):
        super().__init__(color, position, chessboard)
        self.first_move = True
        self.event = False
        image_path = f"game\image\{color}_pawn.png"
        self.load_image(image_path)

    def find_movable_route(self, chessboard):
        super().find_movable_route(chessboard)
        if self.color == 'black':
            directions = [(1, 0)] if not self.first_move else [(1, 0), (2, 0)]
            for dx, dy in directions:
                x = int(self.position[0] + dx)
                y = int(self.position[1] + dy)
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if chessboard[(x, y)] is None:
                        self.movable_list[x][y] = True
                for dx, dy in [(1, 1), (1, -1)]:
                    x = int(self.position[0] + dx)
                    y = int(self.position[1] + dy)
                    if 0 <= x <= 7 and 0 <= y <= 7 and chessboard[(x, y)] and chessboard[(x, y)].color != self.color:
                        self.movable_list[x][y] = True
        elif self.color == 'white':
            directions = [(-1, 0)] if not self.first_move else [(-1, 0), (-2, 0)]
            for dx, dy in directions:
                x = int(self.position[0] + dx)
                y = int(self.position[1] + dy)
                if 0 <= x <= 7 and 0 <= y <= 7:
                    if chessboard[(x, y)] is None:
                        self.movable_list[x][y] = True
                for dx, dy in [(-1, 1), (-1, -1)]:
                    x = int(self.position[0] + dx)
                    y = int(self.position[1] + dy)
                    if 0 <= x <= 7 and 0 <= y <= 7  and chessboard[(x, y)] and chessboard[(x, y)].color != self.color:
                        self.movable_list[x][y] = True
        return self.movable_list
    
    def __deepcopy__(self, memo):
        new_pawn = super().__deepcopy__(memo)
        new_pawn.first_move = copy.deepcopy(self.first_move, memo)   # copy first_move
        return new_pawn

if __name__ == "__main__":
    chess_game = ChessGame(720, 920)
    chess_game.run_initial_interface()
