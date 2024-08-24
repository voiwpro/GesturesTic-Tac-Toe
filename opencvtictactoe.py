import pygame
import sys
import cv2
import mediapipe as mp
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 700  # Adjusted height to add space for the outcome display
GRID_SIZE = 3
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
LINE_WIDTH = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('TIC-TAC-TOE')
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont('Arial', 65, bold=True)
mainfont = pygame.font.SysFont('Arial', 40, bold=True)

# Button settings
button_width = 200
button_height = 50

# Calculate button positions
start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height, button_width, button_height)
end_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 + button_height, button_width, button_height)
play_again_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, SCREEN_HEIGHT // 2 - button_height // 2, button_width, button_height)

# Initialize hand gesture recognition with MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Initialize previous wrist position
previous_wrist_x, previous_wrist_y = None, None

# Function to recognize hand gestures
def recognize_gesture(hand_landmarks):
    global previous_wrist_x, previous_wrist_y  # Declare as global to modify outside the function

    # Check if all fingers are open (start game)
    all_fingers_open = all(l.y < hand_landmarks[mp_hands.HandLandmark.WRIST].y for l in hand_landmarks)
    if all_fingers_open:
        print("Gesture Recognized: start_game")
        return 'start_game'

    # Detect finger positions
    index_tip = hand_landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = hand_landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = hand_landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = hand_landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = hand_landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = hand_landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = hand_landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = hand_landmarks[mp_hands.HandLandmark.PINKY_MCP]
    wrist = hand_landmarks[mp_hands.HandLandmark.WRIST]

    # Initialize previous wrist position if not set
    if previous_wrist_x is None or previous_wrist_y is None:
        previous_wrist_x, previous_wrist_y = wrist.x, wrist.y
        return None

    # Calculate the movement
    delta_x = wrist.x - previous_wrist_x
    delta_y = wrist.y - previous_wrist_y

    # Update previous wrist position
    previous_wrist_x, previous_wrist_y = wrist.x, wrist.y

    # Define movement thresholds
    threshold = 0.05
    if delta_x > threshold:
        print("Gesture Recognized: right")
        return 'right'
    elif delta_x < -threshold:
        print("Gesture Recognized: left")
        return 'left'
    elif delta_y > threshold:
        print("Gesture Recognized: down")
        return 'down'
    elif delta_y < -threshold:
        print("Gesture Recognized: up")
        return 'up'

    # Check for gestures to place 'X' or 'O'
    index_finger_up = index_tip.y < index_mcp.y
    middle_finger_up = middle_tip.y < middle_mcp.y
    ring_finger_down = ring_tip.y > ring_mcp.y
    pinky_finger_down = pinky_tip.y > pinky_mcp.y

    if index_finger_up and middle_finger_up and ring_finger_down and pinky_finger_down:
        print("Gesture Recognized: O")
        return 'O'
    elif index_finger_up and ring_finger_down and pinky_finger_down:
        print("Gesture Recognized: X")
        return 'X'

    return None

def draw_grid(selected_row, selected_col):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            pygame.draw.rect(screen, GREY, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            if row == selected_row and col == selected_col:
                pygame.draw.rect(screen, RED, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)  # Highlight the selected cell
            else:
                pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)  # Regular grid lines

def draw_marks(board):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == 'X':
                draw_x(col * CELL_SIZE, row * CELL_SIZE)
            elif board[row][col] == 'O':
                draw_o(col * CELL_SIZE, row * CELL_SIZE)

def draw_x(x, y):
    padding = 20
    pygame.draw.line(screen, RED, (x + padding, y + padding), (x + CELL_SIZE - padding, y + CELL_SIZE - padding), LINE_WIDTH)
    pygame.draw.line(screen, RED, (x + CELL_SIZE - padding, y + padding), (x + padding, y + CELL_SIZE - padding), LINE_WIDTH)

def draw_o(x, y):
    padding = 20
    pygame.draw.circle(screen, BLUE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 2 - padding, LINE_WIDTH)

def check_winner(board):
    # Check rows for a win
    for row in board:
        if row.count(row[0]) == len(row) and row[0] != '':
            return row[0]

    # Check columns for a win
    for col in range(len(board)):
        check = []
        for row in board:
            check.append(row[col])
        if check.count(check[0]) == len(check) and check[0] != '':
            return check[0]

    # Check diagonals for a win
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2]

    # Check for a draw
    if all(all(row) for row in board):
        return 'Draw'

    # No winner or draw yet
    return None

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def computer_move(board):
    empty_cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE) if board[row][col] == '']
    if empty_cells:
        row, col = random.choice(empty_cells)
        board[row][col] = 'O'

def main_game():
    global previous_wrist_x, previous_wrist_y  # Declare as global to modify outside the function
    board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    game_over = False
    winner = None
    selected_row, selected_col = 0, 0
    player_turn = True  # Player starts first

    # Initialize OpenCV VideoCapture
    cap = cv2.VideoCapture(0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_over:
                    if play_again_button_rect.collidepoint(event.pos):
                        main_game()  # Restart the game
                else:
                    pos = pygame.mouse.get_pos()
                    col = pos[0] // CELL_SIZE
                    row = pos[1] // CELL_SIZE
                    if board[row][col] == '':
                        board[row][col] = 'X'
                        winner = check_winner(board)
                        player_turn = False
                        if winner or all(all(row) for row in board):
                            game_over = True

        # Capture frame from camera
        ret, frame = cap.read()
        if not ret:
            continue

        # Process frame with MediaPipe Hands
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False
        results = hands.process(frame)
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Handle hand landmarks and gestures
        if results.multi_hand_landmarks and player_turn and not game_over:
            for hand_landmarks in results.multi_hand_landmarks:
                gesture = recognize_gesture(hand_landmarks.landmark)
                if gesture == 'right' and selected_col < GRID_SIZE - 1:
                    selected_col += 1
                elif gesture == 'left' and selected_col > 0:
                    selected_col -= 1
                elif gesture == 'up' and selected_row > 0:
                    selected_row -= 1
                elif gesture == 'down' and selected_row < GRID_SIZE - 1:
                    selected_row += 1
                elif gesture == 'X' and board[selected_row][selected_col] == '':
                    board[selected_row][selected_col] = 'X'
                    winner = check_winner(board)
                    player_turn = False
                    if winner or all(all(row) for row in board):
                        game_over = True

        if not player_turn and not game_over:
            computer_move(board)
            winner = check_winner(board)
            player_turn = True
            if winner or all(all(row) for row in board):
                game_over = True

        # Display game screen
        screen.fill(WHITE)
        draw_grid(selected_row, selected_col)  # Highlight selected cell
        draw_marks(board)
        if game_over:
            draw_text(f'{winner} wins!' if winner else 'Draw!', font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            pygame.draw.rect(screen, BLACK, play_again_button_rect, 2)
            draw_text('Play Again', mainfont, BLACK, play_again_button_rect.centerx, play_again_button_rect.centery)
        pygame.display.update()
        clock.tick(60)

def main_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(pos):
                        main_game()
                    elif end_button_rect.collidepoint(pos):
                        running = False

        screen.fill(WHITE)
        draw_text('TIC-TAC-TOE', font, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        pygame.draw.rect(screen, BLACK, start_button_rect, 2)
        draw_text('Start Game', mainfont, BLACK, start_button_rect.centerx, start_button_rect.centery)
        pygame.draw.rect(screen, BLACK, end_button_rect, 2)
        draw_text('Quit', mainfont, BLACK, end_button_rect.centerx, end_button_rect.centery)
        pygame.display.update()

if __name__ == '__main__':
    main_menu()
