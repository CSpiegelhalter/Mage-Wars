def constructZoneMap(I, J, tilesize):
    mute()
    gameMode = getGlobalVariable("GameMode")
    if gameMode == 'Arena':
        ZoneArray = [[1 for j in range(J)] for i in range(I)]
    mapDict = createMapDict(I, J, ZoneArray, tilesize)
    mapDict.get('zoneArray')[0][0]['startLocation'] = '1'
    mapDict.get('zoneArray')[-1][-1]['startLocation'] = '2'
    mapDict["RDA"] = (2,2) 
    setGlobalVariable("Map", str(mapDict))
    return

def createMapDict(I,J,zoneArray,tileSize):
    mapDict = {'Horizontal Zone Dimension' : I,
                'Vertical Zone Dimension' : J,
                'tileSize' : tileSize,
                'minx' : -tileSize*I/2,
                'miny' : -tileSize*J/2,
                'X' : tileSize*I,
                'Y' : tileSize*J}
    array = list(zoneArray)
    zoneList = []
    zoneNameIndex = 1
    for i in range(I):
        for j in range(J):
            z = (createZone(i,j,mapDict['minx'],mapDict['miny'],mapDict['tileSize'], zoneNameIndex) if zoneArray[i][j] else {})
            zoneNameIndex +=1
            array[i][j] = z
            if z: zoneList.append(z)
    mapDict['zoneArray'] = array
    mapDict['zoneList'] = zoneList
    return mapDict

def createZone(i,j,mapX,mapY,size,zoneNameIndex):
    return  {'Horizontal Zone Index' : i,
                'Vertical Zone Index' : j,
                'x' : mapX+i*size,
                'y' : mapY+j*size,
                'size' : size,
                'Name' : str(zoneNameIndex),
                'cardsInZone' : []}

def getZoneContaining(card): #convoluted, can be reworked someday
    if not getGlobalVariable("Map"): return
    mapDict = eval(getGlobalVariable("Map"))
    x,X,y,Y = mapDict.get('minx'),mapDict.get('X'),mapDict.get('miny'),mapDict.get('Y')
    tileSize = mapDict.get('tileSize')
    zoneArray = mapDict.get('zoneArray')
    zoneList = mapDict.get('zoneList')
    cx,cy = card.position
    cX,cY = (card.width,card.height)
    if not (x<cx+cX/2<x+X and y<cy+cY/2<y+Y): return None
    i,j = int(float(cx+cX/2-x)/tileSize),int(float(cy+cY/2-y)/tileSize)
    if zoneArray[i][j]: 
        zoneName = zoneArray[i][j]['Name']
        return zoneList[int(zoneName)-1]

def getCardFormerZone(card, xs, ys):#convoluted, can be reworked someday
    if not getGlobalVariable("Map"): return
    mapDict = eval(getGlobalVariable("Map"))
    x,X,y,Y = mapDict.get('minx'),mapDict.get('X'),mapDict.get('miny'),mapDict.get('Y')
    tileSize = mapDict.get('tileSize')
    zoneArray = mapDict.get('zoneArray')
    zoneList = mapDict.get('zoneList')
    cx = xs[0]
    cy = ys[0]
    cX,cY = (card.width,card.height)
    if not (x<cx+cX/2<x+X and y<cy+cY/2<y+Y): return None
    i,j = int(float(cx+cX/2-x)/tileSize),int(float(cy+cY/2-y)/tileSize)
    if zoneArray[i][j]: 
        zoneName = zoneArray[i][j]['Name']
        return zoneList[int(zoneName)-1]

def getZoneFromAttr(card, attr):
    if getattr(card, attr):
        zoneIndex = int(getattr(card, attr))-1
        mapDict = eval(getGlobalVariable("Map"))
        zone = mapDict['zoneList'][zoneIndex]
        return zone
    else:
        return False


def cardGetDistance(card1,card2):
    zone1 = getZoneContaining(card1)
    zone2 = getZoneContaining(card2)
    return zoneGetDistance(zone1,zone2)

def zoneGetDistance(zone1,zone2):
    return abs(zone1['Horizontal Zone Index']-zone2['Horizontal Zone Index']) + abs(zone1['Vertical Zone Index']-zone2['Vertical Zone Index'])

