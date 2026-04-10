class loanShark:
    def __init__(self):
        self.kneeCaps = 2  # Each player starts with 2 knee caps

    def KneeCapDestruction(self):
        if self.kneeCaps > 1:
            self.kneeCaps -= 1  # Knee cap destroyed
            print("You've been targeted by the henchman named 'The Knee Capper'! You lose one knee cap. and next time, you might not be so lucky...")
        if self.kneeCaps < 2:
            self.kneeCaps -= 1  # Knee cap destroyed
            print("Both of your knee caps have been destroyed! You can no longer walk, and now you're dragged to the dungeon to be dealt with by ISAAC!")