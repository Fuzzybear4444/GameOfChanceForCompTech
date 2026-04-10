class EconomyManager:
    def __init__(self, starting_balance):
        self.balance = starting_balance
       

    def add_funds(self, amount):
        self.balance += amount

    def spend_funds(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Purchase successful! Remaining balance: {self.balance}")
            
            return True  # Purchase successful
        print("Not enough funds to complete the purchase.")
        return False     # Not enough money
    def get_balance(self):
        return self.balance
    
