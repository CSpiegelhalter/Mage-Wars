def resetAndChannel():
    mute()
    notify("{} resets all Action, Ability, Quickcast, and Ready Markers on the Mages cards by flipping them to their active side.\n".format(me.name))
    for card in table:
        if card.name == 'Mana Shard' and card.controller == me:
            resolveManaShard(card)
        if card.targetedBy == me:
            card.target(False)
        if card.isDestroyed:
            card.isDestroyed = ''
        if card.controller == me and card.isFaceUp and not "Alfiya" in card.Name:
            resetMarkers(card)
            reset_temp_traits(card)
            resolveChanneling(card)
            deleteBraceYourself(card)
    return

def resetMarkers(card):
    mute()
    mDict = {ActionRedUsed : ActionRed,
                ActionBlueUsed : ActionBlue,
                ActionGreenUsed : ActionGreen,
                ActionPurpleUsed : ActionPurple,
                QuickBack : Quick,
                Used : Ready,
                UsedII : ReadyII,
                VoltaricON : VoltaricOFF,
                DeflectU : DeflectR,
                Visible : Invisible}
    for key in mDict:
        if card.markers[key] == 1:
            card.markers[key] = 0
            card.markers[mDict[key]] = 1
    if "Packleader's Cowl" == card.Name: card.markers[Guard] = 1
    if "Lightning Raptor" == card.Name and card.markers[Charge]<5: card.markers[Charge] += 1
    
def reset_temp_traits(card):
    traitsToRemove = getTempTraits(card)
    currentTraits = getTempTraits(card)
    traitParams = create_trait_params(currentTraits,traitsToRemove,'Temp',card,card,0,True)
    update_traits(traitParams)
    return


def resolveChanneling(card):
    mute()
    if card.Stat_Channeling:
        if card.name =='Barracks':
            channel = barracks_channel()
        elif card.name == 'Echo of the Depths':
            channel = echo_channel(card)
        else:
            channel = getChanneling(card)
        #debug("Found Channeling stat {} in card {}".format(channel,card.name))
        addMana(card,(channel))
        notify("{} channels {} Mana".format(card, (channel)))
    return

def barracks_channel():
    bChannel = 0
    for card in table:
        if card.isFaceUp and 'Outpost' in card.Subtype and card.controller == me:
            bChannel+=1
    return min(bChannel,3)

def echo_channel(echo):
    channel_bonus = 0
    for card in table:
        if card.isFaceUp and 'Song' in card.Subtype and card.controller == me:
            channel_bonus = 1
            notify('A song has boosted Echo of the Depths\'s channeling by 1')
    return (getChanneling(echo)+channel_bonus)

def resolveManaShard(manaShard):
    cardList = getAllCardsInZoneList(manaShard)
    choiceList = []
    manaRxList = []
    for card in cardList:
        if card.Stat_Channeling != '' and card.controller == manaShard.controller:
            choiceList.append(card.name)
            manaRxList.append(card)
    if choiceList:
        choiceList.append('None')
        #colors = ["#996600" for c in choiceList]+['#000000']
        colors = [getCardTypeColor(manaRxList[i]) for i in range(len(manaRxList))]+ ['#000000']
        manaRx = askChoice('Which Card would you like to give mana from the Mana Shard?',choiceList,colors)
        if manaRx != len(choiceList) and manaRx != 0:
            addMana(manaRxList[manaRx-1],1)
            notify('{} gains 1 mana from the Mana Shard!'.format(manaRxList[manaRx-1]))
    return

def upkeepPhase():
    poisonCondList = []
    curseCountList = []
    for card in table:
        #card.peek()
        #debug('card: {}'.format(card.name))
        if card.controller == me and not (card.Type in typeIgnoreList or card.Name in typeIgnoreList or 'Magestats' in card.Type):
            traits = getTraits(card)
            if not i_have_initiative():
                resolve_lullaby(card, traits)
            resolve_life_bond(card, traits)
            resolve_death_link(card, traits)
            resolve_drown(card)
            resolveLifeGain(card,traits)
            resolveBurns(card, traits)
            resolveRot(card,traits)
            resolveBleed(card,traits)
            checkFermata(card)
            resolveLoadTokens(card,traits)
            resolveEnchantmentDot(card,traits)
            resolveTalos(card,traits)
            resolveCurseItem(card,traits)
            resolveMheg(card)
            resolveMadrigal(card,traits)
            resolveMelting(card,traits)
            resolveLivingArmor(card)
            resolveKiGen(card,traits)
            resolveVoltaric(card) 
            resolveKiUpkeep(card,traits)
            resolveAreaDot(card,traits) 
            resolveSirenHeal(card,traits) 
            resolveStormTokens(card)
            resolveDissipate(card,traits)
            resolveStranglevine(card)
            resolveReconstruct(card, traits)
            resolve_tundra_damage(card,traits)
            resolveRegenerate(card,traits)
            resolveDorseus(card)
            resolve_lullaby(card, traits)
            give_FF_token(card)
            resolveFaithHealersStaff(card)
            resolveAsyranRobes(card)
            resolveUpkeep(card,traits)
        elif card.controller == me and 'Magestats' in card.Type:
            resolve_upkeep_glyphs(card)
        poisonCondList = countPoisonConds(card, poisonCondList)
        curseCountList = countCursedTargets(card, curseCountList)
    resolveMolochs(curseCountList)
    resolvePlagueMaster(poisonCondList)
    '''for card in table:
        if getRemainingLife(card) <1 and getGlobalVariable("GameSetup") == "True":
            remoteCall(card.controller, 'deathPrompt',[card])'''
    return
 
