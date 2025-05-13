def main():
#Select the number of stones we will begin the game with
    stones = 20
#Establish player name as 1 to alternate players
    player = 1
#while loop so the game will continue until condition of 0 stones met
  
    while (stones > 0):
      
#tell the players how many stones are left and then ask how many stones they want to take if/else player 1/2
      
        print(f"There are {stones} stones left.")
        if player == 1:
            take = int(input("Player 1 would you like to remove 1 or 2 stones? "))
        else:
            take = int(input("Player 2 would you like to remove 1 or 2 stones? "))
          
#Conditional for player asking for amount of stones greater than 2 or less than 1
      
        if take < 1 or take > 2:
            take = int(input("Please enter 1 or 2: "))
          
#extra space for pretty formatting
        print()
      
#need to reduce number of stones by take amount and then substitute for new number of stones
        stones -= take  

#change the "player" number from 1 to 2 or from 2 to 1
        player = 2 if player == 1 else 1
#print winner once while loop is over
    print(f"Player {player} wins!")

if __name__ == '__main__':
    main()
