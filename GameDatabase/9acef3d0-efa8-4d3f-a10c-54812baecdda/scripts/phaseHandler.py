# removing gameTurn as python GlobalVariables
# removing roundTimes as python GlobalVariables


def nextPhase(group,x=0,y=0):
	mute()
	mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
	playerNum = mwPlayerDict[me._id]["PlayerNum"]
	gameMode = getGlobalVariable("GameMode")

	if debugMode:	#debuggin'
		if gameMode == "Arena" or "Domination": nextPhaseArena()
		elif gameMode == "Academy": nextPhaseAcademy()
		return True
	else:
		doneWithPhase = getGlobalVariable("DoneWithPhase")
		if str(playerNum) in doneWithPhase:
			return
		doneWithPhase += str(playerNum)
		if len(doneWithPhase) != len(getPlayers()):
			setGlobalVariable("DoneWithPhase", doneWithPhase)
			if currentPhase()[1]<5:
				notify("{} is ready to move on with the {}\n".format(me.name,currentPhase()[0]))
			else:
				notify("{} is done with the {}\n".format(me.name,currentPhase()[0]))

			return False
		else:
			setGlobalVariable("DoneWithPhase", "")
			if gameMode == "Arena" or "Domination" or "Playtest": nextPhaseArena()
			elif gameMode == "Academy": nextPhaseAcademy()
			return True


def nextPhaseArena():
	mute()
	'''gameIsOver = getGlobalVariable("GameIsOver")
	if gameIsOver:	#don't advance phase once the game is done
		notify("Game is Over!")
		return'''
	if getGlobalVariable("GameSetup") != "True": # Player setup is not done yet.
		return
	card = None
	#checkMageDeath(0)
	if currentPhase()[0] == "Upkeep Phase":
		for p in players:
			remoteCall(p, "upkeepPhase", [])
		setPhase(5)
	elif currentPhase()[0] == "Planning Phase":
		setPhase(6)
	elif currentPhase()[0] == "Deployment Phase":
		setPhase(7)
	elif currentPhase()[0] == "First QC Phase":
		setPhase(8)
	elif currentPhase()[0] == "Actions Phase":
		setPhase(9)
	elif currentPhase()[0] == "Final QC Phase":
		nextTurn()

		flipInitiative()

		setEventList('Round',[])#This helps track defenses, arcane zap, etc
		setEventList('Turn',[])#This helps track defenses, arcane zap, etc
		for p in players:
			'''remoteCall(p, "resetDiscounts",[])'''
			remoteCall(p, "resetAndChannel", [])
		setPhase(4)
	update()

def flipInitiative():
	nextPlayer = getNextPlayerNum()
	setGlobalVariable("PlayerWithIni", str(nextPlayer))
	initiativeCard = Card(int(getGlobalVariable("InitiativeCard")))
	for p in players:
		if initiativeCard.controller == p:
			remoteCall(p, "changeIniColor", [initiativeCard])
	return

def changeIniColor(initiativeCard):
	mute()
	myColor = me.getGlobalVariable("MyColor")
	colorsChosen = getGlobalVariable("ColorsChosen")
	oppColor = colorsChosen.replace(myColor, '')
	mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
	if mwPlayerDict[me._id]["PlayerNum"] == int(getGlobalVariable("PlayerWithIni")):
		initiativeCard.alternate = myColor
	else:
		initiativeCard.alternate = oppColor

def i_have_initiative():
	mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
	if mwPlayerDict[me._id]["PlayerNum"] == int(getGlobalVariable("PlayerWithIni")):
		return True
	else:
		return False

def getNextPlayerNum():
	activePlayer = int(getGlobalVariable("PlayerWithIni"))
	nextPlayer = (activePlayer + 1)%2
	return nextPlayer

def remoteHighlight(phaseCard, color):
	phaseCard.highlight = color

def remoteSwitchPhase(phaseCard,phase):
	phaseCard.alternate = phase

def checkInit(player = None):
	mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
	if player:
		if player == int(getGlobalVariable("PlayerWithIni")):
			return True
		else:
			return False
	elif mwPlayerDict[me._id]["PlayerNum"] == int(getGlobalVariable("PlayerWithIni")):
		return True
	else:
		return False