def resolveUpkeep(card,traits):
    mute()
    #still need to take these into account WIP
    '''Remaining: ManaPrism'''
    monolith = getCard('Harshforge Monolith')
    upkeepAmount = 0
    if 'Upkeep' in traits and card.isFaceUp:
        upkeepAmount += traits['Upkeep']
    if card.Type =='Creature' and 'Mage' not in card.Subtype and 'MordoksObelisk' in traits and card.isFaceUp:
        upkeepAmount +=1
    if card.name == 'Mind Control' and card.isFaceUp:
        controlled = Card(int(card.isAttachedTo))
        upkeepAmount += getTotalCardLevel(controlled)
    if card.School == 'Mind' and upkeepAmount > 0 and card.isFaceUp:
        psiOrb = getCard('Psi-Orb')
        if psiOrb and timesHasUsedAbility(psiOrb) <3:
            upkeepAmount -=1
            rememberAbilityUse(psiOrb)
    if monolith and card.Type == 'Enchantment':
        zone = getZoneContaining(card)
        if zone:
            if cardGetDistance(card, monolith) <2:
                upkeepAmount += 1
    if card.name == 'Drown':
        upkeepAmount += card.markers[Suffocate]
    if upkeepAmount > 0:
        upkeepPayment(card, upkeepAmount)
    return

def upkeepPayment(card, upkeepAmount):
    choiceList = ['Yes', 'No']
    colorsList = ['#0000FF', '#FF0000']
    upkeepFilter = "#ABFFFFFF"
    card.filter = upkeepFilter #Light Blue - R=126 G=198 B=222
    if me.Mana < upkeepAmount:
        notify("{} was unable to pay the Upkeep cost for {}\n".format(me, card))
        discard(card)
        return
    else:
        choice = askChoice("Would you like to pay the {} mana upkeep cost for {}?".format(str(upkeepAmount),card.Name), choiceList, colorsList)
        if choice == 1:
            me.Mana -= upkeepAmount
            card.filter = None
            notify("{} pays the Upkeep cost of {} for {}\n".format(me, str(upkeepAmount), card))
        else:
            notify("{} has chosen not to pay the Upkeep cost for {}\n".format(me, card))
            discard(card)

def resolveRegenerate(card,traits):
    mute()
    if traits.get('Living') and card.isFaceUp:
        CGround = getCard('Consecrated Ground')
        if 'Regenerate' in traits and ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits or 'darkfenneOwl' in traits):
            notify("{} has the Finite Life Trait and can not Regenerate\n".format(card.name))
            return
        elif 'Regenerate' in traits and not ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits or 'darkfenneOwl' in traits):
            regenAmount = traits['Regenerate'][0]
            if 'Mage' in card.Subtype:
                damage = me.damage
                removeRegenDamage(card, damage, regenAmount)
            elif card.Type in ['Creature','Conjuration','Conjuration-Wall','Conjuration-Terrain']:
                damage = card.markers[Damage]
                removeRegenDamage(card, damage, regenAmount)
        elif 'consecratedGround' in traits and not 'Regenerate' in traits and not ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits or 'darkfenneOwl' in traits) and 'Holy' in card.School and card.controller == CGround.controller:
            damage = get_total_damage_markers(card)
            regenAmount = 1
            notify('The Consecrated Ground gives {} strength'.format(card))
            removeRegenDamage(card, damage, regenAmount)
    return

