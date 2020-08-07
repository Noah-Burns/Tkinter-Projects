from tkinter import LabelFrame, Frame, Label
from random import shuffle


class Card:
	def __init__(self, number, color, shading, shape):
		self.number = number
		self.color = color
		self.shading = shading
		self.shape = shape


def start(self):
	self.gameState = 2
	self.puzSols = []
	self.message.config(text ="0 of 6 sets found.")

	self.start_shared() 
	self.fieldFrame.config(text = "Puzzle Mode")
	self.foundSets = LabelFrame(self.gameFrame, text="Sets Found")
	self.foundSets.grid(row=0, column=1, padx=(0,40))
	self.fsFrame = Frame(self.foundSets, bg="black")
	self.fsFrame.pack()
	self.scoreboard.config(text = "")
	self.deckStatus.config(text = "")
	for i in range(6):
		for j in range(3):
			img = self.empty.subsample(2,2)
			self.fsLabel = Label(self.fsFrame, image=img, bg="white")
			self.fsLabel.image = img #necessary to prevent image from being GC'd
			self.fsLabel.grid(row=i, column=j, padx=2, pady=2)
	dummy_puz_build(self)
	for i in range(3):
		for j in range(4):
			self.field[i][j].card = self.puzField.pop()
			self.update_card(i,j)


def dummy_puz_build(self):
	self.puzField = []
	deck = [Card(w,x,y,z) for w in self.numbers for x in self.colors for y in self.shadings for z in self.shapes]

	shuffle(deck)
	for i in range(12):
		self.puzField.append(deck[i])
	setsDealt = self.sets_finder(self.puzField)
	if len(setsDealt) == 6:
		self.solutions = setsDealt
		return
	dummy_puz_build(self)



def update_found_sets(self):
	i = 0
	setCards = list(self.helds)
	for imgLbl in self.fsFrame.winfo_children(): #NB score is incremented AFTER this method gets called
		if i < self.score*3:
			i += 1
		elif i < self.score*3 + 3:
			card = setCards[i-self.score*3]
			img = self.imgDict[str(card.number) + card.color + card.shading + card.shape].subsample(2,2)
			imgLbl.config(image= img)
			imgLbl.image = img
			i += 1
		else:
			break



def found_a_set(self):
	for x in self.helds:
		for y in self.field:
			for z in y:
				if x==z.card:
					z.button.config(bg = "white") 
	if frozenset(self.helds) not in self.puzSols:
		self.puzSols.append(frozenset(self.helds)) #these need to be made immutable or they get overwritten
		update_found_sets(self)
		self.score += 1
		self.messageFrame.after_cancel(self.msgUpdate)
		self.message.config(text= str(self.score) + " of 6 sets found.")
	else:
		self.messageFrame.after_cancel(self.msgUpdate)
		self.message.config(text= "Already found that set ...")
		self.msgUpdate = self.messageFrame.after(2000, self.resetMessage, str(self.score) + " of 6 sets found.")
	for x in self.helds:
		for y in self.field:
			for z in y:
				if x==z.card:
					z.button.config(bg = "white") 
	if self.score > 5:
		self.gameOver()	
	self.helds = set()