
def playCardFaceDown(card, x=0, y=0):
	mute()
	myHexColor = playerColorDict[eval(me.getGlobalVariable("MyColor"))]['Hex']
	card.isFaceUp = False
	moveCardToDefaultLocation(card)
	card.peek()
	card.highlight = myHexColor
	notify("{} prepares a Spell from their Spellbook by placing a card face down on the table.\n".format(me))


def moveCardToDefaultLocation(card,returning=False):#Returning if you want it to go to the returning zone
	mute()
	mapDict = eval(getGlobalVariable('Map'))
	mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
	playerNum = mwPlayerDict[me._id]["PlayerNum"]
	x,y = 0,0
	if not card.isFaceUp: cardW,cardH = cardSizes[card.size]['backWidth'],cardSizes[card.size]['backHeight']
	else: cardW,cardH = cardSizes[card.size]['width'],cardSizes[card.size]['height']
	if mapDict:
		zoneArray = mapDict.get('zoneArray')
		cardType = card.type
		cardSubtype = card.Subtype
		if cardType == 'Internal': return
		mapX,mapW = mapDict.get('minx'),mapDict.get('X')
		for i in range(len(zoneArray)):
				for j in range(len(zoneArray[0])):
						zone = zoneArray[i][j]
						if zone and zone.get('startLocation') in [str(playerNum),"*"]:
								zoneX,zoneY,zoneS = zone.get('x'),zone.get('y'),zone.get('size')
								if cardSubtype == "Mage":
										x = (zoneX if i < mapDict.get('Horizontal Zone Dimension')/2 else zoneX + zoneS - cardW)
										y = (zoneY if j < mapDict.get('Vertical Zone Dimension')/2 else zoneY + zoneS - cardH)
								elif cardType == 'Magestats':
										x = (zoneX - cardW if i < mapDict.get('Horizontal Zone Dimension')/2 else mapX + mapW)
										y = (zoneY if j < mapDict.get('Vertical Zone Dimension')/2 else zoneY+zoneS-cardH)
								else:
										x = (zoneX - cardW if i < mapDict.get('Horizontal Zone Dimension')/2 else mapX + mapW)
										y = (zoneY+cardH+cardH*int(returning) if j < mapDict.get('Vertical Zone Dimension')/2 else zoneY+zoneS-2*cardH-cardH*int(returning))
										dVector = ((-1,0) if i<mapDict.get('Horizontal Zone Dimension')/2 else (1,0))
										x,y = splay(x,y,dVector)
	card.moveToTable(x,y,True)
	card.formerZone = ''
	return

def onCardsMoved(args):#TODO: When a card is moved back to the spellbook, remove bTraits, zTraits, etc
	'''args = 	player,			Player moving the cards
				cards, 			list of cards being moved
				fromGroups, 	original groups of the cards (Table, Spellbook, Discard Pile, etc)
				toGroups, 		new groups of the cards (Table, Spellbook, Discard Pile, etc)
				indexs,			original z indexes of cards
				xs,ys,			original x, y coords
				highlights,		original highlights
				markers,		original markers
				faceups			original face up statuses'''
	mute()
	setGlobalVariable("MoveCardArgs",str(args))
	cards = args.cards
	actionType = None
	hasAttached = False 
	for card in cards:	
		if card.Type in typeIgnoreList or card.Name in typeIgnoreList or 'Magestats' in card.Type: return
		if card.controller==me and not card.isAttachedTo=='':
			#debug('card is attached')
			detach(card)
			updateCardLocation(card, args.xs, args.ys, args.toGroups, args.fromGroups)
			updateCardsInZone(card)
		elif card.controller == me and not card.isBoundTo=='':
			#debug('card is bound')
			unbind(card)
			updateCardLocation(card, args.xs, args.ys, args.toGroups, args.fromGroups)
			updateCardsInZone(card)
		elif card.controller == me and table in args.toGroups:
			#debug('table in args.toGroups')
			updateCardLocation(card, args.xs, args.ys, args.toGroups, args.fromGroups)
			updateCardsInZone(card)
			#snapToZone(card)
			alignAttachments(card)
			alignBound(card)
		elif card.controller == me and ('Spellbook' in args.toGroups[0].name or 'Discard Pile' in args.toGroups[0].name):
			#debug('spellbook or discard pile')
			removeBestowedAttack(card)
			detach(card)
			unbind(card)
			if card.Type == 'Equipment' and args.faceups[0]:
				remove_eq_traits_from_mage(card)
			if card.baTraits not in ['','{}'] or card.bfaTraits not in ['','{}'] and card.isFaceUp:
				removeTraitsFromArena(card)
			if card.bMageTraits not in ['','{}'] and card.isFaceUp:
				removeFromMageTraits(card)

		if len(cards) == 1 and table in args.toGroups:
			for otherCard in table:
				if otherCard.Type in typeIgnoreList or otherCard.Name in typeIgnoreList or 'Magestats' in otherCard.Type or otherCard == card: continue
				overlap = comparePosition(otherCard,card)
				if overlap<400 and canBind(card, otherCard) and otherCard.Bindings in ['','[]']:
					c,t = bind(card, otherCard)
					if t:
						actionType = ['binds','to']
						hasAttached = True
						break
				elif overlap<400 and canAttach(card, otherCard) and card.isFaceUp:
					c,t = attach(card, otherCard)
					if t:
						actionType = ['attaches','to']
						hasAttached = True
						break
				else:
					card.Position = (args.xs,args.ys)
		if actionType:
			publicChatMsg("{} {} {} {} {}.".format(me,actionType[0],c,actionType[1],t))
	return