def removeRegenDamage(card, damage, regenAmount):
    mute()
    if damage > regenAmount:
        subDamageAmount(card,regenAmount)
        notify("{}\'s {} regenerates and removes {} damage.\n".format(card.controller, card.name, regenAmount))
    elif regenAmount >= damage:
        if damage > 0:
            subDamageAmount(card,regenAmount)
            notify("{}\'s {} regenerates and removes all damage.\n".format(card.controller, card.name))
        else:
            notify("{}\'s {} is at full health.\n".format(card.controller, card.name))
    return

def resolveLifeGain(card,traits):
    if 'LifeGain' in traits and not ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits):
        mage = getMage()
        targetArenaTraits = getArenaTraits(mage)
        newArenaTraits = {'Life':1}
        traitParams = create_trait_params(targetArenaTraits,newArenaTraits,'Arena', mage, mage)
        update_traits(traitParams)
        notify('{} gains life from the Sunfire Amulet!'.format(me))
    elif 'LifeGain' in traits and ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits):
        notify("{}\'s {} has the Finite Life Trait and can not gain Life\n".format(card.controller, card))
    return

def resolveBurns(card, traits):
    mute()
    '''Remaining: burnproof'''
    #debug('card: {}'.format(card))
    Damage = 0
    burnsRemoved = 0
    if traits.get('Burnproof', False) and card.markers[Burn]:
        card.markers[Burn] = 0
        notify('{} is burnproof'.format(card))
    if traits.get('Hellscape') and card.markers[Burn] == 0:
        card.markers[Burn]+=1
        notify("Hellscape adds a burn to {}.\n".format(card))

    if card.markers[Burn]:
        for i in range(0, card.markers[Burn]):
            roll = rnd(0,2)
            #debug('Burn Roll: {}'.format(str(roll)))
            if roll == 0 and not ('Burn Preservation' in traits or 'adramelechsTouch' in traits):
                card.markers[Burn]-=1
                burnsRemoved +=1
            Damage += roll
        if 'Immunity' in traits:
            if 'Flame' in traits['Immunity']:
                notify("{} is Flame Immune and takes no damage".format(card))
                return
            else:
                addDamageAmount(card, Damage)
        else:
            addDamageAmount(card, Damage)
        if Damage > 0: notify("Adramelech laughs while {} continues to Burn, {} damage was added!\n".format(card, Damage))            
        if burnsRemoved > 0: notify("{} Burns were removed from {}.\n".format(burnsRemoved,card))
        if burnsRemoved == 0 and Damage == 0 and ('Burn Preservation' in traits or 'adramelechsTouch' in traits): notify("The burns on {} were prevented from being removed.\n".format(card))
    return

def resolveRot(card,traits):
    mute()
    if traits['Living'] if 'Living' in traits else '':
        addDamageAmount(card, card.markers[Rot])
        if card.markers[Rot] >0:
            notify("{} Rots for {} damage!\n".format(card.Name, str(card.markers[Rot])))
    return

def resolveBleed(card,traits):
    mute()
    if (traits['Living'] if 'Living' in traits else '') and not 'Plant' in card.Subtype:
        addDamageAmount(card, card.markers[Bleed])
        if card.markers[Bleed] >0:
            notify("{} Bleeds for {} damage!\n".format(card.Name, str(card.markers[Bleed])))
    return

def resolveDissipate(card,traits):
    mute()
    mage = getMage()
    if 'Dissipate' in traits and card.isFaceUp:
        card.markers[Dissipate] -=1
        notify("Removing 1 Dissipate Token from {}, {} Dissipate token(s) left.\n".format(card.Name,card.markers[Dissipate]))
        if not card.markers[Dissipate] and not fermataMarkersFound(card):
            if mage.Name == 'Siren' and 'Song' in card.Subtype and card.group.name not in ['Discard Pile', 'Obliterate Pile']:
                #debug('start Fermata')
                startFermata(card)
            else:
                notify("{} no longer has any Dissipate Tokens\n".format(card.Name))
                if card.name == 'Mana Lotus':
                    me.Mana += 5
                    notify('the Mana Lotus gives 5 mana to the {}.'.format(mage))
                discard(card)
    return

def startFermata(card):
    mageDict = eval(me.getGlobalVariable("MageDict"))
    mageStatsID = int(mageDict["MageStatsID"])
    cardLevel = getTotalCardLevel(card)
    canFermata = False

    for marker in [FermataBlue1, FermataGreen1]:
        if Card(mageStatsID).markers[marker]:
            canFermata = True
    
    if canFermata:
        extensionChoice = askChoice("Do you want to extend the Song {} for a Round by paying {} mana?".format(card.Name,str(cardLevel)),["Yes","No"],["#171e78","#de2827"])
        if extensionChoice == 1:
            me.Mana -= cardLevel
            transferFermataMarker(card, mageStatsID)
            notify("{} has decided to extend the Song {}.\n".format(me,card))
        else:
            notify("{} no longer has any Dissipate Tokens\n".format(card.Name))
            discard(card)
    else:
        notify("{} no longer has any Dissipate Tokens\n".format(card.Name))
        discard(card)
    return