def updateZone(zone):
    mapDict = eval(getGlobalVariable('Map'))
    index = int(zone['Name'])-1  
    mapDict['zoneList'][index] = zone
    setGlobalVariable("Map",str(mapDict))
    return

def updateCardLocation(card, xs, ys, toGroups, fromGroups):
    if table in fromGroups:
        formerZone = getCardFormerZone(card, xs, ys)
        card.formerZone = formerZone['Name'] if formerZone else ''
    if table in toGroups:
        currentZone = getZoneContaining(card)
        card.currentZone = currentZone['Name'] if currentZone else ''
    return

def updateCardsInZone(card):#TODO Refactor
    formerZone = card.formerZone
    currentZone = card.currentZone
    sameZone = formerZone == currentZone
    traitsToAdd = {}
    #debug('updateCardsInZone')
    #debug('Current Zone: {}'.format(currentZone))
    #debug('former Zone: {}'.format(formerZone))
    #debug('sameZone: {}'.format(sameZone))
    if currentZone and not sameZone:
        addCardToCurrentZone(card)
        if (card.zTraits not in ['','{}'] or card.zfTraits not in ['','{}']):
            #debug('found a zone trait in the moving card')
            addTraitsToZone(card)
        zTraitList = checkForCardsWithZoneTraits(card)
        zfTraitList = checkForCardsWithFriendlyZoneTraits(card)
        traitsToAdd = combineZTraitsToAdd(zTraitList, zfTraitList)
        if len(zTraitList) > 0:
            #debug('found a zone trait in the new zone')
            for target in zTraitList:
                newZoneTraits = eval(target.zTraits)
                currentTraits = getZoneTraits(card)
                traitParams = create_trait_params(currentTraits,newZoneTraits,'Zone', card, target)
                update_traits(traitParams)
        if len(zfTraitList) > 0:
            #debug('found a friendly zone trait in the new zone')
            for target in zfTraitList:
                if card.controller == target.controller:
                    newZoneTraits = eval(target.zfTraits)
                    currentTraits = getZoneTraits(card)
                    traitParams = create_trait_params(currentTraits,newZoneTraits,'Zone', card, target)
                    update_traits(traitParams)

    if formerZone and not sameZone:
        zone = getZoneFromAttr(card, 'formerZone')
        oldzTraitList = checkForCardsWithZoneTraits(card, zone)
        oldzfTraitList = checkForCardsWithFriendlyZoneTraits(card, zone)
        traitsToRemove = combineZTraitsToRemove(oldzTraitList, oldzfTraitList)
        if traitsToAdd:
            traitsToRemove = compareTraitsToAdd(traitsToAdd, traitsToRemove)
        
        removeCardFromOldZone(card)
        
        if (card.zTraits not in ['','{}'] or card.zfTraits not in ['','{}']):
            removeTraitsFromOldZone(card)
        
        if len(oldzTraitList) > 0 and traitsToRemove:
            for target in oldzTraitList:
                currentTraits = getZoneTraits(card)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',card,target,0,True)
                update_traits(traitParams)

        if len(oldzfTraitList) > 0 and traitsToRemove:
            for target in oldzfTraitList:
                currentTraits = getZoneTraits(card)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',card,target,0,True)
                update_traits(traitParams)
    return 

def addCardToCurrentZone(card):
    zone = getZoneFromAttr(card, 'currentZone')
    if card._id not in zone['cardsInZone']:
        #debug('adding to current zone ({})'.format(zone['Name']))
        zone['cardsInZone'].append(card._id)
        updateZone(zone)
    return

def removeCardFromOldZone(card):
    mute()
    #debug('removing from former')
    zone = getZoneFromAttr(card, 'formerZone')
    if zone:    
        if card._id in zone['cardsInZone']:
            zone['cardsInZone'].remove(card._id)
            updateZone(zone)
    return

def removeCardFromCurrentZone(card):
    zone = getZoneFromAttr(card, 'currentZone')
    if zone:    
        if card.zTraits not in ['', '{}']:
            #debug('removing zTraits: {}'.format(card.zTraits))
            removeTraitsFromCurrentZone(card)
        if card.zfTraits not in ['', '{}']:
            removeTraitsFromCurrentZone(card)
        if card._id in zone['cardsInZone']:
            zone['cardsInZone'].remove(card._id)
            updateZone(zone)
    return

