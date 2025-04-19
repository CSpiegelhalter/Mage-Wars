def publicChatMsg(string):
	mute()
	gameHost = Player(int(getGlobalVariable("GameHostID")))
	gameLog = getGlobalVariable('GameLog')
	notify("{}".format(string))
	if me == gameHost: 
		gameLog += string + "\n"
		setGlobalVariable('GameLog',str(gameLog))
	return

def debug(str):
	mute()
	global debugMode
	if debugMode:
		whisper("Debug Msg: {}".format(str))
	return

def toggleDebug(group, x=0, y=0):
	global debugMode
	debugMode = not debugMode
	if debugMode:
		notify("{} turns on debug\n".format(me))
	else:
		notify("{} turns off debug\n".format(me))
	return

def onCardDoubleClicked(args):
	#args = card, mouseButton, keysDown
	mute()
	if args.card.type == "DiceRoll":
		genericAttack(0)

def listenForClick(arg):
	global passOnClick
	whisper(arg.get("Click Prompt","Left click to select target"))
	passOnClick = arg

def onCardClicked(args):
	#args = card, mouseButton, keysDown
	mute()
	return

def getEventList(roundOrTurn):
		return (eval(getGlobalVariable("roundEventList")) if roundOrTurn =='Round' else eval(getGlobalVariable("turnEventList")))

def setEventList(roundOrTurn,eventList):
		if roundOrTurn =='Round': setGlobalVariable("roundEventList",str(eventList))
		else: setGlobalVariable("turnEventList",str(eventList))

def appendEventList(roundOrTurn,event):
		eventList = getEventList(roundOrTurn)
		eventList.append(event)
		setEventList(roundOrTurn,str(eventList))

def getMage():
	mageDict = eval(me.getGlobalVariable("MageDict"))
	mage = Card(mageDict['MageID'])
	return mage

def getMageStats():
	mageDict = eval(me.getGlobalVariable("MageDict"))
	mageStats = Card(mageDict['MageStatsID'])
	return mageStats

def checkForSirenMage():
	mage = getMage()
	if mage.name == 'Siren':
		return True
	else:
		return False

def forceCardsWithDissipate():
	cardList = []
	for card in table:
		if card.markers[Dissipate] and 'Force' in card.Subtype and card.controller == me:
			cardList.append(card)
	return cardList

def getCard(desiredCard):
	for card in table:
		if card.name == desiredCard:
			return card
	return None

def get_all_cards_of_name(desiredCard):
	cardList = [card for card in table if card.name == desiredCard]
	return cardList

def createCard(group,x=0,y=0):
	mute()
	global debugMode
	cardName = askString("Create which card?","Enter card name here")
	guid,quantity = askCard({'Name':cardName},title="Select card version and quantity")
	if guid and quantity:
		cards = ([table.create(guid,0,0,1,True)] if quantity == 1 else table.create(guid,0,0,quantity,True))
		for card in cards:
			card.moveTo(me.piles["Spellbook"])
			if not debugMode:
				notify("*** WARNING *** - Spellbook is no longer validated\n")
			notify("A {} was created and was placed into {}'s spellbook.\n".format(card, me))

def boolQuery(query_text,true_text,false_text): # string -> string -> string -> bool
	"""A generic boolean query menu with customizable text for both options"""
	if askChoice(query_text,[true_text,false_text],["#009933","#ff0000"]) == 1: return True
	return False

def getElementals(mage):
	elementalList = []
	for card in table:
		if card.isFaceUp and card.controller == mage.controller and 'Elemental' in card.Subtype:
			elementalList.append(card)
		elif card.isFaceUp and card.controller == mage.controller and 'Golem' in card.Subtype:
			elementalList.append(card)
		elif card.isFaceUp and card.controller == mage.controller and 'Sprite' in card.Subtype:
			elementalList.append(card)
	return elementalList

def create_card_dialog(list, title, min = 1, max = 1):
	dialog = cardDlg(list)
	dialog.min = min
	dialog.max = max
	dialog.title = title
	selectedList = dialog.show()
	return selectedList

