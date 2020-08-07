from random import shuffle

def start(self): #TODO___ optimize the starting methods? combine?
	self.scoreboard.config(text = "0 sets found.")
	self.start_shared()
	if self.foundSets.winfo_ismapped():
		self.foundSets.grid_forget()
	self.fieldFrame.config(text = "Solitaire")
	self.gameState = 1

	shuffle(self.deck)
	for j in range(4):
		for i in range(3):
			self.dealTo(i, j)
	self.sets_finder([spot.card for row in self.field for spot in row if spot.card is not None])
	self.deckStatus.config(text = str(len(self.deck)) + " cards left in deck.")


def sets_finder_handler(self, numSets):
	if numSets == 0: # With 21 cards this should never be true, max. number of spots before a set is inevitable is 20
		if len(self.deck) == 0:
			self.gameOver()
			return
		for x in self.field[0]:
			if x.card is None:
				for i in range(3):
					dealSpot = self.field[i][x.col]
					self.dealTo(dealSpot.row,dealSpot.col) #deal to each empty spot in the first column with an empty spot
					dealSpot.button.grid(row=dealSpot.row, column=dealSpot.col) #regrid the buttons that just got a card from no card
				break
		self.justDealt = True #for updating the message if no sets are found and more cards dealt
		self.message.config(text ="No sets were found, more cards dealt ...")
		self.sets_finder([spot.card for row in self.field for spot in row if spot.card is not None])
	else:
		if self.justDealt:
			self.messageFrame.after_cancel(self.msgUpdate)
			self.messageFrame.after(2000, self.resetMessage, "There are " + str(numSets) + " sets on the board right now.")
		else:
			self.message.config(text ="There are " + str(numSets) + " sets on the board right now.")
		for x in self.field:
			for y in x:
				if y.card is None:
					y.button.grid_forget() #finally, ungrid the buttons with no card
		self.justDealt = False 


def found_a_set(self):
	self.score += 1
	numcards = 0

	if self.buttonsInField() == 12 and len(self.deck) > 0: #TODO___ fix this messy if else
		# Only DON'T redeal (else -> restructure method) if it's (15, 18, or 21), or if the deck is empty
		# there will never be < 12 buttonsInField without an empty deck
		for x in self.helds:
			for y in self.field:
				for z in y:
					if x==z.card:
						z.card = None
						self.dealTo(z.row, z.col)    
	else:
		for x in self.helds:
			for y in self.field:
				for z in y:
					if x==z.card:
						z.card = None #setting the cards to None and not redealing will ungrid 3 buttons (after they're restructured)
						z.button.config(bg = "white") #this is nomrally accomplished in the updateCard method but we only need this part of it
		restructure(self,self.buttonsInField())

	self.sets_finder([spot.card for row in self.field for spot in row if spot.card is not None])
	self.scoreboard.config(text = str(self.score) + " sets found.")
	self.deckStatus.config(text = str(len(self.deck)) + " cards left in deck.")


def restructure(self,numCards):
	"""Puts the spots with a card back into a rectangle."""
	emptySpots = []
	filledOuterSpots = []
	for u in self.field:
		for v in u:
			if v.col <= (numCards-3)/3-1 and v.card is None:
				# (numCards-3)/3 should be the number of 3-card columns we'll have in the new core after removing the 3 helds.
				# these emptySpots are the ones with .card==None in the new core to be filled
				emptySpots.append(v)
			if v.col > (numCards-3)/3-1 and v.card is not None:
				filledOuterSpots.append(v)
	for i in range(len(emptySpots)):
		emptySpots[i].card = filledOuterSpots[i].card
		self.update_card(emptySpots[i].row, emptySpots[i].col)
		filledOuterSpots[i].card = None #tags the spot for ungridding