def comparePosition(otherCard, card):
    '''#debug('comparePosition')
    #debug('card: {}'.format(card))
    #debug('otherCard: {}'.format(otherCard))'''
    return (otherCard.position[0] - card.position[0])**2 + (otherCard.position[1]-card.position[1])**2

def getAllCardsInZoneList(card, zone = None):
    #debug('get all cards in zone list')
    if not zone:
        zone = getZoneFromAttr(card,'currentZone')
    cardsInZone = []
    for cardID in zone['cardsInZone']:
        cardsInZone.append(Card(cardID))
    return cardsInZone

def getAllCardIDsInZoneList(card, zone = None):
    #debug('get all cards in zone list')
    if not zone:
        zone = getZoneFromAttr(card,'currentZone')
    cardsInZone = []
    for cardID in zone['cardsInZone']:
        cardsInZone.append(cardID)
    return cardsInZone

def getOtherCardsInZoneList(card, zone = None):
    #debug('get other cards in zone list')
    cardList = getAllCardsInZoneList(card, zone)
    for eachCard in cardList:
        if eachCard == card:
            cardList.remove(card)
    return cardList

def getOtherCardIDsInZoneList(card, zone = None):
    #debug('get other cards in zone list')
    cardList = getAllCardIDsInZoneList(card, zone)
    for eachCard in cardList:
        if eachCard == card._id:
            cardList.remove(card._id)
    return cardList

def filter_for_creatures_and_conjurations(targets):
    filteredTargets = []
    for target in targets:
        if Card(target).Type in ['Creature','Conjuration'] and Card(target).Stat_Life !='':
            filteredTargets.append(target)
    return filteredTargets

def zoneGetContain(zone,card): # Finds the closest straight-line place to move the object so it is contained.
	x,y = card.position
	X,Y = card.width,card.height
	coordinates = [x,y]
	if (x <= zone.get('x')): coordinates[0] = zone.get('x') + 1
	if (x + X >= zone.get('x')+zone.get('size')): coordinates[0] = zone.get('x') + zone.get('size') - X - 1
	if (y <= zone.get('y')): coordinates[1] = zone.get('y') + 1
	if (y + Y >= zone.get('y')+zone.get('size')): coordinates[1] = zone.get('y') + zone.get('size') - Y - 1
	return (coordinates[0],coordinates[1])

def zoneGetBorder(zone,card): #like getContain, but for borders. Snaps to the nearest border.
	x,y = card.position
	X,Y = card.width,card.height
	borders = [[(zone['x']),(zone['y'] + zone['size']/2)],
			   [(zone['x'] + zone['size']/2),(zone['y'])],
			   [(zone['x'] + zone['size']),(zone['y'] + zone['size']/2)],
			   [(zone['x'] + zone['size']/2),(zone['y'] + zone['size'])]]
	c = [x+X/2,y+Y/2]
	border = borders[0]
	for b in list(borders):
		if (abs(b[0]-c[0]) + abs(b[1]-c[1])) < (abs(border[0]-c[0]) + abs(border[1]-c[1])): border = b
	return (border[0]-X/2,border[1]-Y/2)

def snapToZone(card):
    mute()
    zone = getZoneFromAttr(card, 'currentZone')
    if zone:
        if 'Mage' in card.Subtype:
            snapX,snapY = zoneGetContain(zone,card)
            card.moveToTable(snapX,snapY)
        elif eval(card.Cast_Target).get('Zone') or not card.isFaceUp: #snap to zone
            snapX,snapY = zoneGetContain(zone,card)
            card.moveToTable(snapX,snapY)
        elif card.type == 'Conjuration-Wall': #snap to zone border
            snapX,snapY = zoneGetBorder(zone,card)
            card.moveToTable(snapX,snapY)
    return

def check_tundra_range(card):
    tundraList = get_all_cards_of_name('Frozen Tundra')
    zone = getZoneContaining(card)
    if tundraList and zone:
        for tundra in tundraList:
            if tundra.isFaceUp:
                distance = cardGetDistance(card, tundra)
                if distance < 2:
                    return True
    return False