
def onTableLoaded():
    mute()
    return

def onGameStarted():
    mute()
    global debugMode
    #set the Game Host (this player will be the owner of the Initative and Phase Markers)
    setGlobalVariable("GameHostID",str((sorted([x._id for x in getPlayers()])[0])))
    gameHost = Player(int(getGlobalVariable("GameHostID")))

    if me == gameHost:
        chooseGame()

    #log in chat screen what version of the game definiton the player is using
    publicChatMsg("{} is running v.{} of the Mage Wars module.".format(me, gameVersion))
    setPreliminaryGlobals()

    if len(getPlayers()) == 1:
        debugMode = True
        setUpTestMode()
    else:
        choosePlayerColor()
        if gameHost == me:
            remoteCall(me,"finishSetup",[])
    return

def chooseGame():
    mute()
    buttonColorList = ["#de2827","#171e78", "#01603e"]
    choiceList = ["Mage Wars Arena", "Mage Wars Academy (Coming Soon)", "Mage Wars Arena: Domination (Coming Soon)"]
    choice = askChoice("What would you like to play?", choiceList, buttonColorList)
    if choice == 1:
        setGlobalVariable("GameMode", "Arena")
        chooseMap()
    elif choice == 2:
        #setGlobalVariable("GameMode", "Academy")
        publicChatMsg('The Academy Module is not ready, switching to regular Arena')
        setGlobalVariable('GameMode', "Arena")
        chooseMap()
    elif choice == 3:
        #setGlobalVariable("GameMode", "Domination")
        publicChatMsg('The Domination Module is not ready, switching to regular Arena')
        setGlobalVariable('GameMode', "Arena")
        chooseMap()
    return

def chooseMap():
    mute()
    boardButtonColorList = []
    boardList = []
    for num in gameBoardsDict:
        boardButtonColorList.append(gameBoardsDict[num]["buttonColor"])
        boardList.append(gameBoardsDict[num]["boardName"])
    choice = askChoice("Which Arena Game board would you like to to Use?", boardList, boardButtonColorList)
    publicChatMsg('{} loads {}.'.format(me,boardList[choice-1]))
    table.board = gameBoardsDict[choice]["boardName"]
    zoneDef = gameBoardsDict[choice]["zoneDef"]
    constructZoneMap(zoneDef[0], zoneDef[1], zoneDef[2])
    return

def choosePlayerColor():
    mute()
    colorsList = []
    colorsListHex = []
    for num in playerColorDict:
            colorsListHex.append(playerColorDict[num]["Hex"])
            colorsList.append(playerColorDict[num]["PlayerColor"])
    if debugMode or len(getPlayers()) > 0:
        while (True):
            choice = askChoice("Pick a color:", colorsList, colorsListHex)
            colorsChosen = getGlobalVariable("ColorsChosen")
            if colorsChosen == "":	#we're the first to pick
                setGlobalVariable("ColorsChosen", str(choice))
                me.setGlobalVariable("MyColor", str(choice))
                me.color = playerColorDict[eval(me.getGlobalVariable("MyColor"))]['Hex']
                break
            elif str(choice) not in colorsChosen:	#not first to pick but no one else has taken this yet
                setGlobalVariable("ColorsChosen", colorsChosen + str(choice))
                me.setGlobalVariable("MyColor", str(choice))
                me.color = playerColorDict[eval(me.getGlobalVariable("MyColor"))]['Hex']
                break
            else:	#someone else took our choice
                askChoice("Someone else took that color. Choose a different one.", ["OK"], ["#FF0000"])
    return

def finishSetup(): #Waits until all players have chosen a color, then finishes the setup process.
    mute()
    #first, check whether all the players have chosen a color. If not, use remoteCall to 'bounce' finishSetup() off of OCTGN so that it checks again later.
    if len(getPlayers()) > len(getGlobalVariable("ColorsChosen")):
        remoteCall(me,"finishSetup",[])
        return
    #if everybody has chosen a color, finish the process of setting up
    PlayerSetup()
    #the Gamehost now sets up the Initative, Phase, and Roll Dice Area
    setUpDiceAndPhaseCards()
    populateDiceBanks(True,True)
    publicChatMsg("Players should now load their Spellbooks.")
    nextTurn()
    setPhase(5)
    return


def PlayerSetup():
    mute()
    playersIDList = eval(getGlobalVariable("PlayersIDList"))
    mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
    #creates a list of PlayerID's weeding out any Spectators who joined in the game lobby
    if eval(getGlobalVariable("PlayersIDList")) == []:
        for p in getPlayers():
            playersIDList.append(p._id)
            playersIDList.sort()
            setGlobalVariable("PlayersIDList",str(playersIDList))
    #creates a dictionary where { key is PlayerID : { PlayerNum, PlayerName }}
    playersIDList = eval(getGlobalVariable("PlayersIDList"))
    for i,j in enumerate(playersIDList, start=1):
        mwPlayerDict[j] = {"PlayerNum": (i),"PlayerName":Player(j).name}
        setGlobalVariable("MWPlayerDict",str(mwPlayerDict))
        

