def onMarkerChanged(args):
    ''' args = 	
            card 			the card whose markers are changed
            marker, 	    the name of the marker being changed
            id, 		    the unique identifier of the marker being changed
            value,			the old value of the marker
            scripted,		string, true if the marker was changed via python'''
    
    debug('card: {}\n'.format(args.card))
    debug('marker: {}\n'.format(args.marker))
    debug('id: {}\n'.format(args.id))
    debug('value: {}\n'.format(args.value))
    debug('scripted: {}\n'.format(args.scripted))
    card = args.card
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or 'Magestats' in card.Type:
        return
    mageTokens = [BloodReaper, Pet, HolyAvenger, WoundedPrey, EternalServant,SirensCall]
    tokenDict = {
        "b3b6b5d3-4bda-4769-9bac-6ed48f7eb0fc":Armor,
        "50d83b50-c8b1-47bc-a4a8-8bd6b9b621ce":BloodReaper,
        "82df2507-4fba-4c81-a1de-71e70b9a16f5":Cripple,
        "86a71cf6-35ce-4728-a2f8-6701b1e29aa4":EternalServant,
        "c580e015-96ff-4b8c-8905-28688bcd70e8":Growth,
        "91ed27dc-294d-4732-ab71-37911f4011f2":Guard,
        "99381ac8-7d73-4d75-9787-60e6411d3613":HolyAvenger,
        "14a7b28a-7abc-4330-b139-c7939469df89":Light,
        "e96b3791-fbcf-40a2-9c11-106342703db9":Melee,
        "f4a2d3d3-4a95-4b9a-b899-81ea58293167":Pet,
        "cfb394b2-8571-439a-8833-476122a9eaa5":Ranged,
        "f7379e4e-8120-4f1f-b734-51f1bd9fbab9":Slam,
        "ad0e8e3c-c1af-47b7-866d-427f8908dea4":Sleep,
        "a01e836f-0768-4aba-94d8-018982dfc122":Stuck,
        "4bbac09e-a46c-42de-9272-422e8074533f":Stun,
        "c89baa9e-21c8-4f8c-8635-b258d5d80172":Suffocate,
        "72ee460f-adc1-41ab-9231-765001f9e08e":Veteran,
        "e0bb0e90-4831-43c6-966e-27c8dc2d2eef":RuneofShielding,
        "d10ada1f-c03b-4077-b6cb-c9667d6b2744":RuneofReforging,
        "c2a265f9-ad97-4976-a83c-78891a224478":RuneofPrecision,
        "b3dd4c8e-35a9-407f-b9c8-a0b0ff1d3f07":RuneofPower,
        "ae179c85-11ce-4be7-b9c9-352139d0c8f2":RuneofFortification,
        "ced2ce11-5e69-46a9-9fbb-887e96bdf805":Treebond,
    }
    traitDict = {
        "b3b6b5d3-4bda-4769-9bac-6ed48f7eb0fc":"{'Armor':qty}",
        "50d83b50-c8b1-47bc-a4a8-8bd6b9b621ce":"{'Bloodthirsty':2,'BloodReaper':True}",
        "82df2507-4fba-4c81-a1de-71e70b9a16f5":"{'Restrained':True}",
        "86a71cf6-35ce-4728-a2f8-6701b1e29aa4":"{'Piercing':1,'EternalServant':True}",
        "c580e015-96ff-4b8c-8905-28688bcd70e8":"{'Life':3*qty}",
        "91ed27dc-294d-4732-ab71-37911f4011f2":"{'Counterstrike':True}",
        "99381ac8-7d73-4d75-9787-60e6411d3613":"{'Life':5*qty,'HolyAvenger':True}",
        "14a7b28a-7abc-4330-b139-c7939469df89":"{'Light':1}",
        "e96b3791-fbcf-40a2-9c11-106342703db9":"{'Melee':qty}",
        "f4a2d3d3-4a95-4b9a-b899-81ea58293167":"{'Melee':qty, 'Life':3*qty, 'Armor':1}",
        "cfb394b2-8571-439a-8833-476122a9eaa5":"{'Ranged':qty}",
        "f7379e4e-8120-4f1f-b734-51f1bd9fbab9":"{'Incapacitated':True}",
        "ad0e8e3c-c1af-47b7-866d-427f8908dea4":"{'Incapacitated':True}",
        "a01e836f-0768-4aba-94d8-018982dfc122":"{'Restrained':True, 'Unmovable':True}",
        "4bbac09e-a46c-42de-9272-422e8074533f":"{'Incapacitated':True}",
        "c89baa9e-21c8-4f8c-8635-b258d5d80172":"{'Life':-2*qty}",
        "72ee460f-adc1-41ab-9231-765001f9e08e":"{'Melee':1,'Armor':qty}",
        "e0bb0e90-4831-43c6-966e-27c8dc2d2eef":"{'runeOfShielding':True}",
        "d10ada1f-c03b-4077-b6cb-c9667d6b2744":"{'runeOfReforging':True}",
        "c2a265f9-ad97-4976-a83c-78891a224478":"{'runeOfPrecision':True}",
        "b3dd4c8e-35a9-407f-b9c8-a0b0ff1d3f07":"{'runeOfPower':True}",
        "ae179c85-11ce-4be7-b9c9-352139d0c8f2":"{'Armor':1}",
        "ced2ce11-5e69-46a9-9fbb-887e96bdf805":"{'Armor':1, 'Life':4, 'Treebond':2}",
    }
    if args.id in tokenDict:
        qty = abs(card.markers[tokenDict[args.id]]-args.value)
        if card.markers[tokenDict[args.id]] > args.value and not (tokenDict[args.id] in mageTokens and 'Mage' in card.Subtype) and card.controller == me:
            debug('{}'.format(card))
            if card.name == 'Drown':
                card = Card(eval(card.isAttachedTo))
            currentTraits = getTokenTraits(card)
            newTokenTraits = eval(traitDict[args.id])
            traitParams = create_trait_params(currentTraits,newTokenTraits,'Token', card, 'Token',qty)
            update_traits(traitParams)
            if card.Type == 'Equipment' and card.controller == me:
                mage = getMage()
                currentMageTraits = getTokenTraits(mage)
                traitParams = create_trait_params(currentMageTraits,newTokenTraits,'Token', mage, 'Equipment Token',qty)
                update_traits(traitParams)
        elif card.markers[tokenDict[args.id]] < args.value and not (tokenDict[args.id] in mageTokens and 'Mage' in card.Subtype) and card.controller == me:
            currentTraits = getTokenTraits(card)
            remTokenTraits = eval(traitDict[args.id])
            traitParams = create_trait_params(currentTraits,remTokenTraits,'Token', card, 'Token',qty,True)
            update_traits(traitParams)
            if card.Type == 'Equipment' and card.controller == me:
                mage = getMage()
                currentMageTraits = getTokenTraits(mage)
                traitParams = create_trait_params(currentMageTraits,remTokenTraits,'Token', mage, 'Equipment Token',qty,True)
                update_traits(traitParams)
    debug('Marker: {}'.format(args.marker))
    if getRemainingLife(card) <1 and getGlobalVariable("GameSetup") == "True" and args.marker in ['Damage', 'Tainted', 'Freeze'] and not card.isDestroyed:
        debug('controller {}'.format(card.controller.name))
        remoteCall(card.controller, 'deathPrompt',[card])


    '''
        
        Freeze, 
        Invisible, 
        Runes, 
        SirenCall,
        Tainted
        Treebond
        Zombie'''
    return

