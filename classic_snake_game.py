from graphics import Canvas
import time
import random

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400
TITLE_HEIGHT = 25
SNAKE_SIZE = 20
WALL_THICKNESS = 5
MOVEMENT_SPEED = 12

def main():
    global SNAKE_SPEED
    global TIME_SLEEP
    global canvas

    SNAKE_SPEED = 2
    TIME_SLEEP = 0.15
    lives = 3
    segments_since_last_level = 0

    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)

    create_walls()

    snake_x = CANVAS_WIDTH / 2
    snake_y = CANVAS_HEIGHT / 2
    snake_segments = [
        canvas.create_rectangle(snake_x, snake_y, snake_x + SNAKE_SIZE, snake_y + SNAKE_SIZE, 'green')
    ]

    dx = MOVEMENT_SPEED
    dy = 0

    place_food()

    info_text = canvas.create_text(10, 10, text='')

    while lives > 0:
        key = canvas.get_last_key_press()
        if key == 'ArrowUp':
            dx, dy = 0, -MOVEMENT_SPEED
        elif key == 'ArrowDown':
            dx, dy = 0, MOVEMENT_SPEED
        elif key == 'ArrowLeft':
            dx, dy = -MOVEMENT_SPEED, 0
        elif key == 'ArrowRight':
            dx, dy = MOVEMENT_SPEED, 0

        for i in range(len(snake_segments) - 1, 0, -1):
            segment_coords = canvas.coords(snake_segments[i - 1])
            x1, y1 = segment_coords[0], segment_coords[1]
            canvas.moveto(snake_segments[i], x1, y1)

        canvas.move(snake_segments[0], dx, dy)

        snake_head_coords = canvas.coords(snake_segments[0])
        snake_x1, snake_y1 = snake_head_coords[0], snake_head_coords[1]
        snake_x2 = snake_x1 + SNAKE_SIZE
        snake_y2 = snake_y1 + SNAKE_SIZE

        if (snake_x1 < food_x + SNAKE_SIZE and snake_x2 > food_x and
            snake_y1 < food_y + SNAKE_SIZE and snake_y2 > food_y):
            
            if len(snake_segments) > 1:
                canvas.set_color(snake_segments[-1], 'green')

            tail_coords = canvas.coords(snake_segments[-1])
            tail_x, tail_y = tail_coords[0], tail_coords[1]
            new_segment = canvas.create_rectangle(tail_x, tail_y, tail_x + SNAKE_SIZE, tail_y + SNAKE_SIZE, 'green')
            snake_segments.append(new_segment)

            canvas.set_color(new_segment, 'yellowgreen')

            # Recreate food
            place_food()

            # Increase the segment counter
            segments_since_last_level += 1

            # Increase speed (level) every fifth segment added
            if segments_since_last_level == 5:
                SNAKE_SPEED += 1
                segments_since_last_level = 0  # Reset the counter

            TIME_SLEEP = max(0.001, 0.1 - SNAKE_SPEED * 0.001)

        if check_collision_with_wall(snake_x1, snake_y1):
            lives -= 1
            #print("Lives:", lives)
            if lives > 0:
                pause_and_reposition_snake(canvas, snake_segments)
            else:
                #print("Game Over!")
                canvas.change_text(info_text, "Game Over!")
                break

        update_game_info(canvas, info_text, lives, SNAKE_SPEED, len(snake_segments))
        
        time.sleep(TIME_SLEEP)

def place_food():
    global food_x, food_y, food

    food_x = random.randint(WALL_THICKNESS + 5, (CANVAS_WIDTH - SNAKE_SIZE - WALL_THICKNESS - 5) // SNAKE_SIZE) * SNAKE_SIZE
    food_y = random.randint((TITLE_HEIGHT + WALL_THICKNESS + 5) // SNAKE_SIZE, (CANVAS_HEIGHT - SNAKE_SIZE - WALL_THICKNESS - 5) // SNAKE_SIZE) * SNAKE_SIZE

    try:
        # Try to move existing food        
        canvas.moveto(food, food_x, food_y)
    except NameError:
        # If 'food' is not defined, create it
        food = canvas.create_rectangle(food_x, food_y, food_x + SNAKE_SIZE, food_y + SNAKE_SIZE, 'red')

def create_walls():
    top_wall = canvas.create_rectangle(0, TITLE_HEIGHT, CANVAS_WIDTH, TITLE_HEIGHT + WALL_THICKNESS, 'black')
    bottom_wall = canvas.create_rectangle(0, CANVAS_HEIGHT - WALL_THICKNESS, CANVAS_WIDTH, CANVAS_HEIGHT, 'black')
    left_wall = canvas.create_rectangle(0, TITLE_HEIGHT, WALL_THICKNESS, CANVAS_HEIGHT, 'black')
    right_wall = canvas.create_rectangle(CANVAS_WIDTH - WALL_THICKNESS, TITLE_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT, 'black')

def check_collision_with_wall(snake_x, snake_y):
    return (snake_x < WALL_THICKNESS or snake_x >= CANVAS_WIDTH - WALL_THICKNESS or 
            snake_y < 20 + WALL_THICKNESS or snake_y >= CANVAS_HEIGHT - WALL_THICKNESS)

def pause_and_reposition_snake(canvas, snake_segments):
    time.sleep(2)
    new_x = random.randint(WALL_THICKNESS, (CANVAS_WIDTH - SNAKE_SIZE - WALL_THICKNESS) // SNAKE_SIZE) * SNAKE_SIZE
    new_y = random.randint((20 + WALL_THICKNESS) // SNAKE_SIZE, (CANVAS_HEIGHT - SNAKE_SIZE - WALL_THICKNESS) // SNAKE_SIZE) * SNAKE_SIZE
    canvas.moveto(snake_segments[0], new_x, new_y)

    for segment in snake_segments[1:]:
        canvas.moveto(segment, new_x, new_y)

def update_game_info(canvas, info_text, lives, level, length):
    game_info = f"CiP_SNAKE  Lives: {lives}  Level: {level}  Length: {length}"
    canvas.change_text(info_text, game_info)

if __name__ == '__main__':
    main()