def setUpDiceAndPhaseCards():
    mute()
    tableSetup = getGlobalVariable("TableSetup")
    myColor = me.getGlobalVariable("MyColor")
    gameHost = Player(int(getGlobalVariable("GameHostID")))
    if tableSetup == "False" and gameHost == me: 
        RDA = table.create("c752b2b7-3bc7-45db-90fc-9d27aa23f1a9",0,0) #Roll Dice Area
        RDA.anchor = (True)
        init = table.create("8ad1880e-afee-49fe-a9ef-b0c17aefac3f",0,0) #initiative token
        setGlobalVariable("InitiativeCard", init._id)
        init.anchor = (True)
        init.alternate = myColor
        for c in table:
            if c.type in ['DiceRoll','Phase']: moveRDA(c)
        setGlobalVariable("TableSetup", True)

def moveRDA(card):
    """Moves the dice roll area/initiative/phase marker to the appropriate area"""
    cardW = cardSizes[card.size]['width']
    cardType = card.type
    mapDict = eval(getGlobalVariable("Map"))
    mapX,mapY = mapDict["minx"],mapDict["miny"]
    zoneSize = mapDict["tileSize"]
    rdaI,rdaJ = mapDict["RDA"]
    rowY = mapY + rdaJ*zoneSize
    x,y = 0,0

    if cardType == "DiceRoll":
        x = mapX - cardW - 10
        y = rowY - zoneSize + 100
        mapDict['DiceBoxLocation'] = (x,y)
        setGlobalVariable("Map",str(mapDict))

    elif 'Player Token' in card.name:
            x = mapX - cardW - 52
            y = rowY - zoneSize + 10
    card.moveToTable(x,y,True)
    return

def setUpTestMode():
    setGlobalVariable('debugMode', True)
    setGlobalVariable("PlayerWithIni", str(me._id))
    setGlobalVariable("MWPlayerDict",str({1:{"PlayerNum": 1,"PlayerName":me.name}}))
    me.setGlobalVariable("MyColor",str(4)) #Purple for testing
    me.color = playerColorDict[eval(me.getGlobalVariable("MyColor"))]['Hex']
    setUpDiceAndPhaseCards()
    populateDiceBanks(True,True)
    setPhase(5)
    return

def setPreliminaryGlobals():
    #create a dictionary of attachments and bound spells and enable autoattachment
    setGlobalVariable("attachDict",str({}))
    setGlobalVariable("bindDict",str({}))
    setSetting("AutoAttach", True)

    #set global event lists for rounds and single actions
    setGlobalVariable("roundEventList",str([]))
    setGlobalVariable("turnEventList",str([]))

    #Set the round to 1
    setGlobalVariable("RoundNumber", str(1))
    
    #new Player Order
    setGlobalVariable("PlayersIDList",str([]))
    setGlobalVariable("MWPlayerDict",str({}))
    return

def onDeckLoaded(args):
    #args = player,groups
    mute()
    deck = args.groups[0]
    if args.player == me:
        decksLoaded = getGlobalVariable("DeckLoaded")
        
        if getGlobalVariable("DeckLoaded") == "True":
            publicChatMsg("{} has attempted to load a second Spellbook, the old Spellbook will be deleted".format(me))
            deletedeck(args)
        elif validateDeck(deck):
            setGlobalVariable("DeckLoaded", str(int(decksLoaded)+1))
            setUpMageDict()
            if eval(getGlobalVariable("DeckLoaded")) == len(getPlayers()): 
                setGlobalVariable("DeckLoaded","True")

        else:
            publicChatMsg("Validation of {}'s spellbook FAILED. Please choose another spellbook.".format(me.name))
            choiceList = ['Yes', 'No']
            colorList = ['#0000FF', '#FF0000']
            loadNewPrompt = askChoice("Would you like to delete the deck and load a new one?", choiceList, colorList)
            if loadNewPrompt == 1:
                deletedeck(args)                
    return

def deletedeck(args):
    for group in args.groups:
        for card in group:
            if card.controller == me:
                card.delete()
    decksLoaded = getGlobalVariable("DeckLoaded")
    if decksLoaded == "True":
        decksLoaded = len(getPlayers())
        decksLoaded-=1
        setGlobalVariable("DeckLoaded", min(decksLoaded, 0))
    else:
        setGlobalVariable("DeckLoaded", min(decksLoaded, 0))