def onCounterChanged(args):
    '''args = 	
            Player 			
            Counter, 	    
            value,			
            scripted,	'''	
    
    debug('Player: {}\n'.format(args.player))
    debug('Counter: {}\n'.format(args.counter.name))
    debug('value: {}\n'.format(args.value))
    debug('scripted: {}\n'.format(args.scripted))
    mage = getMage()
    if args.counter.name == 'Life' and not args.scripted:
        lifeChange = me.Life - args.value
        oldLife = eval(mage.Stat_Life)
        mage.Stat_Life = str(oldLife + lifeChange)
    elif args.counter.name == 'Channeling' and not args.scripted:
        channelChange = me.Channeling - args.value
        oldChannel = eval(mage.Stat_Channeling)
        mage.Stat_Channeling = str(oldChannel + channelChange)
    if getRemainingLife(mage) <1:
        remoteCall(mage.controller, 'deathPrompt',[mage])
    return


def toggleActionMarker(card, x=0, y=0): #x and y included because that's what OCTGN will send
    mute()
    myColor = int(me.getGlobalVariable("MyColor"))
    actionMarkerColorDict = {1:"ActionRed",2:"ActionBlue",3:"ActionGreen",4:"ActionPurple"}
    actionMarkerUsedColorDict = {1:"ActionRedUsed",2:"ActionBlueUsed",3:"ActionGreenUsed",4:"ActionPurpleUsed"}
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    checkSetupComplete(myColor)
    actionColor = eval(actionMarkerColorDict[myColor])
    actionColorUsed = eval(actionMarkerUsedColorDict[myColor])
    traits = getTraits(card)
    if card.markers[Slam]:
        flipSlam(card)
    if 'FPDS' in traits:
        addDamageAmount(card, 2)
        notify('The Five Point Death Strike takes its toll on {}.\n{} takes 2 damage'.format(card, card))
    if card.name == 'Alandell, the Blue Knight' and not timesHasOccurred('BuffAlandell',me) and card.markers[actionColor]:
        amount = min(askInteger('How much mana would you like to pay to buff Alandell?',0), 4)
        if amount >0 and me.Mana >= amount:
            me.Mana -= amount
            notify('{} spends {} to buff Alandell\'s attack'.format(me, amount))
            
            rememberPlayerEvent("BuffAlandell",me)

            EOATraits = getEOATraits(card)
            newEOATraits = {'Melee':amount, 'AlEffect':amount}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', card, card)
            update_traits(traitParams)

    if card.markers[actionColorUsed] > 0:
        card.markers[actionColor] = 1
        card.markers[actionColorUsed] = 0
        notify("{} readies Action Marker\n".format(card.Name))
    else:
        card.markers[actionColorUsed] = 1
        card.markers[actionColor] = 0
        notify("{} spends Action Marker\n".format(card.Name))
    return

