"""
This is the Backend for our Virtual Pet. It Creates a Pet that has a Name, a Customizable Pet Type, Emotions, and more.
"""
from flask import Flask, render_template, request, redirect, url_for, session
import random
app = Flask(__name__)
app.secret_key = "UFiishFp2WT3UBVMDkzbgIm1gElF"
SHOP = {
    "Food": {"cost": 4, "value": 25},
    "Water": {"cost": 1, "value": 15},
    "Toy": {"cost": 10},
    "Rent": {"cost": 66}
}
class Pet:
    def __init__(self, name, pet_type): #Makes a New Pet
        self.name = name
        self.type = pet_type
        self.hunger = 50
        self.thirst = 50
        self.happiness = 50
        self.energy = 50
        self.age = 0
        self.alive = True
    def feed(self):
        self.hunger = max(0, self.hunger - 20)
        self.happiness = min(100, self.happiness + 5)
    def drink(self):
        self.thirst = max(0, self.thirst - 15)
    def play(self):
        if self.energy >= 10:
            self.happiness += 15
            self.energy -= 10
    def sleep(self):
        self.energy = min(100, self.energy + 30)
    def pass_time(self): #Advances Time and Does Checks
        self.hunger += 2
        self.thirst += 2
        self.energy -= 3
        self.happiness -= 1
        self.age += 1
        if self.hunger >= 100 or self.thirst >= 100 or self.happiness <= 0 or self.energy <= 0:
            self.alive = False
    def get_state(self): #Looks at Emotions for Sprite
        if self.alive == False:
            return "dead"
        if self.hunger > 70 or self.thirst > 70:
            return "hungry"
        if self.energy < 30:
            return "tired"
        if self.happiness < 40:
            return "sad"
        return "happy"
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        pet_type = request.form["type"]
        pet = Pet(name, pet_type)
        session["wallet"] = 100
        session["inventory"] = {
            "Food": 2,
            "Water": 0,
            "Toy": 0,
            "Rent": 1
        }
        session["pet"] = vars(pet)
        return redirect(url_for("game"))
    return render_template("index.html")
@app.route("/game", methods=["GET", "POST"])
def game():
    if "pet" not in session:
        return redirect(url_for("index"))
    pet_data = session["pet"]
    pet = Pet(pet_data["name"], pet_data["type"])
    pet.__dict__.update(pet_data)
    inventory = session["inventory"]
    #The Following if Statement and Everything Inside of it Does a Function Based on What Type of Action is Preformed.
    if request.method == "POST": 
        action = request.form["action"]
        if action == "feed":
            if inventory["Food"] > 0:
                pet.feed()
                inventory["Food"] -= 1
        elif action == "drink":
            if inventory["Water"] > 0:
                pet.drink()
                inventory["Water"] -= 1
        elif action == "play":
            if inventory["Toy"] > 0:
                pet.play()
        elif action == "sleep":
            pet.sleep()
    pet.pass_time()
    #Economic Functions
    inventory["Rent"] -= 1
    wallet = session["wallet"]
    totalCost = 0
    wallet += 77 #Average Daily Pay for Mcdonalds Worker
    randomExpense = random.randint(0, 15)
    wallet -= randomExpense #Adds a Kind of Randomness Similarly to Life
    if inventory["Rent"] < 1 and wallet > 66:
        inventory["Rent"] += 1
        totalCost += 66
        wallet -= 66
    elif inventory["Rent"] < 1 and wallet < 66:
        pet.alive = False
    if wallet < 0:
        wallet = 0
        pet.happiness -= 10  # being broke hurts morale
    session["wallet"] = wallet
    session["inventory"] = inventory
    session["pet"] = vars(pet)
    image = f"images/{pet.type}/{pet.get_state()}.png"
    if pet.alive == False:
        del session["pet"]
    return render_template("game.html", pet=pet, image=image)
@app.route("/shop", methods=["GET", "POST"])
def shop():
    if "pet" not in session:
        return redirect(url_for("index"))
    wallet = session["wallet"]
    inventory = session["inventory"]
    if request.method == "POST":
        item = request.form["item"]
        if wallet >= SHOP[item]["cost"]:
            wallet -= SHOP[item]["cost"]
            totalCost += SHOP[item]["cost"]
            inventory[item] += 1
        session["wallet"] = wallet
        session["inventory"] = inventory
        session["totalCost"] = totalCost
    return render_template("shop.html", shop=SHOP, wallet=wallet, inventory=inventory)
if __name__ == "__main__":
    app.run(debug=True)