def checkFermata(card): #ugh, will need refactored. This is ugly too
    mageDict = eval(me.getGlobalVariable("MageDict"))
    mageStatsID = int(mageDict["MageStatsID"])
    cardLevel = getTotalCardLevel(card)
    for marker in ['FermataBlue1', 'FermataGreen1']:
        if card.markers[eval(marker)]:
            if me.Mana >= cardLevel:
                extensionChoice = askChoice("Do you want to extend the Song {} for a second Round by paying {} mana?".format(card.Name,str(cardLevel)),["Yes","No"],["#171e78","#de2827"])
                if extensionChoice == 1:
                    me.Mana -= cardLevel
                    incrementFermataMarker(card)
                    return
                else:
                    notify("{} chose not to extend {} and it has expired. The Fermata Marker has been placed back on the stats card.\n".format(me, card.Name))
                    returnFermataMarker(mageStatsID,marker)
                    discard(card)
                    return
            else:
                notify("{} cannot afford to extend {} and it has expired. The Fermata Marker has been placed back on the stats card.\n".format(me, card.Name))
                returnFermataMarker(mageStatsID,marker)
                discard(card)
                return
    
    for marker in ['FermataBlue2', 'FermataGreen2']:
        if card.markers[eval(marker)]:
            notify("{} has expired. The Fermata Marker has been placed back on the stats card.\n".format(card))
            returnFermataMarker(mageStatsID, marker)
            discard(card)
            return
    return


def resolveLoadTokens(card,traits):
    if 'LoadToken' in traits and card.isFaceUp:
        if card.markers[LoadToken] == 0:
            notify("Placing the First Load Token on {}\'s {}...\n".format(card.controller, card)) #found no load token on card
            card.markers[LoadToken] = 1
        elif card.markers[LoadToken] == 1:
            notify("Placing the Second Load Token on {}\'s {}...\n".format(card.controller, card)) #found one load token on card
            card.markers[LoadToken] = 2
    return

def resolveEnchantmentDot(card,traits):
    if 'poisonDOT' in traits: #Ghoul Rot, Curse of Decay
        if 'Immunity' in traits:
            if 'Poison' in traits['Immunity']:
                notify("{} is Poison Immune and takes no damage".format(card))
                return 
        else:
            for attach in eval(card.Attachments):
                if Card(int(attach)).name == 'Ghoul Rot':
                    notify("{} takes {} damage from Ghoul Rot".format(card, str(traits['poisonDOT'])))
                    addDamageAmount(card, traits['poisonDOT'])
                elif Card(int(attach)).name == 'Curse of Decay':
                    notify("{} takes {} damage from Curse of Decay".format(card, str(traits['poisonDOT'])))
                    addDamageAmount(card, traits['poisonDOT'])
    if 'forceCrush' in traits:
        notify("{} takes 2 damage from Force Crush\n".format(card))
        addDamageAmount(card, 2)
    if 'arcaneCorruption' in traits:
        damage = 0
        for attach in card.attachments:
            if attach.Type == 'Enchantment' and attach.controller == me:
                damage += 1
        addDamageAmount(card, damage)
        notify("{} takes {} damage from Arcane Corruption\n".format(card, damage))
    if 'Reclamation' in traits:
        damage = 2
        notify("{} takes {} damage from Reclamation\n".format(card, damage))
        addDamageAmount(card, damage)
    return

def resolveTalos(card,traits):
    if card.Name == 'Altar of Domination':
        if traits['Outposts'] >= 3:
            card.markers[DominationToken] +=1
            notify("Placing a Domination Token on to the {}...\n".format(card))
    return