def toggleReady(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[Ready] > 0:
		card.markers[Ready] = 0
		card.markers[Used] = 1
		notify("{} spends the Ready Marker on {}\n".format(me, card.Name))
	else:
		card.markers[Ready] = 1
		card.markers[Used] = 0
		notify("{} readies the Ready Marker on {}\n".format(me, card.Name))

def toggleGuard(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	toggleToken(card, Guard)

def toggleToken(card, tokenType):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative, Phase, and Vine Markers
	if card.markers[tokenType] > 0:
		card.markers[tokenType] = 0
		if card.isFaceUp:
			notify("{} removes a {} from {}\n".format(me, tokenType[0], card.Name))
		else:
			notify("{} removed from face-down card.\n".format(tokenType[0]))
	else:
		card.markers[tokenType] = 1
		if card.isFaceUp:
			notify("{} adds a {} token to {}\n".format(me, tokenType[0], card.Name))
		else:
			notify("{} added to face-down card.\n".format(tokenType[0]))

def toggleAirGlyph(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	mageDict = eval(me.getGlobalVariable("MageDict"))
	if card.markers[AirGlyphActive] > 0:
		card.markers[AirGlyphActive] = 0
		card.markers[AirGlyphInactive] = 1
		notify("{} deactivates the Air Glyph\n".format(me))
	elif card.markers[AirGlyphInactive] > 0:
		card.markers[AirGlyphInactive] = 0
		card.markers[AirGlyphActive] = 1
		notify("{} Activates the Air Glyph\n".format(me))
		
def toggleEarthGlyph(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	mageDict = eval(me.getGlobalVariable("MageDict"))
	if card.markers[EarthGlyphActive] > 0:
		card.markers[EarthGlyphActive] = 0
		card.markers[EarthGlyphInactive] = 1
		notify("{} deactivates the Earth Glyph\n".format(me))
	elif card.markers[EarthGlyphInactive] > 0:
		card.markers[EarthGlyphInactive] = 0
		card.markers[EarthGlyphActive] = 1
		notify("{} Activates the Earth Glyph\n".format(me))
		
def toggleFireGlyph(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	mageDict = eval(me.getGlobalVariable("MageDict"))
	if card.markers[FireGlyphActive] > 0:
		card.markers[FireGlyphActive] = 0
		card.markers[FireGlyphInactive] = 1
		notify("{} deactivates the Fire Glyph\n".format(me))
	elif card.markers[FireGlyphInactive] > 0:
		card.markers[FireGlyphInactive] = 0
		card.markers[FireGlyphActive] = 1
		notify("{} Activates the Fire Glyph\n".format(me))

def toggleWaterGlyph(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	mageDict = eval(me.getGlobalVariable("MageDict"))
	if card.markers[WaterGlyphActive] > 0:
		card.markers[WaterGlyphActive] = 0
		card.markers[WaterGlyphInactive] = 1
		notify("{} deactivates the Water Glyph\n".format(me))
	elif card.markers[WaterGlyphInactive] > 0:
		card.markers[WaterGlyphInactive] = 0
		card.markers[WaterGlyphActive] = 1
		notify("{} Activates the Water Glyph\n".format(me))

def toggleVoltaric(card, x=0, y=0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if card.markers[VoltaricON] > 0:
		card.markers[VoltaricON] = 0
		card.markers[VoltaricOFF] = 1
		notify("{} disables Voltaric shield\n".format(card.Name))
	else:
		if askChoice("Do you want to enable your Voltaric Shield by paying 2 mana?",["Yes","No"],["#171e78","#de2827"]) == 1:
			if me.Mana < 2:
				notify("{} has insufficient mana in pool\n".format(me))
				return
			me.Mana -= 2
			card.markers[VoltaricON] = 1
			card.markers[VoltaricOFF] = 0
			notify("{}  spends two mana to enable his Voltaric shield\n".format(me))
		else: notify("{} chose not to enable his Voltaric shield\n".format(me))



def checkSetupComplete(myColor):
    mute()
    if myColor == "0":
        whisper("Please perform player setup to initialize player color")
    return
    
def flipSlam(card):
    mute()
    choiceList = ['Yes', 'No']
    colorsList = ['#0000FF', '#FF0000']
    choice = askChoice("Would you like to flip the slam to a daze?", choiceList, colorsList)
    if choice == 1:
        card.markers[Slam] = 0
        card.markers[Daze] += 1
        notify("{}'s Slam turns to a daze\n".format(card.Name))
    else:
        notify("{}'s slam remains unchanged\n".format(card.Name))
    return

def toggleQuickMarker(card, x=0, y=0):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if card.markers[Quick] > 0:
        card.markers[Quick] = 0
        card.markers[QuickBack] = 1
        notify("{} spends Quickcast action\n".format(card.Name))
    else:
        card.markers[Quick] = 1
        card.markers[QuickBack] = 0
        notify("{} readies Quickcast Marker\n".format(card.Name))

def createVineMarker(group, x=0, y=0):
	mute()
	table.create("ed8ec185-6cb2-424f-a46e-7fd7be2bc1e0", x, y)
	notify("{} creates a Green Vine Marker.\n".format(me))

def addOther(card, x = 0, y = 0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	marker, qty = askMarker()
	if qty == 0:
		return
	card.markers[eval(marker[0])] += qty


def placeMarkersOnCard(card):
    mute()
    if card.spawnMarkers:
        propertyList = card.spawnMarkers.split(';')
        for property in propertyList:
            marker = property.split(',')[0]
            markerQty = property.split(',')[1]
            card.markers[eval(marker)] += int(markerQty)
    if card.Type == "Creature" and not "Mage" in card.Subtype : #places action marker on card
        toggleActionMarker(card)
    elif card.Type == "Creature" and "Mage" in card.Subtype:
        toggleActionMarker(card)
        toggleActionMarker(card) #Mages always start with an active action marker
        toggleQuickMarker(card)

def returnMarkers(card, cardTraitsDict):#NEED TO REWRITE
    mute()
    reusableAbilityTokens = [BloodReaper,
                            EternalServant,
                            HolyAvenger,
                            Pet]
                #reusableGeneralTokens = [Light]
    mage = getMage()
    for t in reusableAbilityTokens:
            if card.markers[t]: mage.markers[t] = 1 #Return mage ability markers to their owner.
    
    if card.markers[WoundedPrey]:
            mages = [m for m in table if m.Name == "Johktari Beastmaster" and not m.markers[WoundedPrey]] #WARNING: This may identify the wrong JBM if there are more than 1 in the match. Unfortunately, markers cannot be associated with players, so it is difficult to correctly reassign the marker (not impossible, just not worth the effort)
            if mages:
                    mage = mages[0]
                    mage.markers[WoundedPrey] = 1
    if card.markers[DivineChallenge]:
            mages = [m for m in table if m.Name == "Paladin" and not m.markers[DivineChallenge]] #
            if mages:
                    mage = mages[0]
                    mage.markers[DivineChallenge] = 1
    if card.markers[SirensCall]:
            mages = [m for m in table if m.Name == "Siren" and not m.markers[SirensCall]] #
            if mages:
                    mage = mages[0]
                    mage.markers[SirensCall] = 1
    if card.markers[Light]:
            for card in table:
                if card.Name == "Malakai\'s Basilica" and not card.markers[Light]:
                    card.markers[Light] = 1
    if card.markers[scoutToken]:
            for card in table:
                if card.Name == "Straywood Scout" and not card.markers[scoutToken]:
                    card.markers[scoutToken] = 1
    return

def addToken(card, tokenType):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative, Phase, and Vine Markers
    card.markers[tokenType] += 1
    if card.isFaceUp:
        notify("{} added to {}\n".format(tokenType[0], card.Name))
    else:
        notify("{} added to face-down card.\n".format(tokenType[0]))
    return

def subToken(card, tokenType):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return  # do not place markers/tokens on table objects like Initative, Phase, and Vine Markers
    if card.markers[tokenType] > 0:
        card.markers[tokenType] -= 1
        if card.isFaceUp:
            notify("{} removed from {}\n".format(tokenType[0], card.Name))
        else:
            notify("{} removed from face-down card.\n".format(tokenType[0]))
    return

def addDamage(card, x = 0,y = 0):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if "Mage" in card.Subtype and card.controller == me:
            me.Damage += 1
            notify('Damage added to {}'.format(card))
    else:
            card.markers[Damage] += 1
            notify('Damage added to {}'.format(card))
            

def addDamageAmount(card,amount = 1):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if "Mage" in card.Subtype and card.controller == me:
            me.Damage += amount
            return amount
    else:
            card.markers[Damage] += amount
            return amount

def subDamage(card, x = 0, y = 0):
	mute()
	if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
	if "Mage" in card.Subtype and card.controller == me:
			me.Damage -= 1
	else:
			card.markers[Damage] -= 1
			notify("{} removes {} damage from {}\n".format(me, '1', card.Name))

def subDamageAmount(card,amount = 1):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if "Mage" in card.Subtype and card.controller == me:
        me.Damage = max((me.Damage - amount),0)
    else:
        card.markers[Damage] = max(card.markers[Damage] - amount,0)	

def addMana(card, amount = 1):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if "Mage" in card.Subtype and card.controller == me:
            me.Mana += amount
    else:
            card.markers[Mana] += amount

def addManaMarker(card, x = 0, y = 0):
    mute()
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList or not card.isFaceUp: return
    if "Mage" in card.Subtype and card.controller == me:
            me.Mana += 1
            notify("{} increases their mana supply by 1".format(me))
    else:
        card.markers[Mana] += 1
        notify("{} adds mana to {}".format(me, card))

def returnFermataMarker(mageStatsID, marker):
    mute()
    if marker in ['FermataBlue1', 'FermataBlue2']:
        Card(mageStatsID).markers[FermataBlue1] = 1
    elif marker in ['FermataGreen1', 'FermataGreen2']:
        Card(mageStatsID).markers[FermataGreen1] = 1
    return

def incrementFermataMarker(card):
    mute()
    if card.markers[FermataBlue1] == 1:
        card.markers[FermataBlue1] = 0
        card.markers[FermataBlue2] = 1
    elif card.markers[FermataGreen1] == 1:
        card.markers[FermataGreen1] = 0
        card.markers[FermataGreen2] = 1

def transferFermataMarker(card, mageStatsID):
    mute()
    if Card(mageStatsID).markers[FermataBlue1] == 1:
        card.markers[FermataBlue1] = 1
        Card(mageStatsID).markers[FermataBlue1] = 0
    elif Card(mageStatsID).markers[FermataGreen1] == 1:
        card.markers[FermataGreen1] = 1
        Card(mageStatsID).markers[FermataGreen1] = 0
    return

def fermataMarkersFound(card):
    mute()
    for marker in ['FermataBlue1', 'FermataGreen1', 'FermataBlue2', 'FermataGreen2']:
        if card.markers[eval(marker)]:
            return True
    return False

def adjustEffects(attacker, defender, actualEffect):
    defTraits = getTraits(defender)
    #debug('adjustEffects')
    for effect in actualEffect:
        #debug('effect: {}'.format(effect))
        adjustedEffects = removeIllegalEffects(effect, defTraits, defender, actualEffect)
    if 'Corrode' in adjustedEffects:
        adjustedEffects = swapCorrode(defender, defTraits, adjustedEffects, effect)
        #debug(str(adjustedEffects))
    return adjustedEffects

def removeIllegalEffects(effect, defTraits, defender, actualEffect):
    illegalEffect = False
    adjustedEffects = actualEffect
    conditionTypes = {'Burn' : 'Flame',
                        'Sleep': 'Psychic',
                        'Corrode': 'Acid',
                        'Rot': 'Poison', 
                        'Cripple': 'Poison',
                        'Tainted': 'Poison',
                        'Weak': 'Poison'}
    if 'Immunity' in defTraits:
        for immunity in defTraits['Immunity']:
            #debug(immunity)
            if effect in conditionTypes:
                if conditionTypes[effect] == immunity:
                    illegalEffect = True
    if ((effect == 'Burn' and defTraits.get('Burnproof')) or
            (effect in ['Snatch', 'Push'] and defTraits.get('Unmovable')) or
            (effect == 'Bleed' and (not defTraits.get('Living') or 'Plant' in defender.Subtype)) or
            (effect in ['Bleed', 'Stuck', 'Stun', 'Daze', 'Cripple', 'Weak', 'Slam', 'Stagger'] and defender.Type != 'Creature')):
                illegalEffect = True
    if illegalEffect:
        adjustedEffects.remove(effect)
    return adjustedEffects

def swapCorrode(defender, defTraits, adjustedEffects, effect):
    #debug('swapCorrode')
    armor = computeDefenderArmor(defender, defTraits)
    armor -= defender.markers[Corrode]
    for i in range(len(adjustedEffects)):
        if armor == 0:
            adjustedEffects[i] = 'Damage'
        else:
            armor -=1
    return adjustedEffects

def applyEffects(attacker, defender, actualEffect):
    mute()
    """'effects':{7: ['Push'], 11: ['Push', 'Daze']}"""
    effects = actualEffect
    #debug('Effects: {}'.format(str(effects)))
    conditionsList = ['Bleed','Burn','Corrode','Cripple','Damage','Daze','Freeze', 'Grapple','Rot','Slam','Sleep','Stagger','Stuck','Stun','Tainted','Weak']
    effectsInflictDict = {'Damage' : "suffers 1 point of direct damage! (+1 Damage)",
                            'Bleed' : 'bleeds from its wounds! (+1 Bleed)',
                            'Burn' : 'is set ablaze! (+1 Burn)',
                            'Corrode' : 'corrodes! (+1 Corrode)',
                            'Cripple' : 'is crippled! (+1 Cripple)',
                            'Daze' : 'is dazed! (+1 Daze)',
                            'Freeze': 'Freezes! (+1 Freeze)',
                            'Grapple': 'is Grappled! (+1 Grapple)',
                            'Rot' : 'rots! (+1 Rot)',
                            'Slam' : 'is slammed to the ground! (+1 Slam)',
                            'Sleep' : 'falls fast alseep! (+1 Sleep)',
                            'Stagger' : 'staggers about, not quite sure what is going on! (+1 Stagger)',
                            'Stuck' : 'is stuck fast! (+1 Stuck)',
                            'Stun' : 'is stunned! (Stun)',
                            'Tainted' : "'s wounds fester! (+1 Tainted)",
                            'Weak' : 'is weakened! (+1 Weak)',
                            'Snatch' : 'is snatched toward {}! (Snatch)'.format(attacker),
                            'Push' : 'is pushed away from {}! (Push 1)'.format(attacker),
                            'Taunt' : 'wants to attack {}! (Taunt)'.format(attacker)}
    for e in effects:
        #debug('e: {}'.format(str(e)))
        if e in conditionsList:
            if e == "Damage" and "Mage" in defender.Subtype: 
                defender.controller.damage += 1
            else: 
                defender.markers[eval(e)]+=1
        notify('{} {}\n'.format(defender.Name,effectsInflictDict.get(e,'is affected by {}!'.format(e))))
    return

def toggleDeflect(card, x=0, y=0):
	mute()
	if card.markers[DeflectR] > 0:
		card.markers[DeflectR] = 0
		card.markers[DeflectU] = 1
		notify("{} uses deflect\n".format(card.Name))
	else:
		card.markers[DeflectR] = 1
		card.markers[DeflectU] = 0
		notify("{} readies deflect\n".format(card.Name))


def give_paladin_valor(attacker, defender):
    strongest = determine_strongest_enemy()
    if (defender in strongest or (not strongest and 'Mage' in defender.Subtype)):
        rememberPlayerEvent("Valor",attacker.controller)
        attacker.markers[Valor] += 1