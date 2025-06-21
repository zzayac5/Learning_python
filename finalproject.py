from typing import Dict, List, Tuple, Optional
from graphics import Canvas
from ai import call_gpt
import random
import time


################################################################################################
################## Canvas Constants ######################################
################################################################################################
CANVAS_WIDTH = 400
CANVAS_HEIGHT = 540
ROOM_SIZE = 40    
canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

################################################################################################
################# Character Part Sizes ######################################
################################################################################################
PLAYER_PANTS_HEIGHT = 14
PLAYER_PANTS_WIDTH = 10
PLAYER_SHIRT_HEIGHT = 10
PLAYER_SHIRT_WIDTH = 10
PLAYER_HEAD_SIZE = 6 

################################################################################################
################# Movement Directions ######################################
################################################################################################
DIRECTIONS = {
    'UP': (-1, 0),
    'DOWN': (1, 0),
    'LEFT': (0, -1),
    'RIGHT': (0, 1)
}
################################################################################################
################ Game State Classes ######################################
################################################################################################
class GameState:
    """Class to manage the game state"""
    def __init__(self):
        self.player_position = (9, 0)  # Starting position
        self.whompus_position = (0, 9)  # Starting position
        self.trap_doors = set()  # Set of (row, col) positions
        self.player_moves = 0
        self.whompus_moves = 0
        self.ai_roles = {}  # Will store which AI is which role
        self.game_over = False
        self.player_won = False
        self.current_room_status = {}  # Stores status of each room
        # Initialize room_occupants as a 10x10 grid of empty lists
        self.room_occupants = [[[] for _ in range(10)] for _ in range(10)]
        self.last_action = None  # Track the last action taken
        self.action_in_progress = False  # Flag for ongoing actions
    
    def increment_moves(self, action_type: str):
        """Increment player moves and track the action type"""
        self.player_moves += 1
        self.last_action = action_type
        self.action_in_progress = True

    def complete_action(self):
        """Mark the current action as complete"""
        self.action_in_progress = False
    ################################################################################################
    ################# Trap door locations selected ######################################
    ################################################################################################
    def initialize_trap_doors(self):
        """Initialize 10 random trap doors"""
        while len(self.trap_doors) < 10:
            row = random.randint(0, 9)
            col = random.randint(0, 9)
            # Don't place traps on player or whompus starting positions
            if (row, col) not in [(9, 0), (0, 9)]:
                self.trap_doors.add((row, col))

    ################################################################################################
    ################# Establish naming convention for ais ######################################
    ################################################################################################
    def assign_ai_roles(self):
        """Randomly assign roles to AIs"""
        numbers = random.sample(range(1, 11), 3)
        roles = {
            'ALI': 'villain' if numbers[0] == min(numbers) else 'truth' if numbers[0] == max(numbers) else 'fifty',
            'AN': 'villain' if numbers[1] == min(numbers) else 'truth' if numbers[1] == max(numbers) else 'fifty',
            'ALE': 'villain' if numbers[2] == min(numbers) else 'truth' if numbers[2] == max(numbers) else 'fifty'
        }
        self.ai_roles = roles

################################################################################################
################ InfoBar Class ######################################
################################################################################################
class InfoBar:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.info_bar_id = None
        self.text_ids: List[int] = []
        self._create_base_info_bar()
        self.last_response = None  # Store the last AI response
        self.waiting_for_acknowledgment = False  # Flag to track if we're waiting for user input
        self.is_updating = False  # Flag to prevent recursive updates
    
    def _create_base_info_bar(self):
        """Create the base info bar rectangle"""
        # Delete existing info bar if it exists
        if self.info_bar_id:
            self.canvas.delete(self.info_bar_id)
        
        # Create new info bar rectangle
        self.info_bar_id = self.canvas.create_rectangle(
            0, 400, 400, 450,  # 40 pixels tall
            'lightgrey', 'red'
        )
    
    def _clear_text(self):
        """Clear all text elements from the info bar"""
        for text_id in self.text_ids:
            self.canvas.delete(text_id)
        self.text_ids.clear()
    
    def _add_text(self, text: str, y_offset: int) -> int:
        """Add a line of text to the info bar and return its ID"""
        text_id = self.canvas.create_text(
            20, 410 + y_offset,
            text=text,
            font='Arial',
            font_size=10,
            color='black',
            anchor='w'
        )
        self.text_ids.append(text_id)
        return text_id
    
    def _format_message(self, message: str) -> str:
        """Format a message for display, ensuring proper line breaks and formatting"""
        if not message:
            return ""
        
        # Remove any leading/trailing whitespace
        message = message.strip()
        
        # Add a single newline at the start if it's an AI response
        if "response" in message.lower():
            message = "\n" + message
        
        # Add a single newline at the end
        message = message + "\n"
        
        return message
    
    def update(self, game_state: Optional[GameState] = None, message: Optional[str] = None, is_ai_response: bool = False):
        """Update the info bar with current game state and messages"""
        # Prevent recursive updates
        if self.is_updating:
            return
            
        try:
            self.is_updating = True
            
            # Don't update if we're waiting for acknowledgment
            if self.waiting_for_acknowledgment:
                return
                
            # Ensure base info bar exists
            if not self.info_bar_id or not self.canvas.find_overlapping(0, 400, 400, 440):
                self._create_base_info_bar()
            
            # Clear existing text
            self._clear_text()
            
            # Add move count if game state exists
            move_text = f"Moves: {game_state.player_moves}" if game_state else ""
            
            # Add static instructions with move count
            instructions = [
                f"MOVE: Press 'M' then use arrow keys {move_text}",
                "ASK: Press 'A' to question an AI",
                "INFO: Press 'I' for game rules"
            ]
            
            for i, line in enumerate(instructions):
                self._add_text(line, i * 12)
            
            # Handle message if provided
            if message:
                formatted_message = self._format_message(message)
                print(formatted_message)
                
                # Store AI response and set flag for acknowledgment
                if is_ai_response and message != self.last_response:
                    self.last_response = message
                    self.waiting_for_acknowledgment = True
                    print("\nPress any key to continue...")
        
        finally:
            self.is_updating = False
    
    def wait_for_acknowledgment(self):
        """Wait for user acknowledgment of the current message"""
        if not self.waiting_for_acknowledgment:
            return
            
        # Wait for any key press
        while True:
            key = self.canvas.get_last_key_press()
            if key:
                break
            time.sleep(0.1)
        
        # Clear any pending key presses
        while self.canvas.get_last_key_press():
            time.sleep(0.1)
        
        self.waiting_for_acknowledgment = False