def setUpMageDict():
    mageDict = eval(me.getGlobalVariable("MageDict"))
    for card in me.piles["Spellbook"]:
        if card.Subtype == "Mage":
            mageDict["MageID"] = card._id
            if card.Name == 'Adramelech Warlock':
                adra = eval(getGlobalVariable('adramelechWarlock'))
                adra.append(card._id)
                setGlobalVariable('adramelechWarlock', str(adra))
        elif card.Type == "Magestats":
            mageDict["MageStatsID"] = card._id
    me.setGlobalVariable("MageDict",str(mageDict))
    return mageDict

def mageSetup():
    mute()
    mageDict = eval(me.getGlobalVariable("MageDict"))
    #deck hasn't been loaded or the mage the mage card was flipped face down after mageSetup() has already run once
    if mageDict["MageStatsID"] == 00000 or mageDict["MageRevealed"] == "True": return

    mageID = int(mageDict["MageID"])
    mage = Card(mageID)
    mageStatsID = int(mageDict["MageStatsID"])
    magestats = Card(mageStatsID)

    #set initial health and channeling values
    me.Channeling = int(mage.Stat_Channeling)
    me.Mana = me.Channeling + 10
    me.Life = int(mage.Stat_Life)

    #setup mage card props
    transferPropsFromStats(mage,magestats)
    addDefaultTraits(mage)
    addInitialZone(mage)

    mageDict["MageRevealed"] = "True"
    me.setGlobalVariable("MageDict",str(mageDict))
    notify("{} enters the Arena! - Channeling is set to {} and Mana is set to {} and Life set to {}\n".format(Card(mageID),me.Channeling,me.Mana,me.Life))
    
    #using this to figure out when to roll initiative
    magesRevealed = getGlobalVariable("MagesRevealed")
    setGlobalVariable("MagesRevealed", magesRevealed + str(1))
    gameHost = Player(int(getGlobalVariable("GameHostID")))
    if gameHost == me:
            remoteCall(me,"determineInitiative",[])


#Old method, not sure why they did it this way. Might need rewritten
def transferPropsFromStats(mage, magestats):
    mage.Subtype = magestats.Subtype
    mage.Level = magestats.Level
    mage.Attack = magestats.Attack
    mage.nativeTraits = magestats.nativeTraits
    mage.alternate = "2"
    mage.Subtype = mage.alternateProperty("", "Subtype")
    mage.Level = mage.alternateProperty("", "Level")
    mage.Attack = mage.alternateProperty("", "Attack")
    mage.alternate = ""

def determineInitiative():
    mute()
    #first, check whether all the players revealed their Mages. If not, use remoteCall to 'bounce' determineInitiative() off of OCTGN so that it checks again later.
    if len(getPlayers()) > len(getGlobalVariable("MagesRevealed")):
        remoteCall(me,"determineInitiative",[])
        return
    initRoll = rollForInitiative()
    rerolls = 0
    while initRoll.count(max(initRoll)) > 1 and rerolls <= 3:
        publicChatMsg("High roll tied! Rolling again.")
        initRoll = rollForInitiative()
        rerolls += 1
        if rerolls == 3:
            randomlyDetermineInit(len(getPlayers())) 
    
    victoriousPlayerID = initRoll.index(max(initRoll))+1
    remoteCall(Player(victoriousPlayerID), "AskInitiative", [victoriousPlayerID])
    
def rollForInitiative():
    initRoll = []
    rollForPlayer = 0
    for p in getPlayers():
        publicChatMsg("Automatically rolling initiative for {}...".format(p.name))
        initRoll.append(rnd(1,12))
        publicChatMsg("{} rolled a {} for initiative".format(p.name, initRoll[rollForPlayer]))
        rollForPlayer += 1
        myRollStr = (str(p._id) + ":" + str(initRoll) + ";")
        setGlobalVariable("OppIniRoll", getGlobalVariable("OppIniRoll") + myRollStr)
        update()
    return initRoll

def randomlyDetermineInit(numPlayers): #Need to write
    return

def AskInitiative(playerID):
    mute()
    publicChatMsg("{} has won the Initative Roll and is deciding who should go first.".format(me))
    players = getPlayers()
    choices = [p.name + (" (me)" if p==me else "") for p in players]
    colors = [(playerColorDict[int(p.getGlobalVariable("MyColor"))]["Hex"]) for p in players]
    choice = askChoice("Who should go first?",choices,colors)
    if choice == 0: 
        choice = 1
    firstPlayer = players[choice - 1]
    playerID = firstPlayer._id
    publicChatMsg("A decision has been reached! {} will go first.".format(firstPlayer))
    setGlobalVariable("PlayerWithIni", str(playerID))
    setGlobalVariable("GameSetup", "True")
    init = [card for card in table if card.model == "8ad1880e-afee-49fe-a9ef-b0c17aefac3f"][0]
    init.alternate = Player(playerID).getGlobalVariable("MyColor")
    