def create_double_list_dialog(list1,list2, title,label, bottom_label, min = 1, max = 1):
	dialog = cardDlg(list1, list2)
	dialog.label = label
	dialog.bottomLabel = bottom_label
	dialog.title = title
	return dialog

def damage_transfer(transfer_from_target, transfer_to_target, source = 'Lifebond', amount = 2):
    transfer_from_target = transfer_from_target[0]
    transfer_to_target = transfer_to_target[0]
    damage_transferred_input = min(askInteger('How much damage would you like to transfer?', amount), amount)
    max_damage_transferred = get_total_damage_markers(transfer_from_target)
    damage_transferred = min(damage_transferred_input, max_damage_transferred)
    notify('{} uses {} to transfer {} damage from {} to {}!'.format(me,source, damage_transferred, transfer_from_target, transfer_to_target))
    subDamageAmount(transfer_from_target, damage_transferred)
    addDamageAmount(transfer_to_target, damage_transferred)
    return

def malakaisFirePrompt(heathen):
	mute()
	if askChoice("Smite the heathen with Malakai's Fire?",["Yes, burn the heathen!","No"],["#01603e","#de2827"])==1:
		notify("{} Smites the heathen {} with Malakai's Fire!\n".format(me,heathen))
		rememberPlayerEvent("Malakai's Fire")
		remoteCall(heathen.controller,"malakaisFireReceiptPrompt",[heathen])

def malakaisFireReceiptPrompt(heathen):
	mute()
	if askChoice("Malakai smites {}! Apply Burn condition?".format(heathen.Name.split(",")[0]),["Yes","No"],["#01603e","#de2827"])==1:
		heathen.markers[Burn]+=1
		bookOfMalakai=["...AND THE HEATHENS IN THEIR TREACHERY DOTH BURN LIKE CANDLES, SPAKE MALAKAI. AND LO, SO THEY DID BURN.\n- The book of Malakai, 16:3",
					"...AND HE LIT A THOUSAND FIRES BENEATH THE FOUL. AND MALAKAI SAW THAT IT WAS JUST.\n- The book of Malakai, 19:25",
					"...LET HE WHO JUDGETH WITH NO CAUSE BE JUDGED FIRST. AND THEN BURN HIM.\n-The book of Malakai, 4:22",
					"...BEHOLD YE, FOR THIS IS THE FLAME OF RIGHTEOUSNESS. SEE THAT IT BURNETH EVERMORE IN YOUR HEART. AND ALSO IN THE HEARTS OF THE UNBELIEVERS, BUT IN A MORE LITERAL SENSE.\n-The book of Malakai, 5:18",
					"...FOR I AM THE CANDLE IN THE DARK. THE FEAR IN THE EYES OF THE UNJUST. THE BANE OF THE IMPURE.\n-The book of Malakai, 8:9",
					"...ALL WHO KNEEL BEFORE EVIL SHALL CLAIM THE FIRE OF WRATH AS THEIR REWARD. AS WILL THE EVIL THEMSELVES. REALLY, THOU SHOULDST NOT DISCRIMINATE IN ITS DISTRIBUTION.\n-The book of Malakai, 3:19",
					"...AND MALAKAI GESTURED AT THE LADDINITES, AND LO! EACH BECAME A PILLAR OF FLAME, THEIR WICKEDNESS BURNING BRIGHTER THAN THE SUN.\n-The book of Malakai, 2:4",
					"...AND MALAKAI DID SEE THAT THEY HAD VERILY REPENTED. AND PROCLAIMING THAT SOME CRIMES ARE FORGIVEN BUT THROUGH FLAME, HE SEARED THEIR WICKEDNESS FROM THEIR BONES.\n-The book of Malakai, 8:7",
					"... AND I WILL STRIKE DOWN UPON THEE WITH GREAT VENGEANCE AND FURIOUS ANGER THOSE WHO ATTEMPT TO POISON AND DESTROY MY BROTHERS. AND YOU WILL KNOW MY NAME IS MALAKAI WHEN I LAY MY LIGHT UPON THEE \n-The book of Malakai, 25:17"]
		passage=rnd(0,len(bookOfMalakai)-1)
		notify(bookOfMalakai[passage])
		notify("{} is seared by the flames of righteousness! (+1 Burn)\n".format(heathen.Name.split(",")[0]))

