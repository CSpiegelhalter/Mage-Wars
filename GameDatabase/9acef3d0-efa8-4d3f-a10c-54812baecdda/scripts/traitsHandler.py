def getTraits(card):
    nativeTraits = getNativeTraits(card)
    attachedTraits = getAttachedTraits(card)
    tokenTraits = getTokenTraits(card)
    equipmentTraits = getEquipmentTraits(card)
    zoneTraits = getZoneTraits(card)
    arenaTraits = getArenaTraits(card)
    tempTraits = getTempTraits(card)
    EOATraits = getEOATraits(card)
    traits = getCombinedTraits(nativeTraits, [attachedTraits, tokenTraits, equipmentTraits,zoneTraits,arenaTraits, tempTraits, EOATraits])
    return traits

def getNativeTraits(card):
    #debug('native')
    if card.nativeTraits == '':
        nativeTraits = {}
    else:
        nativeTraits = eval(card.nativeTraits)
    return nativeTraits

def getAttachedTraits(card):
    #debug('attached')
    if card.attachedTraits == '':
        attachedTraits = {}
    else:
        attachedTraits = eval(card.attachedTraits) 
    return attachedTraits

def getTokenTraits(card):
    #debug('token')
    #debug(card)
    if card.tokenTraits == '':
        tokenTraits = {}
    else:
        tokenTraits = eval(card.tokenTraits)
    #debug(str(tokenTraits))
    return tokenTraits

def getEquipmentTraits(card):
    #debug('equipment')
    if card.equipmentTraits == '':
        equipmentTraits = {}
    else:
        equipmentTraits = eval(card.equipmentTraits)
    return equipmentTraits

def getZoneTraits(card):
    #debug('zone')
    if card.zoneTraits == '':
        zoneTraits = {}
    else:
        zoneTraits = eval(card.zoneTraits)
    return zoneTraits

def getArenaTraits(card):
    #debug('arena')
    if card.arenaTraits == '':
        arenaTraits = {}
    else:
        arenaTraits = eval(card.arenaTraits)
    return arenaTraits

def getTempTraits(card):
    #debug('Temp')
    if card.tempTraits == '':
        tempTraits = {}
    else:
        tempTraits = eval(card.tempTraits)
    return tempTraits

def getEOATraits(card):
    #debug('Temp')
    if card.EOATraits == '':
        tempTraits = {}
    else:
        tempTraits = eval(card.EOATraits)
    return tempTraits

def getCombinedTraits(baseTraits, traitList):
    #debug('combined')
    superlativeTraits = [   
                            "Regenerate",
                            "Aegis",
                        ]
    for addedTraits in traitList:
        for key in addedTraits:
            if key in baseTraits:
                if type(baseTraits[key]) == int and key not in superlativeTraits:
                    baseTraits[key]+=addedTraits[key]
                elif key in superlativeTraits:
                    baseTraits[key] += (addedTraits[key])
                    baseTraits[key].sort(reverse=True)
                elif type(baseTraits[key]) == bool:
                    baseTraits[key] = addedTraits[key]
            else:
                baseTraits[key] = addedTraits[key]
    return baseTraits

def addToTraits(card, traits, bTraits, qty = 0):#TODO This will need refactored
    #debug('adding to Traits')
    #debug('card: {}'.format(card))
    #debug('traits: {}'.format(bTraits))
    if 'Magestats' in card.Type or 'Swarm' in card.Subtype:
        return
    updateParams = {"card":card,"traits":traits,"bTraits":bTraits}
    for key in bTraits:
        updateParams['key'] = key
        if key in traits:
            updateParams = determine_trait_to_add(updateParams)
        else:
            updateParams = determine_new_trait_to_add(updateParams)
    traits = updateParams['traits']
    return traits