def onScriptedCardsMoved(args):
	'''args = 	player,			Player moving the cards
				cards, 			list of cards being moved
				fromGroups, 	original groups of the cards (Table, Spellbook, Discard Pile, etc)
				toGroups, 		new groups of the cards (Table, Spellbook, Discard Pile, etc)
				indexs,			original z indexes of cards
				xs,ys,			original x, y coords
				highlights,		original highlights
				markers,		original markers
				faceups			original face up statuses'''
	mute()
	setGlobalVariable("MoveCardArgs",str(args))
	cards = args.cards
	for card in cards:	
		if card.Type in typeIgnoreList or card.Name in typeIgnoreList or 'Magestats' in card.Type: return
		if card.controller == me and 'Spellbook' in args.fromGroups[0].name:#and table in args.toGroups:
			addDefaultTraits(card)
			bestowAttackSpell(card)
		if card.controller == me and table in args.toGroups and table in args.fromGroups:
			#Tinkering
			updateCardLocation(card, args.xs, args.ys, args.toGroups, args.fromGroups)
			updateCardsInZone(card)

	return


def splay(x,y,dVector = (1,0)):
	"""Returns coordinates x,y unless there is already a card at those coordinates,
	in which case it searches for the next open position in the direction defined by dVector.
	Now using recursion!"""
	for c in table:
		if c.controller == me and (x,y) == c.position:
			wKey,hKey = {True: ("width","height"), False: ("backWidth","backHeight")}[c.isFaceUp]
			w,h = cardSizes[c.size][wKey],cardSizes[c.size][hKey]
			dx,dy = dVector
			return splay(x+dx*w,y+dy*h,dVector)
	return x,y

def discard(card, x=0, y=0):
	mute()
	if card.controller != me:
		whisper("{} does not control {} - discard cancelled".format(me, card))
		return
	returnMarkers(card,{})#Need to rewrite this
	card.isFaceUp = True

	for marker in card.markers:
		card.markers[marker] = 0

	if eval(getGlobalVariable('adramelechWarlock')) and 'Enchantment' in card.Type and 'Curse' in card.Subtype and card.isAttachedTo:
		updateAdraCurse(card)

	if card.isAttachedTo:
		detach(card)

	elif card.isBoundTo:
		unbind(card)
	
	if card.Type == 'Equipment' and card.isFaceUp:
		remove_eq_traits_from_mage(card)
	
	if card.baTraits not in ['','{}'] or card.bfaTraits not in ['','{}']:
		removeTraitsFromArena(card)
	
	if card.bMageTraits not in ['','{}']:
		removeFromMageTraits(card)

	removeCardFromCurrentZone(card)
	
	removeBestowedAttack(card)

	if 'Cantrip' in card.nativeTraits:
		card.moveTo(me.piles['Spellbook'])
		notify('{} moves back to {}\'s spellbook because it has Cantrip'.format(card, card.controller))
	else:
		card.moveTo(me.piles['Discard Pile'])
		notify("{} discards {}.\n".format(me,card))
	return

def obliterate(card, x=0, y=0):
	mute()
	if card.controller != me:
		whisper("{} does not control {} - discard cancelled".format(me, card))
		return
	returnMarkers(card,{})#Need to rewrite this
	card.isFaceUp = True
	
	for marker in card.markers:
		card.markers[marker] = 0

	if card.isAttachedTo:
		detach(card)
	elif card.isBoundTo:
		unbind(card)
	
	if card.Type == 'Equipment' and card.isFaceUp:
		remove_eq_traits_from_mage(card)
	
	if card.baTraits not in ['','{}'] or card.bfaTraits not in ['','{}']:
		removeTraitsFromArena(card)
	
	if card.bMageTraits not in ['','{}']:
		removeFromMageTraits(card)

	removeCardFromCurrentZone(card)

	removeBestowedAttack(card)

	card.moveTo(me.piles['Obliterate Pile'])
	notify("{} obliterates {}.\n".format(me,card))
	return

def rotateCard(card, x = 0, y = 0):
	# Rot90, Rot180, etc. are just aliases for the numbers 0-3
	mute()
	if card.controller == me:
		card.orientation = (card.orientation + 1) % 4
		if card.isFaceUp:
			notify("{} Rotates {}\n".format(me, card.Name))
		else:
			notify("{} Rotates a card\n".format(me))