def determine_crumble_cost(params):
	target = params.get('target')
	cost = int(target.Cost)
	return cost

def determine_dissolve_cost(params):
	target = params.get('target')
	equipmentList = get_faceup_equipment_list(target)
	selectedList = create_card_dialog(equipmentList, 'What would you like to Dissolve?', 0, 1)
	cost =0
	if selectedList:
		equipmentChoice = selectedList[0]
		notify('{} cast Dissolve on {}'.format(me, equipmentChoice.name))
		equipmentChoice.target()
		cost = int(equipmentChoice.Cost)
		return cost, equipmentChoice
	return cost, None

def determine_explode_cost(params):
	target = params.get('target')
	equipmentList = get_faceup_equipment_list(target)
	selectedList = create_card_dialog(equipmentList, 'What would you like to explode?', 0, 1)
	cost =0
	if selectedList:
		equipmentChoice = selectedList[0]
		notify('{} casts Explode on {}'.format(me, equipmentChoice.name))
		equipmentChoice.target()
		cost = int(equipmentChoice.Cost) + 6
		return cost, equipmentChoice
	return cost, None

def determine_steal_equipment_cost(params):
	target = params.get('target')
	equipmentList = get_faceup_equipment_list(target)
	selectedList = create_card_dialog(equipmentList, 'What would you like to steal?', 0, 1)
	cost = 0
	if selectedList:
		equipmentChoice = selectedList[0]
		notify('{} casts destroys {}'.format(me, equipmentChoice.name))
		equipmentChoice.target()
		cost = int(equipmentChoice.Cost)*2
		return cost, equipmentChoice
	return cost, None

def determine_disarm_cost(params):
	target = params.get('target')
	equipmentList = get_faceup_equipment_list(target)
	selectedList = create_card_dialog(equipmentList, 'What would you like to Disarm?', 0, 1)
	cost = 0
	if selectedList:
		equipmentChoice = selectedList[0]
		notify('{} Disarms {}'.format(me, equipmentChoice))
		equipmentChoice.target()
		equipmentChoice.markers[Disable] += 1
		cost = getTotalCardLevel(equipmentChoice)
	return cost

def get_faceup_equipment_list(target):
	equipmentList =[]
	for card in table:
		if card.Type == 'Equipment' and card.controller == target.controller and card.isFaceUp:
			equipmentList.append(card)
	return equipmentList

def determine_defend_cost(params):
	target = params.get('target')
	target_level = getTotalCardLevel(target)
	if target_level <3:
		cost = 1
	elif target_level < 5:
		cost = 2
	else:
		cost = 3
	return cost

def determine_quicksand_cost(params):
	target = params.get('target')
	target_level = getTotalCardLevel(target)
	cost = 2*target_level
	return cost

def determine_disperse_cost(params):
	target = params.get('target')
	cost = int(target.Reveal_Cost)
	return cost

def determine_fizzle_cost(params):
	target = params.get('target')
	cost = int(target.Reveal_Cost)
	return cost

def determine_dispel_cost(params):
	target = params.get('target')
	cost = int(target.Reveal_Cost) + int(target.Cost)
	return cost

def determine_rouse_cost(params):
	target = params.get('target')
	target_level = getTotalCardLevel(target)
	cost = target_level
	return cost

def determine_shift_enchant_cost(params):
	target = params.get('target')
	if target.isFaceUp:
		target_level = getTotalCardLevel(target)
		cost = target_level
	else:
		cost =1
	return cost

def determine_sleep_cost(params):
	target = params.get('target')
	target_level = getTotalCardLevel(target)
	if target_level <2:
		cost = 4
	elif target_level < 3:
		cost = 5
	elif target_level < 4:
		cost = 6
	else:
		cost = (target_level-3)*2 + 6
	return cost