def update_traits(traitParams):
    '''traitParams{
        "Target"                :   Card()      #the Card() to update
        "Type of traits"        :   string      #the trait storage property of the card (ex: 'Attached' = card.attachedTraits)
        'Current traits'        :   dict        #the dict of the current traits 
        "Traits to be adjusted" :   dict        #the dict of the new traits to be added (ex: eval(card.bTraits))
        "Source"                :   Card, token #card or token from which the traits to be added came
        "Qty"                   :   int         #only used when dealing with tokens (quantity of tokens)
        "Remove"                :   Bool        #Used to tell whether we're adding or removing
    }'''
    #traitParams = {'Target':target,'Type of traits':'Attached', 'Traits to be adjusted':newAttachedTraits,'Source':card,'Qty':0}
    determine_property_to_adjust(traitParams)
    #debug('traitParams:{}'.format(str(traitParams)))
    update_life_channeling(traitParams.get('Target'))
    return

def update_life_channeling(card):
    if 'Creature' in card.Type or 'Conjuration' in card.Type:
        debug('update_life_channeling for {}'.format(card))
        adjust_channeling(card)
        adjust_life_total(card)
    return

def determine_property_to_adjust(traitParams):
    prop_op = {
        'Attached'  :set_attached_traits,
        'Equipment' :set_equipment_traits,
        'Zone'      :set_zone_traits,
        'Arena'     :set_arena_traits,
        'Token'     :set_token_traits,
        'Temp'      :set_temp_traits,
        'EOA'       :set_EOA_traits
    }
    if traitParams.get('Remove'):
        traitStr = combine_rem_trait_str(traitParams)
        #debug('dpta traitStr: {}'.format(traitStr))
    else:
        traitStr = combine_trait_str(traitParams)
        #debug('dpta2 traitStr: {}'.format(traitStr))
    traitParams['traitStr'] = traitStr
    chosen_prop_op = prop_op.get(traitParams.get('Type of traits'))
    return chosen_prop_op(traitParams)

def combine_trait_str(traitParams):
    updateParams = {
        "card":traitParams.get('Target'),
        "traits":traitParams.get('Current traits'),
        "newTraits":traitParams.get('Traits to be adjusted')
        }
    for key in updateParams.get('newTraits'):
        updateParams['key'] = key
        if key in updateParams.get('traits'):
            updateParams = determine_trait_to_add(updateParams)
        else:
            updateParams = determine_new_trait_to_add(updateParams)
    traits = updateParams['traits']
    return str(traits)

def combine_rem_trait_str(traitParams):
    updateParams = {
        "card":traitParams.get('Target'),
        "traits":traitParams.get('Current traits'),
        "newTraits":traitParams.get('Traits to be adjusted')
        }
    for key in updateParams.get('newTraits'):
        updateParams['key'] = key
        #debug(str(updateParams))
        if key in updateParams.get('traits'):
            if type(updateParams.get('traits')[key]) == int:
                #debug(str(updateParams))
                updateParams = lower_current_trait(updateParams)
            else:
                updateParams = determine_trait_to_remove(updateParams)
    traits = updateParams['traits']
    return str(traits)

def determine_trait_to_add(updateParams):
    trait_op = {
        'Discount':adjust_discount_list,
        'Defense':adjust_defense_list
    }
    chosen_trait_op = trait_op.get(updateParams['key'], add_to_current_trait)
    return chosen_trait_op(updateParams)

def determine_new_trait_to_add(updateParams):
    trait_op = {
        "Treebond"      :   add_treebond_to_traits,
        "ShallowSea"    :   add_shallow_sea_to_traits_special_case,
        "LifeTree"      :   add_life_tree_life
    }
    chosen_trait_op = trait_op.get(updateParams['key'], add_new_trait)

    return chosen_trait_op(updateParams)