def resolveCurseItem(card,traits):
    if 'curseItem' in traits:
        choice = askChoice("Your {} is Cursed. Would you like to take 2 damage to keep it?".format(card.Name), ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            mageDict = eval(me.getGlobalVariable("MageDict"))
            mageID = int(mageDict["MageID"])
            for p in players:
                if p.name == card.controller.name:
                    remoteCall(p, "addDamageAmount", [Card(mageID), 2])
            notify("{}\'s {} is cursed! {} takes 2 damage from holding onto it!\n".format(me, card, me))
            return
        else:
            discard(card)
            notify("{}\'s {} is cursed! {} throws it away before taking any damage!\n".format(me, card, me))
            return
    return

def resolveMheg(card):
    if card.Name == 'Mhegedden, Sealed Demon' and card.markers[SealToken]:
        card.markers[SealToken]-=1
        mage = getMage()
        targetArenaTraits = getArenaTraits(mage)
        newArenaTraits = {'Life':-2}
        traitParams = create_trait_params(targetArenaTraits,newArenaTraits,'Arena', mage, mage)
        update_traits(traitParams)
        notify("A Seal Token has been removed from Mhegedden!\n{} loses 2 life!\n{} token(s) remain".format(me, card.markers[SealToken]))
    return

def resolveMadrigal(card,traits):
    if 'healingMadrigal' in traits and card.Type == 'Creature':
        healCreatureByAmount(card, 2,traits,'Madrigal')
    return

def resolveMelting(card,traits):
    in_range_of_tundra = check_tundra_range(card)
    if 'Melting' in traits and not 'Tundra' in traits and not 'deepFreeze' in traits and not in_range_of_tundra and card.isFaceUp:
        addDamageAmount(card, traits['Melting'])
        notify('{} melts for {} damage!'.format(card, str(traits['Melting'])))
    return

def resolve_tundra_damage(card,traits):
    if 'Tundra' in traits:
        amount = addDamageAmount(card, card.markers[Freeze])
        if amount > 0:
            notify('The Tundra causes {} damage to {}!'.format(card.markers[Freeze],card))
    return

def resolveLivingArmor(card):
    if card.name == 'Living Armor' and card.markers[Armor] <3 and card.isFaceUp:
        choice = askChoice("Would you like to pay 1 mana to gain 2 armor tokens (to a total max of 3)?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            card.markers[Armor] = min(card.markers[Armor]+2, 3)
            me.mana -=1
            notify('The {} grows stronger!\n'.format(card))
    return

def resolveKiUpkeep(card,traits):
    mage = getMage()
    if 'UpKip' in traits and mage.markers[Ki]:
        notify('test')
        choice = askChoice("Would you like to pay 1 Ki to keep {} in play?".format(card.name), ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            mage.markers[Ki]-=1
        else:
            discard(card)
    elif 'Upkip' in traits and not mage.markers[Ki]:
        discard(card)
    return

def resolveVoltaric(card):
    if card.markers[VoltaricOFF] and me.mana >2:
        toggleVoltaric(card)
    return

def resolveKiGen(card,traits):
    if 'Ki' in traits:
        card.markers[Ki]+=traits['Ki']
    if 'ringOfKi' in traits:
        choice = askChoice("Would you like to pay 1 mana for 2 Ki?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            me.mana -=1
            mage = getMage()
            mage.markers[Ki]+=2
    return



def resolve_upkeep_glyphs(card):
    if card.markers[WaterGlyphActive] and me.mana > 1:
        choice = askChoice("Would you like to pay 2 mana to heal a creature with your Water Glyph?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            livingList = []
            for cardChoice in table:#ugly, but only way to iterate over the cards on the table
                if cardChoice.controller == me:
                    traits = getTraits(cardChoice)
                    if traits.get('Living',False) and cardChoice.Type == 'Creature':
                        livingList.append(cardChoice)
            selectedList = create_card_dialog(livingList, 'What would you like to heal?', 0, 1)
            if selectedList:
                me.mana -= 2
                card.markers[WaterGlyphActive] = 0
                card.markers[WaterGlyphInactive] = 1
                selectedCard = selectedList[0]
                traits = getTraits(selectedCard)
                healCreatureByAmount(selectedCard, 2, traits, 'Water Glyph')
    if card.markers[EarthGlyphActive] and me.mana > 1:
        choice = askChoice("Would you like to pay 2 mana to give a creature Armor +2 with your Earth Glyph?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            armorList = []
            for cardChoice in table:
                if (cardChoice.controller == me and
                    cardChoice.Stat_Armor != '-' and 
                    not (cardChoice.Type in typeIgnoreList or cardChoice.Name in typeIgnoreList or 'Magestats' in cardChoice.Type)):
                        armorList.append(cardChoice)
            selectedList = create_card_dialog(armorList, 'What would you like to give Armor?', 0, 1)
            if selectedList:
                me.mana -= 2
                card.markers[EarthGlyphActive] = 0
                card.markers[EarthGlyphInactive] = 1
                selectedCard = selectedList[0]
                tempTraits = getTempTraits(selectedCard)
                newTempTraits = {'Armor':2}
                traitParams = create_trait_params(tempTraits,newTempTraits,'Temp', selectedCard, card)
                update_traits(traitParams)
                notify('{} uses the Earth Glyph to give {} Armor +2 until the end of the round'.format(me, selectedCard))
        pass
    return

def resolveSirenHeal(card,traits):
    if card.Name == 'Siren':
        if 'ShallowSea' in traits and not ('Deathlock' in traits or 'Finite Life' in traits or 'Sardonyx' in traits or 'darkfenneOwl' in traits) and me.Damage > 0:
            subDamage(card)
            notify("Siren heals 1 from being in the Shallow Sea")
    return

def resolveAreaDot(card,traits):
    CGround = getCard('Consecrated Ground')
    if 'idolOfPestilence' in traits and card.Type == 'Creature' and traits.get('Living') and not ('Poison' in traits.get('Immunity') if traits.get('Immunity') else False):
        addDamageAmount(card, 1)
        notify('{} feels the effect of the idol of Pestilence!'.format(card))
    if 'Plagued' in traits and card.Type == 'Creature' and traits.get('Living') and not ('Poison' in traits.get('Immunity') if traits.get('Immunity') else False):
        addDamageAmount(card, 1)
        notify('{} feels the effect of Plagued!'.format(card))
    if 'Malacoda' in traits and card.Type == 'Creature' and traits.get('Living') and not ('Poison' in traits.get('Immunity') if traits.get('Immunity') else False):
        addDamageAmount(card, 2)
        notify('{} feels the effect of Malacoda\'s Poison!'.format(card))
    if 'PGCloud' in traits and card.Type == 'Creature' and traits.get('Living') and not ('Poison' in traits.get('Immunity') if traits.get('Immunity') else False):
        addDamageAmount(card, 2)
        notify('{} feels the effect of the Poison Gas Cloud!'.format(card))
    if CGround and 'Holy' not in card.School and card.controller != CGround.controller and card.Type == 'Creature' and 'consecratedGround' in traits:
        addDamageAmount(card, 1)
        notify('{} is being purified in the Holy light of the Consecrated Ground!'.format(card))
    return

def resolveStormTokens(card):
    if card.Name == 'Staff of Storms' and card.isFaceUp:
        if card.markers[StormToken]<=3:
            notify("A Storm Token appears on {}\'s {}.\n".format(me, card)) 
            card.markers[StormToken] += 1
        notify("{} has {} Storm Tokens\n".format(card, card.markers[StormToken]))
    return

def deleteBraceYourself(card):
    if card.Name == 'Brace Yourself' and card.isFaceUp:
        discard(card)
    return

def resolveStranglevine(card):
    if card.name == 'Stranglevine' and card.isFaceUp:
        card.markers[CrushToken]+=1
        target = Card(int(card.isAttachedTo))
        choice = askChoice("Would you like to pay {} mana to keep the Stranglevine attached to {}?".format(str(card.markers[CrushToken]), target.name), ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            if me.mana < card.markers[CrushToken]:
                whisper('You do not have enough mana to do that!')
                notify("The Stranglevine on {} whithers away!".format(target))
                discard(card)
            else:
                notify("The Stranglevine on {} grows tighter!\n{} damage is added!".format(target, card.markers[CrushToken]))
                me.mana -= card.markers[CrushToken]
                remoteCall(target.controller, 'addDamageAmount',[target,card.markers[CrushToken]])
        else:
            notify("The Stranglevine on {} whithers away!".format(target))
            discard(card)
    return

def resolveReconstruct(card, traits):
    if 'Mort' in traits and 'Skeleton' in card.Subtype:
        damageRemaining = get_total_damage_markers(card)
        if damageRemaining:
            subDamageAmount(card, traits['Mort'])
            notify('{} reconstructs by {}!'.format(card,min(damageRemaining, traits['Mort'])))
    return

def countPoisonConds(card, poisonCondList):
    for key in card.markers:
        if "82df2507-4fba-4c81-a1de-71e70b9a16f5" in key:
            poisonCondList.append(card)
            #Cripple
        elif "81360faf-87d6-42a8-a719-c49386bd2ab5" in key:
            #Rot
            poisonCondList.append(card)
        elif "826e81c3-6281-4a43-be30-bac60343c58f" in key:
            #Tainted
            poisonCondList.append(card)
        elif "22ef0c9e-6c0b-4e24-a4fa-e9d83f24fcba" in key:
            #Weak
            poisonCondList.append(card)
    return poisonCondList

def countCursedTargets(card, curseCountList):
    if find_if_cursed_by_me(card):
        curseCountList.append(card)
    return curseCountList

def resolvePlagueMaster(poisonCondList):
    mage = getMage()
    if mage.name == 'Necromancer' and len(poisonCondList)>0:
        if askChoice('Would you like to use Plaguemaster?',['Yes','No'],["#01603e","#de2827"]) == 1:
            dialog = cardDlg(poisonCondList)
            dialog.min = 0
            dialog.max = len(poisonCondList)
            dialog.title = 'Select your plaguemaster victims'
            selectedList = dialog.show()
            if me.Mana < len(selectedList):
                whisper('You don\'t have enough mana for that many')
                selectedList = dialog.show()
            me.Mana -= len(selectedList)
            notify('{} pays {} for their plaguemaster ability'.format(me, len(selectedList)))
            for card in selectedList:
                remoteCall(card.controller, 'addDamageAmount', [card, 1])
                notify('{} feels the effects of {} the plaguemaster'.format(card, me))
    return

def resolveMolochs(curseCountList):
    mage = getMage()
    mageTraits = getTraits(mage)
    if 'Moloch' in mageTraits and len(curseCountList)>0:
        if askChoice('Would you like to use Moloch\'s Torment?',['Yes','No'],["#01603e","#de2827"]) == 1:
            dialog = cardDlg(curseCountList)
            dialog.min = 0
            dialog.max = len(curseCountList)
            dialog.title = 'Select your Moloch\'s Torment victims'
            selectedList = dialog.show()
            if me.Mana < len(selectedList):
                whisper('You don\'t have enough mana for that many')
                selectedList = dialog.show()
            me.Mana -= len(selectedList)
            notify('{} pays {} for Moloch to Torment its victims!\n'.format(me, len(selectedList)))
            for card in selectedList:
                remoteCall(card.controller, 'addDamageAmount', [card, 1])
                notify('{} feels the cursed pain from Moloch!'.format(card))
    return

def resolveDorseus(card):
    if card.name =='Dorseus, Stallion of Westlock':
        healList = getOtherCardsInZoneList(card)
        for healCard in healList:
            if healCard.controller != me:
                healList.remove(healCard)
            if healCard.Type != 'Creature':
                healList.remove(healCard)
        if healList >0:
            dialog = cardDlg(healList)
            dialog.min = 0
            dialog.max = 1
            dialog.title = 'Who would you like to heal with Dorseus'
            selectedCard = dialog.show()
            if selectedCard:
                selectedCard = selectedCard[0]
                damageRemaining = get_total_damage_markers(selectedCard)
        if selectedCard and damageRemaining:
            notify('{} is healed by Dorseus\'s divine light'.format(selectedCard))
            subDamageAmount(selectedCard, 2)
    return

def resolve_lullaby(card, traits):
    if 'Lullaby' in traits:
        attackRoll, effectRoll = rollDice(0)
        if effectRoll > 6:
            card.markers[Stun] +=1
            notify('{} has been stunned by the Lullaby!'.format(card))
        else:
            card.markers[Daze] += 1
            notify('{} has been dazed by the Lullaby!'.format(card))
    return

def give_FF_token(card):
    if 'Forcefield' in card.name and card.isFaceUp and card.markers[FFToken]<3:
        card.markers[FFToken] += 1
        notify('Forcefield gains a token\n')

def resolve_life_bond(card, traits):
    if traits.get('Lifebond') and card.markers[Damage]:
        choice = askChoice('Would you like to transfer Damage from {} with Life Link?'.format(card.name),['Yes','No'],["#01603e","#de2827"])
        if choice == 1:
            transfer_to_target = [getMage()]
            transfer_from_target = [card]
            damage_transfer(transfer_from_target, transfer_to_target, 'Life Link', 3)
    elif traits.get('EleLifebond'):
        debug('here')
        choice = askChoice('Would you like to pay 1 mana to use Lifebond to transfer Damage?',['Yes','No'],["#01603e","#de2827"])
        if choice == 1 and me.Mana > 1:
            transfer_to_list = getElementals(card)
            transfer_to_list.append(getMage())
            ELBDlg = create_double_list_dialog(transfer_to_list,[], 'Lifebond','Select (click on) where the damage will come from', 'Move the target to receive the damage below', min = 1, max = 1)
            transfer_from_target = ELBDlg.show()
            transfer_to_target = ELBDlg.bottomList
            cost = 1
            if transfer_from_target and transfer_to_target:
                me.Mana -= cost
                notify('{} pays {} mana'.format(me, cost))
                damage_transfer(transfer_from_target, transfer_to_target)
    elif traits.get('Treebond'):
        if askChoice('Would you like to use Treebond to transfer Damage?',['Yes','No'],["#01603e","#de2827"]) == 1:
            transfer_to_list = [getMage(), card]
            TBDlg = create_double_list_dialog(transfer_to_list,[], 'Treebond','Select (click on) where the damage will come from', 'Move the target to receive the damage below', min = 1, max = 1)
            transfer_from_target = TBDlg.show()
            if not transfer_from_target:
                transfer_from_target = TBDlg.list
            transfer_to_target = TBDlg.bottomList
            if transfer_from_target and transfer_to_target:
                damage_transfer(transfer_from_target, transfer_to_target)
    return

def resolve_death_link(card, traits):
    if traits.get('Deathlink'):
        DL = getSpecificAttachment(card, 'Death Link')
        target = card
        remoteCall(DL.controller, 'death_link_prompt', [target])
    return

def death_link_prompt(target):
    if me.Damage > 0:
        if askChoice('Would you like to transfer Damage to {} with Death Link?'.format(target.name),['Yes','No'],["#01603e","#de2827"]) == 1:
            transfer_to_target = [target]
            transfer_from_target = [getMage()]
            damage_transfer(transfer_from_target, transfer_to_target, 'Death Link', 2)
    return

def resolve_drown(card):
    mute()
    if card.name == 'Drown':
        card.markers[Suffocate] += 1
    return

def resolveFaithHealersStaff(card):
    mute()
    if card.name == 'Faith Healer\'s Staff' and card.isFaceUp:
        choice = askChoice("Faith Healer\'s Staff: Would you like to pay 1 mana to heal a Living creature in this zone?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            if me.Mana < 1:
                whisper('You do not have enough mana to use Faith Healer\'s Staff!')
                return
            # Get the Mage's zone
            mage = getMage()
            zoneCards = getAllCardsInZoneList(mage)
            # Filter for Living creatures in the zone
            livingList = []
            for zoneCard in zoneCards:
                if zoneCard.controller == me:
                    traits = getTraits(zoneCard)
                    if traits.get('Living', False) and (zoneCard.Type == 'Creature' or ('Mage' in zoneCard.Subtype and zoneCard.Type == 'Creature')):
                        livingList.append(zoneCard)
            if not livingList:
                notify("No Living creatures found in {}'s zone.".format(mage.name))
                return
            # Let player select a creature
            selectedList = create_card_dialog(livingList, 'Select a Living creature to heal', 0, 1)
            if selectedList:
                me.Mana -= 1
                notify("{} pays 1 mana to use Faith Healer\'s Staff.".format(me))
                selectedCard = selectedList[0]
                # Roll 1 attack die and get effect roll (effect roll ignored)
                attackRoll, effectRoll = rollDice(1)
                # Calculate healing based on normal and critical damage
                healingAmount = attackRoll[2] + 2 * attackRoll[3] + attackRoll[4] + 2 * attackRoll[5]
                # Heal the creature
                damage = get_total_damage_markers(selectedCard)
                if damage > 0:
                    subDamageAmount(selectedCard, min(healingAmount, damage))
                    notify("Faith Healer's Staff heals {} for {} damage.".format(selectedCard, min(healingAmount, damage)))
                else:
                    notify("{} is at full health.".format(selectedCard))
            else:
                notify("No creature selected for Faith Healer\'s Staff.")
        else:
            notify("{} chooses not to use Faith Healer\'s Staff.".format(me))
    return

def resolveAsyranRobes(card):
    mute()
    if card.name == 'Asyran Robes' and card.isFaceUp:
        choice = askChoice("Asyran Robes: Would you like to move 1 damage from a friendly Living creature to your Mage?", ['Yes', 'No'], ['#0000FF', '#FF0000'])
        if choice == 1:
            # Get the Mage's zone
            mage = getMage()
            zoneCards = getAllCardsInZoneList(mage)
            # Filter for friendly Living creatures with damage
            damagedLivingList = []
            for zoneCard in zoneCards:
                if zoneCard.controller == me:
                    traits = getTraits(zoneCard)
                    if (traits.get('Living', False) and 
                        (zoneCard.Type == 'Creature' or ('Mage' in zoneCard.Subtype and zoneCard.Type == 'Creature')) and 
                        get_total_damage_markers(zoneCard) > 0):
                        damagedLivingList.append(zoneCard)
            if not damagedLivingList:
                notify("No damaged Living creatures found in {}'s zone.".format(mage))
                return
            # Show simple selection dialog
            selectedList = create_card_dialog(damagedLivingList, 'Select a Living creature to move 1 damage from', 0, 1)
            if selectedList:
                selectedCard = selectedList[0]
                # Transfer 1 damage to the Mage
                subDamageAmount(selectedCard, 1)
                addDamageAmount(mage, 1)
                notify("Asyran Robes moves 1 damage from {} to {}.".format(selectedCard, mage))
            else:
                notify("No creature selected for Asyran Robes.")
        else:
            notify("{} chooses not to use Asyran Robes.".format(me))
    return