def determine_SH_cost(params):
	target = params.get('target')
	target_cost = int(target.Cost)
	attach_list = getAttachedCards(target)
	attach_cost = 0
	for card in attach_list:
		if card.isFaceUp:
			attach_cost += int(card.Cost)+int(card.Reveal_Cost)
		else:
			attach_cost+=2
	cost = target_cost + attach_cost
	return cost
	
def determine_steal_enchant_cost(params):
	target = params.get('target')
	cost = (int(target.Cost) + int(target.Reveal_Cost))*2
	return cost

def determine_upheaval_cost(params):
	target = params.get('target')
	target_cost = int(target.Cost)
	attach_list = getAttachedCards(target)
	attach_cost = 0
	for card in attach_list:
		if card.isFaceUp and card.Reveal_Cost != '':
			attach_cost += int(card.Cost)+int(card.Reveal_Cost)
		elif card.isFaceUp:
			attach_cost += int(card.Cost)
		else:
			attach_cost+=2
	cost = target_cost + attach_cost
	return cost

def deathPrompt(card):
		mute()
		if not "Mage" in card.Subtype and not card.isDestroyed: 
			life_total = eval(card.Total_Life if not card.Total_Life == '' else card.Stat_Life)
			damage_total, sources = get_collected_damage_total(card)
			choice = askChoice("{} appears to be destoyed. \nCalculated from: \nLife: {} \tDamage: {}{}{}{}. \n\nAccept destruction?".format(card.name, 
																																		life_total,
																																		damage_total,
																																		'\n\tfrom Damage markers: '+str(sources[0]),
																																		'\n\tfrom Tainted (markers): '+str(sources[1])+'('+str(sources[1]/3)+')' if sources[1] > 0 else '',
																																		'\n\tfrom Freeze (markers): '+str(sources[2]) +'('+str(sources[1]/2)+')' if sources[2] > 0 else ''),
							["Yes","No"],
							["#01603e","#de2827"])
			if choice == 1:
				notify('{} is destroyed'.format(card))
				card.isDestroyed = 'True'
				discard(card)
			else: notify("{} does not accept the destruction of {}.\n".format(me,card))
		elif 'Mage' in card.Subtype:
			life_total = me.Life
			damage_total, sources = get_collected_damage_total(card)
			choice = askChoice("Your {} appears to have fallen in the arena! \nCalculated from: \nLife: {} \tDamage: {}{}{}{}. \n\nAccept Loss?".format(card.name, 
																																						life_total,
																																						damage_total,
																																						'\n\tfrom Damage markers: '+str(sources[0]),
																																						'\n\tfrom Tainted markers: '+str(sources[1]) if sources[1] > 0 else '',
																																						'\n\tfrom Freeze markers: '+str(sources[2]) if sources[2] > 0 else ''),
							["Yes","No"],
							["#01603e","#de2827"])
			if choice == 1:
				card.orientation = 1
				notify('{} has fallen in the Arena!'.format(me))

def get_collected_damage_total(card):
	if 'Mage' in card.Subtype:
		damage_amount = me.Damage
		damage_total = damage_amount + 3*card.markers[Tainted] + 2*card.markers[Freeze]
		
		sources = [damage_amount, 3*card.markers[Tainted], 2*card.markers[Freeze]]
	else:
		traits = getTraits(card)
		damage_amount = card.markers[Damage]
		if traits.get('Living'):
			damage_total = card.markers[Damage] + 3*card.markers[Tainted] + 2*card.markers[Freeze]
			sources = [damage_amount, 3*card.markers[Tainted], 2*card.markers[Freeze]]
		else:
			damage_total = card.markers[Damage]
			sources = [damage_amount, 0, 0]	
	return damage_total, sources

def get_collected_life_total(card):#Remove maybe? Not used right now

	base_life = eval(card.Stat_Life)
	
	traits = getTraits(card)
	life_adj = traits.get('Life',0)
	sources = [base_life, life_adj]
	return sources