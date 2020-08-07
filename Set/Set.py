from tkinter import Tk, LabelFrame, Frame, Label, Button, PhotoImage, NORMAL, DISABLED
from PIL import ImageTk
import datetime
import SolitaireMode as solit
import PuzzleMode as puz

class Card:
	def __init__(self, number, color, shading, shape):
		self.number = number
		self.color = color
		self.shading = shading
		self.shape = shape


class Spot:
	def __init__(self, row, col, card, button):
		self.row = row
		self.col = col
		self.card = card
		self.button = button


class Set:
	def __init__(self, parent):
		self.parent	= parent
		parent.title("Set")
		parent.iconbitmap("assets/cardsIcon.ico")
		#parent.config(bg="#384d9c")

		################### Instance Variables ###################
		self.numbers = {1: "one", 2: "two", 3: "three"}
		self.colors = {"r": "red", "g": "green", "p": "purple"}
		self.shadings = {"e": "non", "h": "half", "f": "fully"}
		self.shapes = {"S": "squiggle", "D": "diamond", "O": "oval"}
		self.deck = [Card(w,x,y,z) for w in self.numbers for x in self.colors for y in self.shadings for z in self.shapes]
		# field is defined at the bottom since it requires the tk frame it's in
		self.helds = set()
		self.justDealt = False
		self.solutions = []
		self.puzField = []
		self.puzSols = []
		self.score = 0
		self.setsOnBoard = 0
		self.gameState = 0 #0 is no game currently being played, 1 is solitaire, 2 is puzzle
		self.startTime = 0
		self.imgDict = {str(w) + x + y + z: PhotoImage(file="assets/" + str(w) + x + y + z + ".png") for w in self.numbers for x in self.colors for y in self.shadings for z in self.shapes}
		self.empty = PhotoImage(file="assets/empty.png")


		########################## GUI ##########################
		self.gameFrame = Frame(parent)
		self.fieldFrame = LabelFrame(self.gameFrame, text="")
		# the foundSets LabelFrame for puzzle mode will also go here

		self.lowerFrame = Frame(parent)
		self.foundSets = LabelFrame(self.lowerFrame, text="Sets Found")
		self.messageFrame = Frame(self.lowerFrame)
		self.message = Label(self.messageFrame, text="")
		self.msgUpdate = self.messageFrame.after(1, self.resetMessage, "")
		self.scoreboard = Label(self.lowerFrame, text="")
		self.deckStatus = Label(self.lowerFrame, text= "")
		self.solsButton = Button(self.lowerFrame, text="Show current solutions.", command=self.showSolutions)
		self.field = [[Spot(i, j, None, Button(self.fieldFrame, image=self.empty, bg="white", command=lambda i=i, j=j: self.bClick(i, j))) for j in range(7)] for i in range(3)]
		#This is the game board, 21 spots max. A set is unavoidable with 20 spots. It is redefined in the startSolit method.
		#For puzzle mode the field will have only 4 columns and a seperate widget showing the found sets will be gridded into the fieldFrame ___TODO____

		self.solitButton = Button(self.lowerFrame, text="Start/Restart a Solitaire Game", command=lambda: solit.start(self))
		self.puzzleButton = Button(self.lowerFrame, text="Start/Restart a Puzzle Game", command=lambda: puz.start(self))

		self.gameFrame.pack()
		self.fieldFrame.grid(row=0, column=0, padx=40)#.grid(row=0, column=0)
		for y in range(3): #grid 12 of the 21 possible field buttons, additional buttons will get gridded in only if they have a card
			for x in range(4):
				self.field[y][x].button.grid(row=y, column=x)

		self.lowerFrame.pack()
		self.messageFrame.pack()
		self.message.pack()
		self.scoreboard.pack()
		self.deckStatus.pack()
		self.solsButton.pack()
		self.solitButton.pack()
		self.puzzleButton.pack(pady=(0,40))


	######################## METHODS ########################
	def gameOver(self):
		timeDif = datetime.datetime.now()-self.startTime # datetime timedelta object
		finTime = "Finished in {} minute{}, {}.{} second{}.".format(
			timeDif.seconds//60,
			"s" if timeDif.seconds//60 != 1 else "",
			timeDif.seconds%60,
			str(timeDif)[8:11], #this truncates to milliseconds, doesn't round, shouldn't ever really be an issue
			"s" if timeDif.seconds> 0 else ""
		)
		for x in self.field:
			for y in x:
				y.button.config(state = DISABLED)
		if self.gameState == 1:
			self.message.config(text = "No sets and deck is empty, game over! " + finTime)
		else:
			self.message.config(text = "All sets found, game over! " + finTime)
		self.gameState = 0


	def start_shared(self):
		self.deck = [Card(w,x,y,z) for w in self.numbers for x in self.colors for y in self.shadings for z in self.shapes]
		self.helds = set()
		self.score = 0

		if self.buttonsInField() != 12:
			for button in self.fieldFrame.winfo_children(): 
				button.grid_forget() #ungrid the buttons in the field
			for x in range(3): #grid 12 of the 21 possible field buttons, additional buttons will get gridded in only if they have a card
				for y in range(4):
					self.field[x][y].button.grid(row=x, column=y)
		for row in self.field:
			for spot in row:
				spot.card = None
				spot.button.config(state=NORMAL)
		self.startTime = datetime.datetime.now()


	def sets_finder(self, cardsList):
		self.solutions=[]
		self.setsOnBoard = 99
		sets = []

		for i in cardsList:
			for j in cardsList:
				if j != i:
					for k in cardsList:
						if k != j and k != i and {i,j,k} not in sets and self.is_set([i,j,k]):
							sets.append({i,j,k})
							self.solutions.append({i,j,k})
		if self.gameState == 1:
			self.setsOnBoard = len(sets)
			solit.sets_finder_handler(self,self.setsOnBoard)
		if self.gameState == 2:
			return sets


	def is_set(self, givenCards, extraInfo="no"):
		"""takes a set of exactly 3 card objects, extraInfo if called from having full helds in checkSet()), not if called from setsFinder()"""
		attrSwitcher = {
			"number": {x.number for x in givenCards},
			"color": {x.color for x in givenCards},
			"shading": {x.shading for x in givenCards},
			"shape": {x.shape for x in givenCards}
		}

		
		if extraInfo == "yes":
			for attribute in attrSwitcher:
				if len(attrSwitcher.get(attribute)) == 2:
					falsRay = [False, "two of", "one of", attribute]

					notSetAtts = [eval("self." + attribute + "s.get(card." + attribute + ")", {"self": self, "card": card}) for card in givenCards]
					#the above is hacky but the easiest way to reconcile with the dictionaries
					print(notSetAtts)
					for x in notSetAtts:
						if notSetAtts.count(x) == 2 and x not in falsRay:
							falsRay[1] = str(x)
						if notSetAtts.count(x) == 1:
							falsRay[2] = str(x)
					print(falsRay)
					return falsRay #to show reason why it's not a set
			return [True]
		else:
			for attribute in attrSwitcher:
				if len(attrSwitcher.get(attribute)) == 2:
					return False
			return True


	def checkSet(self): #TODO ___ this is convoluted, maybe store spots in helds instead of cards? 
		infoRay = self.is_set(self.helds, extraInfo="yes")
		if infoRay[0]:
			if self.gameState == 1:
				solit.found_a_set(self)
			else:
				puz.found_a_set(self)
		else:
			#Make a grammatically correct string explaining why helds is not a set. Handles a few possible cases.
			#REMEMBER infoRay = [False, "two of", "one of", attribute]
			self.messageFrame.after_cancel(self.msgUpdate)
			whyNot = "two cards {} {} and the other {} {}."
			badAttr = infoRay[3]
			whyNotSwitcher = {
				"number": " symbol",
				"color": "",
				"shading": "-shaded",
				"shape": ""
			}
			switchText = whyNotSwitcher.get(badAttr)
			isNums = badAttr=="number"
			isShapes = badAttr=="shape"
			edgeCase = False

			if isShapes:
				for card in self.helds:
					print(self.shapes[card.shape])
					#print(infoRay[2])
					if self.shapes[card.shape]==infoRay[2] and card.number==1: #if the bat attr is shapes and the "one off" is a singular shape
						edgeCase = True
						print("edge case")
						break
			if edgeCase:
				part4 = "a{} ".format("n" if infoRay[2]=="oval" else "") + infoRay[2] + switchText
			elif isNums and infoRay[2]!="one" or isShapes:
				part4 = infoRay[2] + switchText + "s"
			else:
				part4 = infoRay[2] + switchText
			self.message.config(text = "Not a set, " + whyNot.format(
				"have" if isNums or isShapes else "are",
				infoRay[1] + switchText + "s" if isNums and infoRay[1]!="one" or isShapes
				else infoRay[1] + switchText,
				"has" if isNums or isShapes else "is",
				part4
			))
			for x in self.field:
				for y in x:
					if y.card in self.helds:
						y.button.config(bg = "white") #this is one reason to make helds spots instead of cards
			self.msgUpdate = self.messageFrame.after(5000, self.resetMessage, "There are " + str(self.setsOnBoard) + " sets on the board right now." if self.gameState==1 else str(self.score) + " of 6 sets found.")
		self.helds = set()
	


	##########################################################################################


	def bClick(self, i, j):
		if self.field[i][j].card not in self.helds:
			self.field[i][j].button.config(bg = "orange")
			self.helds.add(self.field[i][j].card)
			if len(self.helds) > 2:
				self.checkSet()
		else:
			self.field[i][j].button.config(bg = "white")
			self.helds.remove(self.field[i][j].card)


	def dealTo(self, i, j):
		self.field[i][j].card = self.deck.pop()
		self.update_card(i, j)


	def update_card(self, i, j): 
		"""updates the button image"""
		self.field[i][j].button.config(bg = "white") #this is redundant for some calls but better than putting it everywhere
		self.field[i][j].button.config(image = self.imgDict[str(self.field[i][j].card.number) + self.field[i][j].card.color + self.field[i][j].card.shading + self.field[i][j].card.shape])


	def showSolutions(self):
		msgText = ""
		for sol in self.solutions:
			for card in sol:
				msgText += str.capitalize(self.numbers[card.number] + " " + self.colors[card.color] + " " + self.shadings[card.shading] + "-shaded " + self.shapes[card.shape] + ", ")
			msgText = msgText[:-2]
			msgText += ".\n"
		self.message.config(text = msgText)


	def buttonsInField(self):
		i = 0
		for x in self.field:
			for y in x:
				if y.button.winfo_ismapped():
					i += 1
		return i


	def resetMessage(self, msgText): 
		"""This only needs to be a separate method for timed event handling purposes"""
		self.message.config(text = msgText)
	
	


root = Tk()
GUI = Set(root)
root.mainloop()