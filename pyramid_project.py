## The assignment here was to build a program that could make a pyramid with bricks
## the code was suppose to work with "almost" all dimensions of the initial bricks
## we started with canvas of 600x300 and bricks that were 30x12 with 14 being in the initial base
## I wanted to take it a step further and give the user a chance to pick any brick size structure
## and see if it still made a pyramid. I have been thinking about the final project I will make
## for code in place and I am thinking about making a checkers game against a computer oponent. 
## I have been thinking about how I would input ML into the back end of it and allow every 
## game that it plays be a round of learning. But I am unsure if that is the best way to go this
## early in my journy. Anyway enjoy

from graphics import Canvas
import random
CANVAS_WIDTH = 600      # Width of drawing canvas in pixels
CANVAS_HEIGHT = 300     # Height of drawing canvas in pixels

def main():

    BRICK_WIDTH	= int(input("How wide do you want the blocks from 10 to 50? "))        # refered to as b.w. the width of each brick in pixels
    BRICK_HEIGHT = int(input("How tall do you want the blocks from 1 to 50? "))       # refered to as b.h. the height of each brick in pixels
    BRICKS_IN_BASE = int(input("How many blocks do you want in the base from 1 to 100? "))   # refered to as b.b. the number of bricks in the base

  ## Based on the user input we will calculate the starting positions for the first block which
  ## will be the anchor for the rest of our build

    Q = CANVAS_WIDTH-(BRICK_WIDTH*BRICKS_IN_BASE)
    stl = ((Q)/2)+(BRICK_WIDTH/2)           #Starting position for block 1
    sbl = CANVAS_HEIGHT     #Starting position for bl block 1
    sbr = ((Q)/2)+BRICK_WIDTH+(BRICK_WIDTH/2)    #starting position for br block 1
    str = (CANVAS_HEIGHT - BRICK_HEIGHT)    #starting position block 1 tr


    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    # setting the starting values equal to a new value so that I can have a running value but keep the starting values
    # the same for other iterations of the pyramid

    tl = stl        #tl = top left
    bl = sbl        #bl = bottom left 
    br = sbr        #br=bottom right 
    tr = str        #tr = top right

    x = BRICKS_IN_BASE
    # making th pyramid based on the number of bricks in the base
    for n in range (BRICKS_IN_BASE):
        for i in range (x-1):
          
          #Make a single brick
          
            canvas.create_rectangle(
            tl, bl, br, tr, 
            "red", "blue",)

        # Move the next brick over one brick width along the row
            tl= tl + BRICK_WIDTH
            br = br + BRICK_WIDTH
            if x/2 == float:
                color = "red" 
            else:
                color = "blue"
        #to make a pyramid instead of trapazoid, when the row is done reduce x by 1 
        x = x-1

#Below are transition values  
        tl = (stl) + ((n+1) * (BRICK_WIDTH/2))
        bl = sbl-((n+1) * BRICK_HEIGHT)
        br = sbr + ((n+1) * (BRICK_WIDTH/2))
        tr = (str) - ((n+1) * BRICK_HEIGHT)
# start all values from original positions ("stl, sbl, sbr, str")
# add n+1 multiplied (to move up and over)
# for horizontal position (TL/BR) one half brick height (if we move over full brick it wouldnt work)
# for vertical position (BL/TR) its just brick height

if __name__ == '__main__':
    main()