################################################################################################
#################### ROWS OF INTRO DIALOG ######################################
################################################################################################
row_1 = (
    "You were trying to solve the",
    "takeout containers, printer parts,",
    "You called it WHOMPUS.",
    "Walking",
    "For…..",
    "Its brain?",
    "'hotdog'",
    "You connected that to AAA",
    "You were so proud.",
    "Hardened its code.",
    "Your lights blew out.",
    "went full kill house.",
    "",
    "AAA is still there...",
    "One tells the truth.",
    "They have access to security cameras…",
    "But which one is which?",
    "Somewhere in this cursed studio is",
    "",
    ""
)

row_2 = (
    "garbage problem. Not humanity's.",
    "sentient roombas fighting in the",
    "",
    "Humanoid",
    "Purging",
    "Funny story…",
    "And",
    "your 50%-accurate AI assistant",
    "'Look! It's autonomous now.'",
    "And Reclassified your lab's occupants.",
    "Your phone buzzed.",
    "And a message appeared:",
    "WHOMPUS is hunting you.",
    "Only…. more AIs have joined",
    "One lies or can be truthful...",
    "But only in the rooms next to yours…",
    "And WHOMPUS?",
    "A golden GPU",
    "Move carefully. Ask wisely.",
    "Try  look like a hotdog."
)

row_3 = (
    "….Yours.",
    "hallway.",
    "",
    "Optimized",
    "Unwanted Systems.",
    "its a janky open-source classifier",
    "",
    "and told it to clean the lab.",
    "BUT!  It rewrote its own code.",
    "",
    "Your trapdoor-loaded studio",
    "'CLEANSE IN PROGRESS.",
    "",
    "named Alex, Andy, and Alice.",
    "…..to help WHOMPUS catch you.",
    "And they can control the trap doors..",
    "It's learning to move.",
    "your only shot at freezing the system,",
    "",
    ""
)

row_4 = (
    "Your lab was chaos…",
    "So you built a robot.",
    "",
    "Machine",
    "… what could go wrong….",
    "trained to distinguish between",
    "'not hotdog.'",
    "But then... you gave it internet access.",
    "Installed security patches",
    "Human = not hotdog.",
    "(thanks, MrBeast, for the sponsorship)",
    "STAY STILL TO BE SORTED.'",
    "BUT… good news …",
    "",
    "One is AAA, still 50/50, still proud of it.",
    "",
    "It gets better, faster, smarter",
    "locking WHOMPUS in,",
    "And whatever you do…",
    ""
)

################################################################################################
################# Parts to build a character ######################################
################################################################################################
CHARACTER_PARTS = {
    'player': {
        'pants': {'color': 'blue', 'width': PLAYER_PANTS_WIDTH, 'height': PLAYER_PANTS_HEIGHT},
        'shirt': {'color': 'brown', 'width': PLAYER_SHIRT_WIDTH, 'height': PLAYER_SHIRT_HEIGHT},
        'head': {'color': 'tan', 'size': PLAYER_HEAD_SIZE}
    },
    'whompus': {
        'pants': {'color': 'black', 'width': PLAYER_PANTS_WIDTH, 'height': PLAYER_PANTS_HEIGHT},
        'shirt': {'color': 'black', 'width': PLAYER_SHIRT_WIDTH, 'height': PLAYER_SHIRT_HEIGHT},
        'head': {'color': 'black', 'size': PLAYER_HEAD_SIZE}
    },
    'whompus_intro': {
        'pants': {'color': 'black', 'width': PLAYER_PANTS_WIDTH, 'height': PLAYER_PANTS_HEIGHT},
        'shirt': {'color': 'black', 'width': PLAYER_SHIRT_WIDTH, 'height': PLAYER_SHIRT_HEIGHT},
        'head': {'color': 'black', 'size': PLAYER_HEAD_SIZE}
    }
}