def add_new_trait(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    traits[key]=bTraits[key]
    updateParams['traits'] = traits
    return updateParams

def add_to_current_trait(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    superlativeTraits = [   
                            "Regenerate",
					        "Aegis",
	                    ]
    if type(traits[key])==int and key not in superlativeTraits:
        traits[key]+=bTraits[key]
    elif type(traits[key]) == int and key in superlativeTraits:
        traits[key] += (bTraits[key])
        traits[key].sort(reverse = True)
    updateParams['traits'] = traits
    return updateParams

def add_treebond_to_traits(updateParams):##############
    card = updateParams['card']
    if card.controller == me:
        mage = getMage()
        arenaMageTraits = getArenaTraits(mage)
        newArenaTraits = {'Life':4}
        traitParams = create_trait_params(arenaMageTraits,newArenaTraits,'Arena', mage, card)
        update_traits(traitParams)
    updateParams = add_new_trait(updateParams)
    return updateParams

def add_shallow_sea_to_traits_special_case(updateParams):
    if ('Siren' in updateParams['card'].name or 'Naiya' in updateParams['card'].name):
        tempParams = {
            'card':updateParams['card'],
            'traits':updateParams['traits'],
            'key':'ChannelBoost',
            'newTraits':{'ChannelBoost':1}
        }
        tempParams = add_new_trait(tempParams)
        updateParams['traits'] = tempParams['traits']
    # if ('Naiya' in updateParams['card'].name):
    #     tempParams = {
    #         'card':updateParams['card'],
    #         'traits':updateParams['traits'],
    #         'key':'Regenerate',
    #         'newTraits':{'Regenerate':[1]}
    #     }
    #     tempParams = add_new_trait(tempParams)
    #     updateParams['traits'] = tempParams['traits']
    updateParams = add_new_trait(updateParams)
    return updateParams

def add_life_tree_life(updateParams):
    card = updateParams.get('card')
    #debug(card.name)
    traits = getTraits(card)
    if traits.get('Living') and card.name != "Etherian Lifetree":
        tempParams = {
            'card':updateParams['card'],
            'traits':updateParams['traits'],
            'key':'Life',
            'newTraits':{'Life':2}
        }
        tempParams = add_new_trait(tempParams)
        updateParams['traits'] = tempParams['traits']
    updateParams = add_new_trait(updateParams)
    return updateParams

def adjust_discount_list(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    discountList =traits[key]
    discountList+= bTraits[key]
    traits[key] = discountList
    updateParams['traits'] = traits
    return updateParams

def adjust_defense_list(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    traits[key]+=bTraits[key]
    updateParams['traits'] = traits
    return updateParams

def set_attached_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.attachedTraits = newTraitStr
    return

def set_equipment_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.equipmentTraits = newTraitStr
    return

def set_zone_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.zoneTraits = newTraitStr
    return

def set_arena_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.arenaTraits = newTraitStr
    return

def set_temp_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.tempTraits = newTraitStr
    return

def set_EOA_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.EOATraits = newTraitStr
    return

def addToMageTraits(card): 
    mage = getMage()
    currentTraits = getArenaTraits(mage)
    newArenaTraits = eval(card.bMageTraits)
    traitParams = create_trait_params(currentTraits,newArenaTraits,'Arena', mage, card)
    update_traits(traitParams)
    return

def set_token_traits(traitParams):
    card = traitParams.get('Target')
    newTraitStr = traitParams.get('traitStr')
    card.tokenTraits = newTraitStr
    return

def create_trait_params(currentTraits, newTraits, type, target, source, qty = 0,remove = False):
    traitParams = {
            'Target':target,
            'Type of traits':type, 
            'Current traits':currentTraits, 
            'Traits to be adjusted':newTraits,
            'Source':source,
            'Qty':qty,
            'Remove':remove}
    return traitParams

def determine_trait_to_remove(updateParams):
    trait_op = {
        'Discount':remove_from_discount_list,
        'Defense':remove_from_defense_list,
        "ShallowSea":remove_shallow_sea_from_traits_special_case,
        'Treebond':remove_treebond_from_traits,
        'LifeTree':remove_life_tree_life
    }
    chosen_trait_op = trait_op.get(updateParams['key'], remove_current_trait)
    return chosen_trait_op(updateParams)

def lower_current_trait(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    traits[key]-=bTraits[key]
    if traits[key]==0:
        traits.pop(key,None)
    updateParams['traits'] = traits
    return updateParams

def remove_current_trait(updateParams):
    traits = updateParams['traits']
    key = updateParams['key']
    traits.pop(key, None)
    updateParams['traits'] = traits
    return updateParams

def remove_from_defense_list(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    traits[key].remove(bTraits[key][0])
    updateParams['traits'] = traits
    return updateParams

def remove_from_discount_list(updateParams):
    traits = updateParams['traits']
    bTraits = updateParams['newTraits']
    key = updateParams['key']
    discountList = [traits[key]]
    discountList.remove(bTraits[key])
    if not discountList:
        traits.pop(key, None)
    else:
        traits[key] = str(discountList).strip('[]')
    updateParams['traits'] = traits
    return updateParams

def remove_shallow_sea_from_traits_special_case(updateParams):
    if ('Siren' in updateParams['card'].name or 'Naiya' in updateParams['card'].name):
        tempParams = {
            'card':updateParams['card'],
            'traits':updateParams['traits'],
            'key':'ChannelBoost',
            'newTraits':{'ChannelBoost':0}
        }
        tempParams = remove_current_trait(tempParams)
        updateParams['traits'] = tempParams['traits']
    updateParams = remove_current_trait(updateParams)
    return updateParams

def remove_life_tree_life(updateParams):
    card = updateParams.get('card')
    #debug(card.name)
    traits = getTraits(card)
    if traits.get('Living') and card.name != "Etherian Lifetree":
        tempParams = {
            'card':updateParams['card'],
            'traits':updateParams['traits'],
            'key':'Life',
            'newTraits':{'Life':2}
        }
        tempParams = remove_current_trait(tempParams)
        updateParams['traits'] = tempParams['traits']
    updateParams = remove_current_trait(updateParams)
    return updateParams

def remove_treebond_from_traits(updateParams):
    card = updateParams['card']
    if card.controller == me:
        mage = getMage()
        arenaMageTraits = getArenaTraits(mage)
        remArenaTraits = {'Life':4}
        traitParams = create_trait_params(arenaMageTraits,remArenaTraits,'Arena', mage, card,0,True)
        update_traits(traitParams)
    updateParams = remove_current_trait(updateParams)
    return updateParams

def removeFromMageTraits(card):
    mage = getMage()
    traitsToRemove = eval(card.bMageTraits)
    currentTraits = getArenaTraits(mage)
    traitParams = create_trait_params(currentTraits,traitsToRemove,'Arena',mage,card,0,True)
    update_traits(traitParams)
    return

def addEqTraitsToMage(card):
    mage = getMage()
    if card.bTraits != '':
        newEquipTraits = eval(card.bTraits)
        currentTraits = getEquipmentTraits(mage)
        traitParams = create_trait_params(currentTraits,newEquipTraits,'Equipment', mage, card)
        update_traits(traitParams)
    if card.zTraits != '':
        add_to_mage_z_traits(card, mage)
        addTraitsToZone(mage)
    if card.zfTraits != '':
        add_to_mage_zf_traits(card,mage)
        addTraitsToZone(mage)
    return

def add_to_mage_z_traits(card, mage):
    newZTraits = eval(card.zTraits)
    if mage.zTraits:
        mageZTraits = eval(mage.zTraits)
    else:
        mageZTraits = {}
    for key in newZTraits:
        mageZTraits[key] = newZTraits[key]
    mage.zTraits = str(mageZTraits)
    return

def add_to_mage_zf_traits(card, mage):
    newZTraits = eval(card.zfTraits)
    if mage.zfTraits:
        mageZFTraits = eval(mage.zfTraits)
    else:
        mageZFTraits = {}
    for key in newZTraits:
        mageZFTraits[key] = newZTraits[key]
    mage.zfTraits = str(mageZFTraits)
    return

def remove_eq_traits_from_mage(card):
    mage = getMage()
    if card.bTraits != '':
        traitsToRemove = eval(card.bTraits)
        currentTraits = getEquipmentTraits(mage)
        traitParams = create_trait_params(currentTraits,traitsToRemove,'Equipment',mage,card,0,True)
        update_traits(traitParams)
    if card.zTraits != '':
        removeTraitsFromOldZone(card)

        traitsToRemove = eval(card.zTraits)
        currentTraits = getZoneTraits(mage)
        traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',mage,card,0,True)
        update_traits(traitParams)

        removeEqZTraitsFromMage(mage,traitsToRemove)
    if card.zfTraits != '':
        removeTraitsFromOldZone(card)

        traitsToRemove = eval(card.zfTraits)
        currentTraits = getZoneTraits(mage)
        traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',mage,card,0,True)
        update_traits(traitParams)

        removeEqZFTraitsFromMage(mage,traitsToRemove)
    return

def removeEqZTraitsFromMage(mage,zTraits):
    traits = getZoneTraits(mage)
    for key in zTraits:
        if key in traits:
            if type(traits[key])==int:
                traits[key]-=zTraits[key]
                if traits[key]==0:
                    traits.pop(key,None)
            else:
                traits.pop(key, None)
    mage.zTraits = str(traits)
    return

def removeEqZFTraitsFromMage(mage,zTraits):
    traits = getZoneTraits(mage)
    for key in zTraits:
        if key in traits:
            if type(traits[key])==int:
                traits[key]-=zTraits[key]
                if traits[key]==0:
                    traits.pop(key,None)
            else:
                traits.pop(key, None)
    mage.zfTraits = str(traits)
    return

def addDefaultTraits(card): #Ugly, but it's a catch all for now
    traits = getTraits(card)
    if card.Type == 'Creature':
        if 'Living' not in traits:
            traits['Living'] = True
        if 'Incorporeal' not in traits:
            traits['Incorporeal'] = False
        if 'Flying' not in traits:
            traits['Flying'] = False
    elif card.Type ==  'Conjuration':
        if 'Living' not in traits:
            traits['Living'] = False
        if 'Incorporeal' not in traits:
            traits['Incorporeal'] = False    
    card.nativeTraits = str(traits)
    return

def addInitialZone(mage):
    mapDict = eval(getGlobalVariable("Map"))
    mwPlayerDict = eval(getGlobalVariable("MWPlayerDict"))
    playerNum = mwPlayerDict[me._id]["PlayerNum"]
    for zone in mapDict['zoneList']:
        if 'startLocation' in zone:    
            if int(zone['startLocation']) == playerNum:
                mage.currentZone = zone['Name']
                mage.formerZone = zone['Name']
    return

def addTraitsToZone(card):#TODO refactor
    mapDict = eval(getGlobalVariable("Map"))
    zoneList = mapDict['zoneList']
    currentZone = int(card.currentZone)
    cards = zoneList[currentZone-1]['cardsInZone']
    #debug('card: {}'.format(card))
    for target in cards:
        #debug('target: {}'.format(target))
        target = Card(target)
        if target != card:
            if card.zTraits not in ['','{}'] and card.isFaceUp:
                newZoneTraits = eval(card.zTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,newZoneTraits,'Zone', target, card)
                update_traits(traitParams)

            if card.zfTraits not in ['','{}'] and card.isFaceUp and card.controller ==target.controller:
                newZoneTraits = eval(card.zfTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,newZoneTraits,'Zone', target, card)
                update_traits(traitParams)

    return

def removeTraitsFromOldZone(card):
    mapDict = eval(getGlobalVariable("Map"))
    zoneList = mapDict['zoneList']
    if card.Type == 'Equipment':
        mage = getMage()
        formerZone = int(mage.formerZone)
    else:
        formerZone = int(card.formerZone)
    cards = zoneList[formerZone-1]['cardsInZone']
    if len(cards) >0:
        for target in cards:       
            target = Card(target)
            if card.zTraits not in ['', '{}']:
                traitsToRemove = eval(card.zTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',target,card,0,True)
                update_traits(traitParams)
            if card.zfTraits not in ['', '{}']:
                traitsToRemove = eval(card.zfTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',target,card,0,True)
                update_traits(traitParams)
    return

def removeTraitsFromCurrentZone(card):
    mapDict = eval(getGlobalVariable("Map"))
    zoneList = mapDict['zoneList']
    if card.Type == 'Equipment':
        mage = getMage()
        currentZone = int(mage.currentZone)
    else:
        currentZone = int(card.currentZone)
    cards = zoneList[currentZone-1]['cardsInZone']
    if len(cards) >0:
        for target in cards:       
            target = Card(target)
            if card.zTraits not in ['', '{}']:
                traitsToRemove = eval(card.zTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',target,card,0,True)
                update_traits(traitParams)
            if card.zfTraits not in ['', '{}']:
                traitsToRemove = eval(card.zfTraits)
                currentTraits = getZoneTraits(target)
                traitParams = create_trait_params(currentTraits,traitsToRemove,'Zone',target,card,0,True)
                update_traits(traitParams)
    return

def checkForCardsWithZoneTraits(card, zone = None):
    cardList = []
    cardsInZone = getOtherCardsInZoneList(card, zone)
    if cardsInZone != []:
        for target in cardsInZone:
            if target.zTraits not in ['','{}']:
                cardList.append(target)
    return cardList

def checkForCardsWithFriendlyZoneTraits(card, zone = None):
    cardList = []
    cardsInZone = getOtherCardsInZoneList(card, zone)
    if cardsInZone != []:
        for target in cardsInZone:
            if target.zfTraits not in ['','{}']:
                cardList.append(target)
    return cardList

def findArenaTraitsList():
    cardsWithArenaTraits=[]
    for card in table:
        if card.baTraits not in ['','{}']:
            cardsWithArenaTraits.append(card)
        elif card.bfaTraits not in ['','{}'] and card.controller == me:
            cardsWithArenaTraits.append(card)
    return cardsWithArenaTraits

def addTraitsToArena(card):#ReDesign into 'Target type':{'effect':'bonus'} at some point
    for targetCard in table:
        zone = getZoneContaining(targetCard)
        if zone:
            currentTraits = getArenaTraits(targetCard)
            newArenaTraits = eval(card.baTraits)
            #debug(card.baTraits)
            traitParams = create_trait_params(currentTraits,newArenaTraits,'Arena', targetCard, card)
            update_traits(traitParams)
            #addToArenaTraits(card, targetCard)
    return

def removeTraitsFromArena(card):
    if card.baTraits not in ['','{}']:
        traitsToRemove = eval(card.baTraits)
    elif card.bfaTraits not in ['','{}']:
        traitsToRemove= eval(card.baTraits)
    for targetCard in table:
        zone = getZoneContaining(targetCard)
        if zone:
            currentTraits = getArenaTraits(targetCard)
            traitParams = create_trait_params(currentTraits,traitsToRemove,'Arena',targetCard,card,0,True)
            update_traits(traitParams)
            #removeFromArenaTraits(targetCard,traitsToRemove)
    return

def getChanneling(card):
    if 'Mage' in card.Subtype and card.controller == me:
        channeling = me.Channeling
    else:
        if card.Total_Channeling:
            channeling = eval(card.Total_Channeling)
        else:
            channeling = eval(card.Stat_Channeling)
    return channeling

def adjust_life_total(card, addlLife = 0):
    debug('adjust_life_total for {}'.format(card.name))
    if card.Stat_Life:
        traits = getTraits(card)
        
        lifeAdj = traits.get('Life',0)

        baseLife = eval(card.Stat_Life)
        
        if card.Total_Life:
            oldTotalLife = eval(card.Total_Life)
        else:
            oldTotalLife = baseLife
        
        totalLife = baseLife + lifeAdj + addlLife
        
        if 'Mage' in card.Subtype and card.controller == me:
            me.Life = totalLife
            card.Total_Life = str(totalLife)
        else:
            card.Total_Life = str(totalLife)
        if totalLife != oldTotalLife:
            notify('{}\'s life total is now {}'.format(card, totalLife))
    return

def adjust_channeling(card):
    if card.Stat_Channeling:
        traits = getTraits(card)
        
        channelAdj = traits.get('ChannelBoost',0)

        baseChannel = eval(card.Stat_Channeling)
        
        if card.Total_Channeling:
            oldTotalChannel = eval(card.Total_Channeling)
        else:
            oldTotalChannel = baseChannel

        totalChannel = baseChannel + channelAdj

        if 'Mage' in card.Subtype:
            card.Total_Channeling = str(totalChannel)
            me.Channeling = totalChannel
        else:
            card.Total_Channeling = str(totalChannel)
        if totalChannel != oldTotalChannel:
            notify('{}\'s Channeling is now {}'.format(card, totalChannel))
    return

def getRemainingLife(card):
    debug(card)
    if card.Type in ['Creature', 'Conjuration'] and card.Stat_Life:
        debug('got here')
        damage_total, sources = get_collected_damage_total(card)
        if 'Mage' in card.Subtype:
            mage = getMage()
            
            remainingLife = max(me.Life - damage_total,0)
        else:
            if card.Total_Life == '':
                card.Total_Life = card.Stat_Life
            debug(card.Stat_Life)
            remainingLife = max(eval(card.Total_Life) - damage_total,0)
            debug(str(remainingLife))
        return remainingLife
    else:
        '''returns true because tokenManipulation line 94 looks for getRemainingLife <1'''
        return True

def get_total_damage_markers(card):
    if 'Mage' in card.Subtype:
        damageTotal = me.Damage
    else:
        damageTotal = card.markers[Damage]
    return damageTotal

def addFriendlyArenaTraits(card):
    for target in table:
        if target.Type in typeIgnoreList or target.Name in typeIgnoreList or 'Magestats' in card.Type:
            return
        elif target.controller == card.controller:
            currentTraits = getArenaTraits(target)
            newArenaTraits = eval(card.baTraits)
            traitParams = create_trait_params(currentTraits,newArenaTraits,'Arena', target, card)
            update_traits(traitParams)
    return



def add_adra_curse(card):
    adra = eval(getGlobalVariable('adramelechWarlock'))
    if len(adra) == 2 or (len(adra) == 1 and Card(adra[0]).controller == card.controller):
        cursedCard = Card(int(card.isAttachedTo))
        ccTraits = getAttachedTraits(cursedCard)
        if 'adraCursed' not in ccTraits:
            newTraits = {'Flame':1, 'adraCursed':True}
            traitParams = create_trait_params(ccTraits,newTraits,'Attached', cursedCard, card)
            update_traits(traitParams)
    return
'Attached'
def updateAdraCurse(card):
    #debug('updating adra curse')
    cursedCard = Card(int(card.isAttachedTo))
    otherAttachments = getAttachedCards(cursedCard)
    stillCursed = False
    for attachment in otherAttachments:
        if attachment == card:
            continue
        else:
            if 'Curse' in attachment.Subtype:
                stillCursed = True
    if not stillCursed:
        remove_adra_curse(cursedCard)

def remove_adra_curse(card):
    ccTraits = getAttachedTraits(card)
    if 'adraCursed' in ccTraits:
        newTraits = {'Flame':1, 'adraCursed':True}
        traitParams = create_trait_params(ccTraits,newTraits,'Attached', card, card,0,True)
        update_traits(traitParams)
    return

def combineZTraitsToRemove(oldzTraitList, oldzfTraitList):
    traitsToRemove = {}
    if oldzTraitList:
        for card in oldzTraitList:
            cardTraits = eval(card.zTraits)
            traitsToRemove.update(cardTraits)
    if oldzfTraitList:
        for card in oldzfTraitList:
            cardTraits = eval(card.zfTraits)
            traitsToRemove.update(cardTraits)
    return traitsToRemove

def combineZTraitsToAdd(zTraitList, zfTraitList):
    traitsToAdd = {}
    if zTraitList:
        for card in zTraitList:
            cardTraits = eval(card.zTraits)
            traitsToAdd.update(cardTraits)
    if zfTraitList:
        for card in zfTraitList:
            cardTraits = eval(card.zfTraits)
            traitsToAdd.update(cardTraits)
    return traitsToAdd

def compareTraitsToAdd(traitsToAdd, traitsToRemove):###########TEST
    if traitsToRemove:
        for key in traitsToAdd:
            if traitsToAdd.get(key, None) == traitsToRemove.get(key, None):
                traitsToRemove.pop(key,None)
        return traitsToRemove


def reset_EOA_traits(card):
    card.EOATraits = ''
    return