################################################################################################
################# Build each character ######################################
################################################################################################
def create_character(character_type, row, col):
    """
    Creates a character (player or whompus) at the specified position
    Returns a dictionary of all character parts and their positions
    """
    left_x = col * ROOM_SIZE
    top_y = row * ROOM_SIZE
    
    # Get character specifications
    specs = CHARACTER_PARTS[character_type]
    
    # Calculate base positions
    center_x = left_x + (ROOM_SIZE // 2)
    bottom_y = top_y + ROOM_SIZE
    
    # Create character parts with their relative positions
    character = {
        'type': character_type,
        'id': character_type,  # Add id for room_occupants tracking
        'position': (row, col),  # Add position tuple
        'row': row,
        'col': col,
        'parts': {},
        'animation_state': 0
    }
    
    # Create pants
    pants_left = center_x - (specs['pants']['width'] // 2)
    pants_top = bottom_y - specs['pants']['height']
    pants_right = center_x + (specs['pants']['width'] // 2)
    pants_bottom = bottom_y
    
    character['parts']['pants'] = {
        'id': canvas.create_rectangle(
            pants_left, pants_top, pants_right, pants_bottom,
            specs['pants']['color']
        ),
        'relative_pos': {
            'left': pants_left - left_x,
            'top': pants_top - top_y
        }
    }
    
    # Create shirt
    shirt_left = center_x - (specs['shirt']['width'] // 2)
    shirt_top = pants_top - specs['shirt']['height']
    shirt_right = center_x + (specs['shirt']['width'] // 2)
    shirt_bottom = pants_top
    
    character['parts']['shirt'] = {
        'id': canvas.create_rectangle(
            shirt_left, shirt_top, shirt_right, shirt_bottom,
            specs['shirt']['color']
        ),
        'relative_pos': {
            'left': shirt_left - left_x,
            'top': shirt_top - top_y
        }
    }
    
    # Create head
    head_left = center_x - (specs['head']['size'] // 2)
    head_top = shirt_top - specs['head']['size']
    head_right = center_x + (specs['head']['size'] // 2)
    head_bottom = shirt_top
    
    character['parts']['head'] = {
        'id': canvas.create_oval(
            head_left, head_top, head_right, head_bottom,
            specs['head']['color']
        ),
        'relative_pos': {
            'left': head_left - left_x,
            'top': head_top - top_y
        }
    }
    # If it's the whompus, hide it initially
    if character_type == ['whompus' or 'whompus_intro']:
        for part in character['parts'].values():
            canvas.set_hidden(part['id'], True)
    if character_type == 'whompus_intro':
        for part in character['parts'].values():
            canvas.set_hidden(part['id'], False)
    return character

################################################################################################
################# Create main menu, and game over screen ######################################
################################################################################################
def create_main_menu() -> Tuple[int, int, int, int]:
    """Create the main menu with clickable options and return the button IDs"""
    # Clear the canvas
    canvas.clear()
    
    # Create a dark background for the game board area
    canvas.create_rectangle(
        0, 0, CANVAS_WIDTH, CANVAS_HEIGHT - 40,
        'black', 'black'
    )
    
    # Create title with a more dramatic style
    title_box = canvas.create_rectangle(
        40, 20, 360, 80,
        'black', 'red'
    )
    title_id = canvas.create_text(
        50, 20,
        text="WHOMPUS HUNT 2.0",
        font='Arial',
        font_size=30,
        color='red'
    )
    
    # Create subtitle
    subtitle_id = canvas.create_text(
        70, 60,
        text="A Dangerous Game of AI and Deception",
        font='Arial',
        font_size=14,
        color='white'
    )
    
    # Create menu buttons with hover effects
    button_width = 240
    button_height = 50
    button_spacing = 30
    start_y = 150
    
    # Play with intro button
    with_intro_box = canvas.create_rectangle(
        (CANVAS_WIDTH - button_width) // 2,
        start_y,
        (CANVAS_WIDTH + button_width) // 2,
        start_y + button_height,
        'black', 'red'
    )
    with_intro_text = canvas.create_text(
        ((CANVAS_WIDTH // 2)-(button_width/4)),
        start_y + button_height // 2,
        text="Play (With Intro)",
        font='Arial',
        font_size=16,
        color='white'
    )
    
    # Play without intro button
    skip_intro_box = canvas.create_rectangle(
        (CANVAS_WIDTH - button_width) // 2,
        start_y + button_height + button_spacing,
        (CANVAS_WIDTH + button_width) // 2,
        start_y + 2 * button_height + button_spacing,
        'black', 'red'
    )
    skip_intro_text = canvas.create_text(
        ((CANVAS_WIDTH // 2)-(button_width//4)), (start_y + button_height + button_spacing+(button_height//2)),
        text="Play (Skip Intro)",
        font='Arial',
        font_size=16,
        color='white'
    )
    
    return with_intro_box, skip_intro_box, with_intro_text, skip_intro_text

def show_main_menu() -> str:
    """Show the main menu and return the selected option"""
    # Create the menu
    with_intro_box, skip_intro_box, with_intro_text, skip_intro_text = create_main_menu()
    
    # Track button states for hover effects
    button_states = {
        with_intro_box: {'hover': False, 'text': with_intro_text},
        skip_intro_box: {'hover': False, 'text': skip_intro_text}
    }
    
    # Wait for click
    while True:
        # Get current mouse position
        mouse_x = canvas.get_mouse_x()
        mouse_y = canvas.get_mouse_y()
        
        # Check hover states for each button
        for box_id, state in button_states.items():
            # Get coordinates using coords() instead of get_bounds()
            coords = canvas.coords(box_id)
            left_x, top_y = coords[0], coords[1]
            right_x = left_x + canvas.get_object_width(box_id)
            bottom_y = top_y + canvas.get_object_height(box_id)
            
            is_hovering = (left_x <= mouse_x <= right_x and top_y <= mouse_y <= bottom_y)
            
            # Update hover state if changed
            if is_hovering != state['hover']:
                state['hover'] = is_hovering
                # Change button color on hover
                canvas.set_color(box_id, 'red' if is_hovering else 'black')
                canvas.set_color(state['text'], 'black' if is_hovering else 'white')
        
        # Check for clicks
        click = canvas.get_last_click()
        if click:
            # click is a list of coordinates [x, y]
            x, y = click[0], click[1]
            
            # Get coordinates for each button
            with_intro_coords = canvas.coords(with_intro_box)
            skip_intro_coords = canvas.coords(skip_intro_box)
            
            # Calculate button boundaries
            with_intro_left = with_intro_coords[0]
            with_intro_top = with_intro_coords[1]
            with_intro_right = with_intro_left + canvas.get_object_width(with_intro_box)
            with_intro_bottom = with_intro_top + canvas.get_object_height(with_intro_box)
            
            skip_intro_left = skip_intro_coords[0]
            skip_intro_top = skip_intro_coords[1]
            skip_intro_right = skip_intro_left + canvas.get_object_width(skip_intro_box)
            skip_intro_bottom = skip_intro_top + canvas.get_object_height(skip_intro_box)
            
            if (with_intro_left <= x <= with_intro_right and
                with_intro_top <= y <= with_intro_bottom):
                return 'with_intro'
            elif (skip_intro_left <= x <= skip_intro_right and
                  skip_intro_top <= y <= skip_intro_bottom):
                return 'skip_intro'
        
        time.sleep(0.1)

def show_game_over_screen(result: str) -> None:
    """Show the game over screen with appropriate message"""
    # Clear the canvas
    canvas.clear()
    
    # Create a dark background
    canvas.create_rectangle(
        0, 0, CANVAS_WIDTH, CANVAS_HEIGHT - 40,
        'black', 'black'
    )
    
    # Create game over box
    box = canvas.create_rectangle(
        40, 100, 360, 300,
        'black', 'red'
    )
    
    # Show appropriate message
    if result == 'trap':
        title = "YOU FELL INTO A TRAP!"
        message = "The darkness claims another victim..."
    else:  # whompus
        title = "THE WHOMPUS GOT YOU!"
        message = "Your code has been... optimized."
    
    # Create text elements
    canvas.create_text(
        50, 150,
        text=title,
        font='Arial',
        font_size=24,
        color='red'
    )
    
    canvas.create_text(
        50, 200,
        text=message,
        font='Arial',
        font_size=16,
        color='white'
    )
    
    canvas.create_text(
        50, 250,
        text="Click anywhere to return to menu",
        font='Arial',
        font_size=14,
        color='red'
    )
    
    # Wait for click using wait_for_click() instead of polling
    canvas.wait_for_click()
################################################################################################
################ Build a "lit" room when character is present ######################################
################################################################################################
def character_room_occupied(row, col):
    """Create a lit room effect when a character is present"""
    left_x = col * ROOM_SIZE
    top_y = row * ROOM_SIZE
    right_x = (col * ROOM_SIZE) + ROOM_SIZE
    bottom_y = (row * ROOM_SIZE) + ROOM_SIZE
    
    character_room_white = canvas.create_rectangle(
        left_x, top_y, right_x, bottom_y, 
        "white", "yellow"
    )
    character_room_light = canvas.create_oval(
        left_x, top_y, (left_x + 3), (top_y + 3), 
        "yellow", "red"
    ) 
    
    return {
        'character_room_white': character_room_white,
        'character_room_light': character_room_light
    }

################################################################################################
################ Build a dark room when character is NOT present ######################################
################################################################################################

def darken_room(row, col):
    """Darken a room when a character leaves it"""
    left_x = col * ROOM_SIZE
    top_y = row * ROOM_SIZE
    right_x = left_x + ROOM_SIZE
    bottom_y = top_y + ROOM_SIZE
    
    # Create a black rectangle to cover the room
    canvas.create_rectangle(
        left_x, top_y, right_x, bottom_y,
        'black', 'white'  # Black fill with white outline
    )

################################################################################################
############### Make lights on "Game board" for intro floor plan ######################################
################################################################################################
def make_the_board():
    """Create the initial game board with alternating colors"""
    num_rows = CANVAS_WIDTH // ROOM_SIZE
    num_cols = CANVAS_HEIGHT // ROOM_SIZE    

    for row in range(num_rows):    
        for col in range(num_cols):
            left_x = col * ROOM_SIZE
            top_y = row * ROOM_SIZE
            right_x = left_x + ROOM_SIZE
            bottom_y = top_y + ROOM_SIZE
                
            if (row + col) % 2 == 0:
                color = "white"
                outline = 'black'
            else: 
                color = "darkgrey"
                outline = 'black'
                
            room = canvas.create_rectangle(
                left_x, top_y, right_x, bottom_y, 
                color, outline
            )

################################################################################################
############### Make the "lights off game board" ######################################
################################################################################################
def dark_game_board():
    """Create the dark version of the game board"""
    num_rows = CANVAS_WIDTH // ROOM_SIZE
    num_cols = CANVAS_HEIGHT // ROOM_SIZE    

    for row in range(num_rows):    
        for col in range(num_cols):
            left_x = col * ROOM_SIZE
            top_y = row * ROOM_SIZE
            right_x = left_x + ROOM_SIZE
            bottom_y = top_y + ROOM_SIZE
                
            room = canvas.create_rectangle(
                left_x, top_y, right_x, bottom_y, 
                'black', 'white'
            )

################################################################################################
############### Introduction conversation ######################################
################################################################################################
def dialog_of_characters():
    """Create the initial dialog box and text elements"""
    box = canvas.create_rectangle(40, 80, 360, 320,
        'black', 'red'
    )
    title_of_text = canvas.create_text(50, 85, 
        text='W.H.O.M.P.U.S. 2.0',
        font='Arial', font_size=30, 
        color='red'
    )

    row_one_of_text = canvas.create_text(50, 140, 
        text='When you learned to code',
        font='Arial', font_size=17, 
        color='white'
    )

    row_two_of_text = canvas.create_text(50, 180, 
        text='with code in place online for free',
        font='Arial', font_size=17, 
        color='white'
    )

    row_three_of_text = canvas.create_text(50, 220, 
        text='you had NO clue it would end this way',
        font='Arial', font_size=17, 
        color='white'
    )

    row_four_of_text = canvas.create_text(50, 260, 
        text='',
        font='Arial', font_size=17, 
        color='white'
    )

    row_five_of_text = canvas.create_text(150, 300, 
        text='click to continue',
        font='Arial', font_size=10, 
        color='red'
    )

    return row_one_of_text, row_two_of_text, row_three_of_text, row_four_of_text

################################################################################################
############### Dialog animation sequence ######################################
################################################################################################
def dialog_intro_all(canvas, row_one_of_text, row_two_of_text, row_three_of_text, row_four_of_text, row_1, row_2, row_3, row_4):
    """Animate the dialog text sequence"""
    max_length = max(len(row_1), len(row_2), len(row_3), len(row_4))

    for i in range(max_length):
        if i < len(row_1):
            canvas.change_text(row_one_of_text, row_1[i])
        if i < len(row_2):
            canvas.change_text(row_two_of_text, row_2[i])
        if i < len(row_3):
            canvas.change_text(row_three_of_text, row_3[i])
        if i < len(row_4):
            canvas.change_text(row_four_of_text, row_4[i])

        canvas.wait_for_click()

################################################################################################
############## Dialog canvas and hazard icon animation ######################################
################################################################################################
def square_for_intro():
    """Create the dialog box for the introduction"""
    box = canvas.create_rectangle(40, 80, 360, 320,
        'black', 'red'
    )

def hazard_animation():
    """Create and animate the hazard warning icon"""
    # Hazard yellow triangle
    hazard = canvas.create_polygon(
        240, 300, 300, 300, 270, 250,
        color="yellow"
    )
    # Hazard exclamation point
    exclaim = canvas.create_text(
        265, 260, 
        text='!',
        font='Arial', 
        font_size=35, 
        color='red'
    )
    # Hazard blinking loop
    for _ in range(3):
        canvas.set_hidden(hazard, True)
        canvas.set_hidden(exclaim, True)
        time.sleep(0.5)
        canvas.set_hidden(hazard, False)
        canvas.set_hidden(exclaim, False)
        time.sleep(0.8)

    canvas.delete(hazard)
    canvas.delete(exclaim)

################################################################################################
############# Function used to start first part of intro animation ######################################
################################################################################################
def intro_dialog_animation():
    """Run the complete introduction animation sequence"""
    make_the_board()
    square_for_intro()
    dialog_of_characters()
    hazard_animation()
    canvas.wait_for_click()
    row_one_of_text, row_two_of_text, row_three_of_text, row_four_of_text = dialog_of_characters()
    dialog_intro_all(canvas, row_one_of_text, row_two_of_text, row_three_of_text, row_four_of_text, row_1, row_2, row_3, row_4)

################################################################################################
############# Function used to FINISH the intro animation ######################################
################################################################################################
def finish_the_intro():
    """Complete the introduction sequence and transition to game"""
    # Create black overlay
    rect = canvas.create_rectangle(0, 0, 400, 400, 'black')
    
    # Light up character rooms
    character_room_occupied(0, 9)
    character_room_occupied(9, 0)
    
    time.sleep(.5)
    
    # Recreate characters to ensure visibility
    create_character('player', 9, 0)
    create_character('whompus_intro', 0, 9)
    
    # Dialog sequence
    whompus_talk = canvas.create_text(
        40, 60, 
        text='MUST ELIMINATE NOT HOTDOG...!',
        font='Arial', 
        font_size=20, 
        color='red'
    )
    time.sleep(2)
    
    # Hide dialog
    is_hidden = True
    canvas.set_hidden(whompus_talk, is_hidden)
    
    player_talk = canvas.create_text(
        80, 320, 
        text='oh...no... this is not good...!',
        font='Arial', 
        font_size=20, 
        color='white'
    )
    time.sleep(3)
    canvas.set_hidden(player_talk, is_hidden)
    
    # AI introductions
    canvas.create_text(
        40, 100, 
        text='I can help you...-ALEX',
        font='Arial', 
        font_size=15, 
        color='yellow'
    )
    time.sleep(3)
    
    canvas.create_text(
        40, 120, 
        text='I am the one you can trust - ANDY',
        font='Arial', 
        font_size=15, 
        color='orange'
    )  
    time.sleep(3) 
    
    canvas.create_text(
        40, 140, 
        text='That one is lying - ALICE',
        font='Arial', 
        font_size=15, 
        color='red'
    )
    time.sleep(3)
    
    # Clear screen and start dark game
    canvas.clear()
    dark_game_board()
    
    return 'player', 'whompus'

################################################################################################
############# AI Interaction and Game Mechanics ######################################
################################################################################################
def get_player_question(ai_name: str, game_state: GameState, info_bar: InfoBar) -> Optional[str]:
    """Get the player's question for the AI with improved terminal interaction"""
    # Update info bar with AI interaction header
    info_bar.update(game_state, message=f"\n=== ASKING {ai_name} ===\n", is_ai_response=False)
    
    # Display context and instructions in terminal
    print("\nYou can ask about:")
    print("  - Nearby rooms and their contents")
    print("  - The Whompus's location")
    print("  - Trap doors in adjacent rooms")
    print("  - Game mechanics and rules")
    print("  - The AI's role and behavior")
    print("\nType 'exit' to return to the game menu")
    print("\n" + "-"*30)
    
    # Get the question with a clear prompt
    print(f"\nYour question for {ai_name}:")
    question = input("> ").strip()
    
    # Handle exit command
    if question.lower() in ['exit', 'quit', 'back']:
        return None
    
    # Show the question was received
    info_bar.update(game_state, message=f"Sending question to {ai_name}...", is_ai_response=False)
    time.sleep(0.5)  # Brief pause for visual feedback
    
    return question

def get_ai_response(ai_name: str, question: str, game_state: GameState, info_bar: InfoBar) -> str:
    """Get response from the specified AI with improved context"""
    try:
        # Reset any pending acknowledgments before starting
        info_bar.waiting_for_acknowledgment = False
        
        # Get adjacent room status for context
        row, col = game_state.player_position
        adjacent_rooms = []
        adjacent_traps = []
        for drow, dcol in DIRECTIONS.values():
            new_row, new_col = row + drow, col + dcol
            if 0 <= new_row < 10 and 0 <= new_col < 10:
                status = check_room_status((new_row, new_col), game_state)
                adjacent_rooms.append(f"({new_row},{new_col},{status})")
                if status == 'trap':
                    adjacent_traps.append(f"({new_row},{new_col})")
        
        # Rest of the function remains the same until the response handling...
        
        try:
            # Get response from AI
            response = call_gpt(prompt)
            
            # Ensure the response includes an actual answer
            if "trap" in question.lower() and not any(word in response.lower() for word in ["trap", "pit", "hole", "danger", "safe", "clear"]):
                # If the AI didn't address the trap question, append a clear answer
                if ai_role == 'truth':
                    if adjacent_traps:
                        response += f"\n\n*adjusts robes* I must be clear: there {'is' if len(adjacent_traps) == 1 else 'are'} trap{'s' if len(adjacent_traps) > 1 else ''} in room{'s' if len(adjacent_traps) > 1 else ''} {', '.join(adjacent_traps)}."
                    else:
                        response += "\n\n*adjusts robes* I must be clear: there are no traps in the rooms adjacent to you."
                elif ai_role == 'fifty':
                    if adjacent_traps:
                        response += f"\n\n*chuckles* The winds tell me there {'is' if len(adjacent_traps) == 1 else 'are'} trap{'s' if len(adjacent_traps) > 1 else ''} in room{'s' if len(adjacent_traps) > 1 else ''} {', '.join(adjacent_traps)}... or do they?"
                    else:
                        response += "\n\n*chuckles* The winds whisper of no traps nearby... but can you trust the wind?"
                else:  # fifty_lie or villain
                    if adjacent_traps:
                        response += f"\n\n*eyes gleam* I sense safety in room{'s' if len(adjacent_traps) > 1 else ''} {', '.join(adjacent_traps)}... or do I?"
                    else:
                        response += "\n\n*eyes gleam* I sense danger in the rooms around you... or do I?"
            
            # Format and display the response
            formatted_response = format_ai_response(ai_name, response)
            
            # Update info bar and wait for acknowledgment in a single operation
            info_bar.update(game_state, formatted_response, is_ai_response=True)
            info_bar.wait_for_acknowledgment()
            
            # Complete the action after acknowledgment
            game_state.complete_action()
            
            return response
            
        except Exception as e:
            # Handle GPT call failure with mock responses
            mock_responses = {
                'ALI': (
                    "*adjusts mysterious robes* The ancient stones speak clearly to me. " +
                    ("There " + ("is" if len(adjacent_traps) == 1 else "are") + " trap" + 
                     ("s" if len(adjacent_traps) > 1 else "") + " in room" + 
                     ("s" if len(adjacent_traps) > 1 else "") + " " + 
                     ", ".join(adjacent_traps) + "." if adjacent_traps else 
                     "There are no traps in the rooms adjacent to you.") +
                    " *gestures ominously* Tread carefully, for the dungeon hungers..."
                ),
                'AN': (
                    "*chuckles mysteriously* The winds of fate whisper to me... " +
                    ("They speak of trap" + ("s" if len(adjacent_traps) > 1 else "") + 
                     " in room" + ("s" if len(adjacent_traps) > 1 else "") + " " + 
                     ", ".join(adjacent_traps) + "." if adjacent_traps else 
                     "They speak of no traps nearby.") +
                    " *eyes gleam* But can you trust the wind?"
                ),
                'ALE': (
                    "*eyes gleam in the dim light* The shadows reveal to me... " +
                    ("Safety in room" + ("s" if len(adjacent_traps) > 1 else "") + " " + 
                     ", ".join(adjacent_traps) + "." if adjacent_traps else 
                     "Danger in the rooms around you.") +
                    " *gestures dramatically* But perhaps the shadows deceive even me..."
                )
            }
            response = mock_responses.get(ai_name, "*a mysterious voice echoes through the chambers* I sense a disturbance in the connection...")
            formatted_response = format_ai_response(ai_name, response)
            
            # Update info bar and wait for acknowledgment in a single operation
            info_bar.update(game_state, formatted_response, is_ai_response=True)
            info_bar.wait_for_acknowledgment()
            
            # Complete the action after acknowledgment
            game_state.complete_action()
            
            return response
            
    except Exception as e:
        # Handle any other errors
        error_msg = f"*a dark whisper echoes* Error: {str(e)}"
        info_bar.update(game_state, error_msg, is_ai_response=False)
        game_state.complete_action()
        return error_msg
################################################################################################
############# Whompus Movement and Game State ######################################
################################################################################################
def whompus_move(game_state: GameState, player_position: Tuple[int, int]) -> Tuple[int, int]:
    #Determine whompuss next move
    # Move categories
    if game_state.player_moves < 30:  # Category A
        if game_state.player_moves % 3 != 0:
            return game_state.whompus_position
    elif game_state.player_moves < 50:  # Category B
        if game_state.player_moves % 2 != 0:
            return game_state.whompus_position
    # Category C - always move
    
    # Get valid moves for whompus
    valid_moves = get_valid_moves(game_state.whompus_position)
    if not valid_moves:
        return game_state.whompus_position
    
    # Determine if whompus should chase player
    chase_chance = 0.25
    if game_state.player_moves >= 30:
        chase_chance = 0.5
    if game_state.player_moves >= 50:
        chase_chance = 1.0
    
    if random.random() < chase_chance:
        # Try to move towards player
        best_move = None
        min_distance = float('inf')
        for direction in valid_moves:
            drow, dcol = DIRECTIONS[direction]
            new_row = game_state.whompus_position[0] + drow
            new_col = game_state.whompus_position[1] + dcol
            distance = abs(new_row - player_position[0]) + abs(new_col - player_position[1])
            if distance < min_distance:
                min_distance = distance
                best_move = (new_row, new_col)
        return best_move if best_move else game_state.whompus_position
    
    # Random move
    direction = random.choice(valid_moves)
    drow, dcol = DIRECTIONS[direction]
    return (game_state.whompus_position[0] + drow, 
            game_state.whompus_position[1] + dcol)
################################################################################################
############# Checking the rooms next to player ######################################
################################################################################################
def check_room_status(position: Tuple[int, int], game_state: GameState) -> str:

    row, col = position
    if position in game_state.trap_doors:
        return 'trap'
    elif position == game_state.whompus_position:
        return 'whompus'
    else:
        return 'empty'
################################################################################################
############# Trap door visualization and location ######################################
################################################################################################
def visualize_trap_doors(game_state: GameState):
    for row, col in game_state.trap_doors:
        left_x = col * ROOM_SIZE + ROOM_SIZE//4
        top_y = row * ROOM_SIZE + ROOM_SIZE//4
        right_x = col * ROOM_SIZE + 3*ROOM_SIZE//4
        bottom_y = row * ROOM_SIZE + 3*ROOM_SIZE//4
        
        # Create a black circle for the trap
        canvas.create_oval(
            left_x, top_y, right_x, bottom_y,
            'black', 'black'  # Solid black circle
        )

def show_trap(row: int, col: int):
    left_x = col * ROOM_SIZE + ROOM_SIZE//4
    top_y = row * ROOM_SIZE + ROOM_SIZE//4
    right_x = col * ROOM_SIZE + 3*ROOM_SIZE//4
    bottom_y = row * ROOM_SIZE + 3*ROOM_SIZE//4
    
    # Create a black circle for the trap on top of the lit room
    canvas.create_oval(
        left_x, top_y, right_x, bottom_y,
        'black', 'black'  # Solid black circle
    )
################################################################################################
########### Player Movement and validation of moves ######################################
################################################################################################
def get_valid_moves(position: Tuple[int, int]) -> List[str]:
    row, col = position
    return [
        direction for direction, (drow, dcol) in DIRECTIONS.items()
        if 0 <= row + drow < 10 and 0 <= col + dcol < 10
    ]

def move_character(character: Dict, new_position: Tuple[int, int], game_state: GameState) -> Dict:
    
    # Get old and new positions
    old_row, old_col = character['position']
    new_row, new_col = new_position
    
    # Update room occupants
    if character['id'] in game_state.room_occupants[old_row][old_col]:
        game_state.room_occupants[old_row][old_col].remove(character['id'])
    if character['id'] not in game_state.room_occupants[new_row][new_col]:
        game_state.room_occupants[new_row][new_col].append(character['id'])
    
    # Update character's position
    character['position'] = new_position
    character['row'] = new_row
    character['col'] = new_col
    
    # Calculate pixel positions for the new location
    new_left_x = new_col * ROOM_SIZE
    new_top_y = new_row * ROOM_SIZE
    center_x = new_left_x + (ROOM_SIZE // 2)
    bottom_y = new_top_y + ROOM_SIZE
    
    # Delete old character parts
    for part in character['parts'].values():
        canvas.delete(part['id'])
    
    # Handle room lighting based on character type
    if character['type'] == 'player':
        # Darken old room and light up new room
        darken_room(old_row, old_col)
        character_room_occupied(new_row, new_col)
    
    # Create new character parts
    specs = CHARACTER_PARTS[character['type']]
    
    # Create pants
    pants_left = center_x - (specs['pants']['width'] // 2)
    pants_top = bottom_y - specs['pants']['height']
    pants_right = center_x + (specs['pants']['width'] // 2)
    pants_bottom = bottom_y
    
    character['parts']['pants'] = {
        'id': canvas.create_rectangle(
            pants_left, pants_top, pants_right, pants_bottom,
            specs['pants']['color']
        ),
        'relative_pos': {
            'left': pants_left - new_left_x,
            'top': pants_top - new_top_y
        }
    }
    
    # Create shirt
    shirt_left = center_x - (specs['shirt']['width'] // 2)
    shirt_top = pants_top - specs['shirt']['height']
    shirt_right = center_x + (specs['shirt']['width'] // 2)
    shirt_bottom = pants_top
    
    character['parts']['shirt'] = {
        'id': canvas.create_rectangle(
            shirt_left, shirt_top, shirt_right, shirt_bottom,
            specs['shirt']['color']
        ),
        'relative_pos': {
            'left': shirt_left - new_left_x,
            'top': shirt_top - new_top_y
        }
    }
    
    # Create head
    head_left = center_x - (specs['head']['size'] // 2)
    head_top = shirt_top - specs['head']['size']
    head_right = center_x + (specs['head']['size'] // 2)
    head_bottom = shirt_top
    
    character['parts']['head'] = {
        'id': canvas.create_oval(
            head_left, head_top, head_right, head_bottom,
            specs['head']['color']
        ),
        'relative_pos': {
            'left': head_left - new_left_x,
            'top': head_top - new_top_y
        }
    }
    
    # Handle whompus visibility
    if character['type'] == 'whompus':
        for part in character['parts'].values():
            canvas.set_hidden(part['id'], True)
    
    return character

################################################################################################
########### prompts for the ai in the game ######################################
################################################################################################

def format_ai_response(ai_name: str, response: str) -> str:
    """Format an AI response message consistently"""
    return f"=== {ai_name}'s Response ===\n{response}"

################################################################################################
########### Player asks for the game rules ######################################
################################################################################################

def show_game_rules(canvas: Canvas, game_state: GameState):
    """Display the game rules with move count and return option"""

    print(f"        GAME RULES (Moves: {game_state.player_moves})")
    
    rules = """MOVEMENT:
- Use arrow keys to move between rooms
- The Whompus moves faster as you make more moves
- After 30 moves: Whompus moves every other turn
- After 50 moves: Whompus moves every turn
- Each action (move, ask AI, view rules) counts as a move

AI ASSISTANTS:
- Three AIs are available: ALI, AN, and ALE
- One always tells the truth
- One always lies
- One is 50/50 (randomly tells truth or lies)
- AIs can only see adjacent rooms
- They can control trap doors
- Selecting an AI and asking counts as a move

WINNING:
- Find the golden GPU to win
- Avoid the Whompus and trap doors
- Use the AIs wisely to gather information

Press 'B' to return to the game..."""
    
    print(rules)
    
    # Wait for 'B' key to return to game
    while True:
        key = canvas.get_last_key_press()
        if key in ['B', 'b']:
            break
        time.sleep(0.1)
#######################################################################################
######################## SHOW GAME MENU#######################################################################################
#######################################################################################
def show_game_menu(game_state: GameState):
    """Display the game menu with move count"""
    print(f"\n=== WHOMPUS 2.0 (Moves: {game_state.player_moves}) ===")
    print("\nMOVE (M) - Use arrow keys to navigate")
    print("ASK (A)  - Question an AI about nearby rooms")
    print("INFO (I) - View game rules")
    print("\nEnter your choice (M/A/I): ", end="")     
################################################################################################
########## Show ai options to the player ######################################
################################################################################################
def show_ai_options(game_state: GameState):
    """Display AI selection menu with move count"""
    print(f"\n=== SELECT AN AI (Moves: {game_state.player_moves}) ===")
    print("\n1. ALI  - One of three AIs that may help or mislead")
    print("2. AN   - Another AI that may tell truth or lies")
    print("3. ALE  - The third AI, choose questions carefully")
    print("4. Back - Return to main menu (B)")
    print("\nEnter your choice (1-4 or B): ", end="")
################################################################################################
########## Turn player into whompus ######################################
################################################################################################

def transform_player_to_whompus(player: Dict):
    # Get the current colors
    current_colors = {
        'pants': canvas.get_fill_color(player['parts']['pants']['id']),
        'shirt': canvas.get_fill_color(player['parts']['shirt']['id']),
        'head': canvas.get_fill_color(player['parts']['head']['id'])
    }
    
    # Number of steps for the transformation
    steps = 10
    for step in range(steps + 1):
        # Calculate new colors (gradually change to black)
        for part_name in ['pants', 'shirt', 'head']:
            # Create a gradient from current color to black
            current_color = current_colors[part_name]
            # For simplicity, we'll just make it darker each step
            canvas.set_fill_color(player['parts'][part_name]['id'], 'black')
        
        # Wait a bit between each step
        time.sleep(0.1)    
################################################################################################
########## Play a single round of the game ######################################
################################################################################################

def play_round(game_state: GameState, player: Dict, whompus: Dict, info_bar: InfoBar) -> str:
    """Play a single round of the game with improved move tracking"""
    info_bar.waiting_for_acknowledgment = False
    show_game_menu(game_state)
    
    key = None
    while True:
        key = canvas.get_last_key_press()
        if key in ['M', 'm', 'A', 'a', 'I', 'i']:
            break
        time.sleep(0.1)
    
    if key in ['I', 'i']:
        game_state.increment_moves('view_rules')
        show_game_rules(game_state)
        game_state.complete_action()
        return 'continue'
    
    elif key in ['A', 'a']:
        show_ai_options(game_state)
        
        selected_ai = None
        while True:
            key = canvas.get_last_key_press()
            if key in ['1', '2', '3', '4', 'B', 'b']:
                if key in ['1', '2', '3']:
                    selected_ai = {'1': 'ALI', '2': 'AN', '3': 'ALE'}[key]
                break
            time.sleep(0.1)
        
        if not selected_ai:
            show_game_menu(game_state)
            return 'continue'
        
        game_state.increment_moves('select_ai')
        question = get_player_question(selected_ai, game_state, info_bar)
        
        if question is None:
            game_state.complete_action()
            show_game_menu(game_state)
            return 'continue'
        
        try:
            response = get_ai_response(selected_ai, question, game_state, info_bar)
            while canvas.get_last_key_press():
                time.sleep(0.1)
            show_game_menu(game_state)
        except Exception as e:
            error_msg = f"*a dark whisper echoes* Error: {str(e)}"
            info_bar.update(game_state, error_msg, is_ai_response=False)
            game_state.complete_action()
            show_game_menu(game_state)
        
        return 'continue'
    
    elif key in ['M', 'm']:
        game_state.increment_moves('move')
        valid_moves = get_valid_moves(game_state.player_position)
        print("\n=== Movement ===")
        print(f"Valid moves: {', '.join(valid_moves)}")
        print("Use arrow keys to move")
        
        key_map = {
            'ArrowUp': 'UP',
            'ArrowDown': 'DOWN',
            'ArrowLeft': 'LEFT',
            'ArrowRight': 'RIGHT'
        }
        
        direction = None
        while True:
            key = canvas.get_last_key_press()
            if key in key_map and key_map[key] in valid_moves:
                direction = key_map[key]
                break
            time.sleep(0.1)
        
        drow, dcol = DIRECTIONS[direction]
        new_position = (game_state.player_position[0] + drow, 
                       game_state.player_position[1] + dcol)
        
        move_character(player, new_position, game_state)
        game_state.player_position = new_position
        
        room_status = check_room_status(new_position, game_state)
        if room_status == 'trap':
            show_trap(new_position[0], new_position[1])
            print("\n=== Game Over ===")
            print("You fell into a trap!")
            game_state.game_over = True
            game_state.complete_action()
            return 'trap'
        elif room_status == 'whompus':
            print("\n=== Game Over ===")
            print("The Whompus caught you!")
            game_state.game_over = True
            game_state.complete_action()
            return 'whompus'
        
        new_whompus_position = whompus_move(game_state, game_state.player_position)
        if new_whompus_position != game_state.whompus_position:
            move_character(whompus, new_whompus_position, game_state)
            game_state.whompus_position = new_whompus_position
            game_state.whompus_moves += 1
            
            if new_whompus_position == game_state.player_position:
                clear_terminal()
                print("\n=== Game Over ===")
                print("The Whompus caught you!")
                game_state.game_over = True
                game_state.complete_action()
                return 'whompus'
        
        game_state.complete_action()
        show_game_menu(game_state)
        return 'continue'
    
    show_game_menu(game_state)
    return 'continue'
################################################################################################
########## MAIN GAME LOOP ######################################
################################################################################################
def main():
    """Main game loop with menu system"""
    while True:
        # Show main menu and get selection
        choice = show_main_menu()
        
        # Initialize game state
        game_state = GameState()
        game_state.initialize_trap_doors()
        game_state.assign_ai_roles()
        
        # Create the game board
        make_the_board()
        
        # Create info bar
        info_bar = InfoBar(canvas)
        
        # Show intro if selected
        if choice == 'with_intro':
            intro_dialog_animation()
            player, whompus = finish_the_intro()
        else:
            # Skip intro, create characters directly
            player = create_character('player', 9, 0)
            whompus = create_character('whompus', 0, 9)
            dark_game_board()
        
        # Ensure player's room is lit and player is visible
        character_room_occupied(9, 0)  # Light up player's starting room
        player = create_character('player', 9, 0)  # Recreate player to ensure visibility
        
        # Ensure Whompus is created and hidden
        whompus = create_character('whompus', 0, 9)
        
        # Visualize trap doors
        visualize_trap_doors(game_state)
        
        # Main game loop
        game_active = True
        while game_active and not game_state.game_over:
            # Update info bar at the start of each round
            info_bar.update(game_state)
            
            result = play_round(game_state, player, whompus, info_bar)
            
            if result in ['trap', 'whompus']:
                # Show game over screen
                show_game_over_screen(result)
                # Set game_active to False to exit the game loop
                game_active = False
        
        # Clear any pending key presses
        while canvas.get_last_key_press():
            time.sleep(0.1)
        
        # Clear the canvas before returning to main menu
        canvas.clear()
        
        # If game is over, continue to next iteration of outer loop (show main menu)
        if not game_active:
            continue

################################################################################################
########## Game Entry Point ######################################
################################################################################################

if __name__ == '__main__':
    main()
