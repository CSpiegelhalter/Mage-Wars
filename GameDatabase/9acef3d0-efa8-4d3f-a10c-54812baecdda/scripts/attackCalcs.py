import math

def canDeclareAttack(card, target=None):
    mute()
    if not card.isFaceUp: return False
    if ((card.Type == 'Creature' or
        ('Conjuration' in card.Type and card.Attack != '') or
        ('Enchantment' in card.Type and card.Attack != '') or
        ('Incantation' in card.Type and card.Attack != '')) and
        ('Incapacitated' not in getTraits(card))):
            return True

def canDeclareHeal(card):
    canHeal = False
    if card.bAttack != '' or card.Attack != '':
        attackList = getAttackList(card)
        for attack in attackList:
            if attack.get('Heal'):
                canHeal = True
    return canHeal

def canDeclareReconstruct(card):
    canRCon = False
    if card.bAttack != '' or card.Attack != '':
        attackList = getAttackList(card)
        for attack in attackList:
            if attack.get('Reconstruct'):
                canRCon = True
    return canRCon

def checkAttackTargetInRange(attack, targetingCard, targetedCard):
    mute()
    rangeMin = attack['range'][0]
    rangeMax = attack['range'][1]
    if targetingCard.Type in ['Incantation','Equipment']:
        mage = getMage()
        distance = cardGetDistance(mage, targetedCard)
    else:
        distance = cardGetDistance(targetingCard, targetedCard)
    if distance <= rangeMax and distance >= rangeMin:
        return True
    return False

def genericAttack(group = None, x = None, y = None):
    attack = chooseAttack()
    dice = -1
    if attack:
        dice = attack.get('dice',-1)
        attack['unmodDice'] = dice
    if dice >= 0:
        rollDice(dice)

def computeAttack(attack, targetingCard = None, targetedCard = None):#TODO redo and sort by melee +, ranged + 
    mute()
    debug('computeAttack')
    debug('attack: '+attack['name'])
    debug('dice: '+str(attack['dice']))
    attackerTraits = getTraits(targetingCard)
    defenderTraits = getTraits(targetedCard)

    adjAttack = adjustFromRangeType(attack, targetingCard, attackerTraits)
    debug('dice from Range: '+str(adjAttack['dice']))
    adjAttack = adjustFromDamageType(attack, attackerTraits, defenderTraits)
    debug('dice from Damage Type: '+str(adjAttack['dice']))
    adjAttack = adjustFromAttackerTraits(attack, targetingCard, targetedCard) #WIP
    debug('dice from attTraits: '+str(adjAttack['dice']))
    adjAttack = adjustFromDefenderTraits(attack, targetingCard, targetedCard)#WIP
    debug('dice from defTraits: '+str(adjAttack['dice']))
    adjAttack = adjustForSpecificTargets(attack, attackerTraits, defenderTraits, targetingCard, targetedCard)#WIP
    debug('dice from Target: '+str(adjAttack['dice']))
    adjAttack = adjustDiceFromTokens(attack, targetingCard, targetedCard, attackerTraits)
    debug('dice from Tokens: '+str(adjAttack['dice']))
    adjAttack = adjustDiceForMageAbs(attack, targetingCard, targetedCard)
    debug('dice from Mage: '+str(adjAttack['dice']))
    adjAttack = adjustDiceForGrimsonRange(attack, targetingCard, targetedCard)
    debug('dice from Grimson: '+str(adjAttack['dice']))
    adjAttack = adjustDiceForEvents(attack, targetingCard, targetedCard)
    debug('dice from Events: '+str(adjAttack['dice']))
    adjAttack = adjust_dice_for_strongest(attack, targetingCard, targetedCard, attackerTraits)
    debug('dice from Strongest: '+str(adjAttack['dice']))
    if adjAttack.get('Autonomous'):
        adjAttack['dice'] = attack['unmodDice']
    if adjAttack['dice'] <1:
        adjAttack['dice'] = 1
    return adjAttack

def adjustForCharging(attack, targetingCard):
    mute()
    attackerTraits = getTraits(targetingCard)
    charge = False
    if (targetingCard and 'Charge' in attackerTraits 
        and attack['range type'] == 'Melee'
        and not hasAttackedThisTurn(targetingCard)):
            chargeChoice = askChoice('Apply charge bonus (+{}) to this attack?'.format(str(attackerTraits['Charge'])),['Yes','No'],["#01603e","#de2827"])
            if chargeChoice == 1:
                rememberCharge(targetingCard) 
                attack['dice']+=attackerTraits['Charge']
                charge = True
    return attack, charge

def adjustFromRangeType(attack, targetingCard, traits):
    mute()
    if 'Debilitate' in traits or 'Infernia' in traits and attack.get('range type') == 'Melee':
        return attack
    if attack['range type'] in traits and not attack.get('strikes',1)>1:#timesHasUsedAttack(targetingCard,attack['name'])
        attack['dice']+=traits[attack['range type']]
    return attack

def adjustFromDamageType(attack, attackerTraits, defenderTraits):
    #TODO: track the amount of times it happens in an attack action/round
    #TODO: Deal with immunity
    mute()
    if 'damage type' in attack:        
        if attack['damage type'] in defenderTraits:
            attack['dice']+= defenderTraits[attack['damage type']]
    if 'Fireshaper' in attackerTraits and attack.get('damage type') == 'Flame' and attack.get('range type') in ['Melee', 'Ranged']:
        attack['dice']+=1
    elif 'LightningRing' in attackerTraits and attack.get('damage type') == 'Lightning' and attack.get('range type') in ['Melee', 'Ranged']:
        attack['dice']+=1
    elif 'dawnbreakerRing' in attackerTraits and attack.get('damage type') == 'Light' and attack.get('range type') in ['Melee', 'Ranged']:
        attack['dice']+=1
    elif 'Hellscape' in attackerTraits and attack.get('damage type') == 'Flame':
        attack['dice'] +=1 
    #ring of healing
    return attack

def adjustFromAttackerTraits(attack, targetingCard, targetedCard):
    mute()
    attackerTraits = getTraits(targetingCard)
    defenderTraits = getTraits(targetedCard)
    if ('Bloodthirsty' in attackerTraits 
        and defenderTraits.get('Living',True)
        and targetedCard.Type == 'Creature' 
        and attack.get('range type','None') == 'Melee' 
        and not 'Spell' in attack
        and not attack.get('strikes',1)>1):
            if 'Mage' in targetedCard.Subtype and targetedCard.controller.Damage > 0:
                #Bloodthirsty
                attack['dice']+=attackerTraits['Bloodthirsty']
            elif defenderTraits['Living'] and targetedCard.markers[Damage]:
                #Bloodthirsty
                attack['dice']+=attackerTraits['Bloodthirsty']
    if 'Rage' in attackerTraits and attack['range type']=='Melee' and not attack.get('strikes',1)>1:
        #Melee +
        attack['dice']+= targetingCard.markers[Rage]
    if 'Agony' in attackerTraits and not 'Spell' in attack:
        attack['dice']-=2
    if 'ShallowSea' in attackerTraits:
        if 'Aquatic' in targetingCard.Subtype and attack['range type'] == 'Melee' and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
            #Melee +1
            attack['dice']+=1
        elif 'Aquatic' not in targetingCard.Subtype and not 'Spell' in attack and ((attackerTraits.get('Flying') and attack.get('range type') == 'Melee') or not attackerTraits.get('Flying')):
            attack['dice']-=1
    if 'tangleRoot' in attackerTraits and attack.get('range type') == 'Melee':
        tangleR = getSpecificAttachment(targetingCard, 'Tangleroot')
        attack['dice'] -= tangleR.markers[Dissipate]
    if 'steepHill' in attackerTraits and not attackerTraits.get('Flying') and attack.get('range type') == 'Ranged' and not attack.get('strikes',1)>1:
        #Ranged +1
        attack['dice']+=1
    if attack.get('academyWeapon') and int(targetingCard.level)>5:
        attack['dice']+=1
    if 'ringOfTides' in attackerTraits and checkInit() and attack.get('damage type') == 'Hydro':
        attack['dice']+=1
    if 'Redclaw' in attackerTraits and 'RedClaw' not in targetingCard.name and 'Canine' in targetingCard.Subtype and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        #Melee +1
        attack['dice']+=1
    if 'Vengeful' in attackerTraits and attack.get('range type') == 'Melee' and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        #Melee +1
        attack['dice']+=1
    if 'StandardBearer' in attackerTraits and attack.get('range type') == 'Melee' and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        standardBearer = getCard('Standard Bearer')
        bearer = Card(int(standardBearer.isAttachedTo))
        if bearer != targetingCard:
            #Melee +1
            attack['dice']+=1
    if 'PressAttack' in attackerTraits and attack.get('range type') == 'Melee' and 'Soldier' in targetingCard.Subtype and targetingCard.controller == me and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        #Melee +1
        attack['dice'] += 1
    if 'MartialMastery' in attackerTraits and (attack.get('range type') == 'Melee' or (attack.get('Spell') and Card(attack.get('originalCardSource')).School in ['Mind'])):
        attack['dice']+=1
    if targetingCard.name == 'Ketsuro Sentinel' and targetingCard.attachments not in ['','[]']:
        attack['dice'] += 1
    return attack

def adjustFromDefenderTraits(attack, targetingCard, targetedCard):
    mute()
    attackerTraits = getTraits(targetingCard)
    defenderTraits = getTraits(targetedCard)
    if 'markedForDeath' in defenderTraits and not hasAttackedTargetThisTurn(targetingCard, targetedCard) :
        attack['dice']+=1
    if 'Aegis' in defenderTraits and not attack.get('Heal') and not attack.get('Drain'):
        attack['dice'] -= defenderTraits['Aegis'][0]
    if 'glancingBlow' in defenderTraits:
        attack['dice'] -=3
    if 'dampCloak' in defenderTraits and not 'Aegis' in defenderTraits and attack.get('range type') == 'Ranged':
        attack['dice'] -=1
    if 'Tundra' in defenderTraits and 'Frost' not in targetedCard.Subtype and 'Frost' in attack.get('damage type','None'):
        attack['dice'] +=1
    if 'forceShield' in defenderTraits:
        FShield = getSpecificAttachment(targetedCard, 'Force Shield')
        FSAegis = FShield.markers[Dissipate]
        if 'Aegis' in defenderTraits:
            if FSAegis > defenderTraits['Aegis'][0]:
                attack['dice'] -= (FSAegis-defenderTraits['Aegis'][0])
        else:
            attack['dice'] -= FSAegis
    return attack

def adjustForSpecificTargets(attack, attackerTraits, defenderTraits,targetingCard, targetedCard):
    mute()
    if 'Target' in attack and canTarget(targetedCard,targetingCard, attack['Target']['target']):
        attack['dice']+=attack['Target']['bonus']
    if 'TigerStance' in attackerTraits and defenderTraits.get('Flying'):
        attack['dice'] +=1
    return attack

def adjustDiceFromTokens(attack, targetingCard, targetedCard, attackerTraits):
    mute()
    '''strongest'''
    #targetED card adjustments
    if (targetedCard.markers[WoundedPrey]
        and not 'Mage' in targetedCard.Subtype
        and ('Animal' in targetingCard.Subtype or 'Johktari Beastmaster' in targetingCard.Name)
        and attack['range type'] == 'Melee'
        and not attack.get('strikes',1)>1
        and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits):
            attack['dice'] += 1
    if targetedCard.markers[AegisToken]:
        attack['dice']-=1
    if targetedCard.markers[scoutToken] and not 'Straywood Scount' in targetedCard.name:
        attack['dice']+=1
    #targetING card adjustments
    if targetingCard.markers[Weak] and not 'Spell' in attack:
        attack['dice']-=targetingCard.markers[Weak]
    if targetingCard.markers[Stagger]:
        attack['dice']-=2
    if targetingCard.controller == me and targetingCard.markers[SirensCall] and checkForSirenMage() and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits and not 'Mage' in targetingCard.Subtype:
        #Melee +2
        attack['dice']+=2
    if targetingCard.markers[Growth] and attack['range type']=='Melee' and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        #Melee +1
        attack['dice']+=targetingCard.markers[Growth]
    if targetingCard.markers[Freeze] and 'Spell' not in attack:
        attack['dice']-=1
    if targetingCard.markers[Charge] and 'Lightning Raptor' in targetingCard.name:
        attack['dice']+= targetingCard.markers[Charge]
    if targetingCard.markers[Grapple] and attack['range type']=='Melee':
        attack['dice']-=2
    if targetingCard.markers[Wrath] and attack['range type']=='Melee' and not attack.get('strikes',1)>1 and not 'Infernia' in attackerTraits and not 'Debilitate' in attackerTraits:
        #Melee +1
        attack['dice']+=targetingCard.markers[Wrath]
    if targetingCard.markers[HolyAvenger] and attack.get('range type') == 'Melee' and not timesHasOccurred("Holy Avenger",targetingCard.controller):
        attack = holyAvengerBuff(attack, targetingCard, targetedCard)
    if targetingCard.markers[Pet] and not attack.get('strikes',1)>1:
        mage = getMage()
        otherCards = getOtherCardsInZoneList(targetingCard)
        for otherCard in otherCards:
            if otherCard == mage:
                attack['dice']+=1
    return attack

def adjustDiceForMageAbs(attack, targetingCard, targetedCard):
    '''JBM conditional ranged'''
    mute()
    if attack['range type'] == 'Ranged' and not 'Spell' in attack and 'Johktari Beastmaster' in targetingCard.name and not attack.get('strikes',1)>1:
        attack['dice']+=1
    return attack

def adjustDiceForGrimsonRange(attack, targetingCard, targetedCard):
    if 'Grimson' in targetingCard.name and 'Thundergun' in attack['name']:
        distance = cardGetDistance(targetingCard,targetedCard)
        attack['dice'] -= (distance-1)
    return attack
        
def adjustDiceForEvents(attack, targetingCard, targetedCard):
    if attack.get('name') == 'Serrated Edge' and not hasAttackedThisRound(targetingCard):
        eventList = getEventList('Round')
        for e in eventList:
            if e[0] == 'Attack' and Card(e[1][1]) == targetedCard and 'Animal' in Card(e[1][0]).Subtype and Card(e[1][0]).controller == targetingCard.controller and e[1][3] > 0:
                attack['dice'] += 1
                break
    return attack

def getAttackList(card):
    mute()
    if card.Attack != '':
        rawAttack = eval(card.Attack)
    else:
        rawAttack = None
    attackList = []
    if rawAttack:
        if isinstance(rawAttack, tuple):
            for attack in rawAttack:
                attackList += [attack]
        else:
            attackList = [rawAttack]
    return attackList

def checkAffordAttackCost(attack, targetingCard):
    mute()
    manaPool = targetingCard.markers[Mana]+me.Mana
    if attack.get('Cost') > manaPool:
        return False
    else:
        return True

def bestowAttackSpell(card, target = None):
    mute()
    if card.bAttack != '' and card.Type in ['Attack','Incantation'] and not target:
        mage = getMage()
        addToAttackLine(card, mage)
    elif card.bAttack != '' and card.Type in ['Attack','Incantation','Enchantment'] and target:
        addToAttackLine(card, target)
    return

def addToAttackLine(card, target):
    targetAttackList = getAttackList(target)
    newAttack = eval(card.bAttack)
    newAttackList = []
    if isinstance(newAttack, tuple):
        for attack in newAttack:
            newAttackList += [attack] 
    else:
        newAttackList = [newAttack]
    for newAttack in newAttackList:
        newAttack['originalCardSource'] = card._id
        targetAttackList.append(newAttack)
    target.Attack = str(targetAttackList).strip('[]')

def addEqAttacksToMage(card):
    mute()
    if card.bAttack != '':
        mage = getMage()
        addToAttackLine(card, mage)
    return

def removeBestowedAttack(card, target = None):
    if card.bAttack != '' and card.Type in ['Equipment', 'Attack', 'Incantation','Enchantment'] and not target:
        mage = getMage()
        removeFromAttackLine(card, mage)
    elif card.bAttack != '' and card.Type in ['Attack','Incantation','Enchantment'] and target:
        removeFromAttackLine(card, target)
    return

def removeFromAttackLine(card, target):
    targetAttack = getAttackList(target)
    oldAttack = eval(card.bAttack)
    oldAttackList = []
    if isinstance(oldAttack, tuple):
        for attack in oldAttack:
            oldAttackList += [attack]
    else:
        oldAttackList = [oldAttack]
    for oldAttack in oldAttackList:
        oldAttack['originalCardSource'] = card._id
        if oldAttack in targetAttack:
            targetAttack.remove(oldAttack)
    target.Attack = str(targetAttack).strip('[]')
    return

def forcefieldBlock(attack, attacker, defender):
    mute()
    attachmentList = getAttachedCards(defender)
    if len(attachmentList)>0:
        for card in attachmentList:
            if card.name == 'Forcefield' and card.markers[FFToken] and card.isFaceUp:
                card.markers[FFToken] -= 1
                notify("The forcefield absorbs the attack!\n".format(attacker.name.split(',')[0]))
                rememberAttackUse(attacker,defender,attack['name'],0)
                return True
    else:
        return False
    
def symbioticOrbDefense(attack, attacker, defender):
    mute()
    defTraits = getTraits(defender)
    if ('symbOrb' in defTraits or 'symbOrb' in defender.zfTraits) and not timesHasOccurred('symbOrb', me) and attack.get('range type') == 'Melee':
        if payForSymbioticOrb():
            for card in table:
                if card.name == 'Symbiotic Orb' and card.markers[Ready] and card.isFaceUp and defender.controller == card.controller:
                    toggleReady(card)
                    notify("Symbiotic Orb protects {} from the attack!".format(defender))
                    rememberAttackUse(attacker, defender, attack['name'], 0)
            return True
    return False

def checkEnchantmentDefenses(attack, attacker, defender):
    mute()
    attachmentList = getAttachedCards(defender)
    if len(attachmentList)>0:
        for card in attachmentList:
            if card.name == 'Block' and not attack.get('Unavoidable') and card.isFaceUp:
                notify("{}'s attack is blocked!\n".format(attacker.name.split(',')[0]))
                rememberAttackUse(attacker,defender,attack['name'],0)
                return True
            if card.name == 'Redirect' and not attack.get('Unavoidable') and card.isFaceUp:
                notify("{}'s attack is redirected!\n".format(attacker.name.split(',')[0]))
                rememberAttackUse(attacker,defender,attack['name'],0)
                addDamageAmount(attacker,2)
                return True
            if card.name == 'Fumble' and not attack.get('Unavoidable') and card.isFaceUp and not attack.get('Spell'):
                notify("{} fumbles the attack!\n".format(attacker.name.split(',')[0]))
                rememberAttackUse(attacker,defender,attack['name'],0)
                return True
            if card.name == 'Dodge' and not attack.get('Unavoidable') and card.isFaceUp:
                if getTotalCardLevel(defender) < 3:
                    notify("{} dodges the attack!\n".format(defender.name.split(',')[0]))
                    rememberAttackUse(attacker,defender,attack['name'],0)
                    return True
                else:
                    attackRoll, effectRoll = rollDice(0)
                    if effectRoll > 6:
                        notify("{} dodges the attack!\n".format(defender.name.split(',')[0]))
                        rememberAttackUse(attacker,defender,attack['name'],0)
                        return True
                    else:
                        return False
            if card.name == 'Tiger Stance'and not attack.get('Unavoidable') and card.isFaceUp:
                choice = parry(card)
                if choice == 1 and rollDice(0)[1] > 6:
                    notify("{} dodges the attack!\n".format(defender.name.split(',')[0]))
                    rememberAttackUse(attacker,defender,attack['name'],0)
                    return True
                else:
                    return False
    return False

def parry(card):
    mage = getMage()
    if mage.markers[Ki] > 1:
        target = Card(eval(card.isAttachedTo))
        choice = askChoice('Would you like to pay 2 Ki to give {} a 7+ defense?'.format(target.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            mage.markers[Ki] -= 2
            notify('{} attempts to dodge!'.format(card))
    return choice

def checkReverseAttack(attack, attacker, defender):
    mute()
    attachmentList = getAttachedCards(defender)
    if len(attachmentList)>0:
        for card in attachmentList:
            if card.name == 'Reverse Attack' and not attack.get('Unavoidable') and card.isFaceUp:
                notify("{}'s attack is magically reversed!\n".format(attacker.name.split(',')[0]))
                rememberAttackUse(attacker,defender,attack['name'],0)
                return True
    return False

def checkChosenDefenses(attack, attacker, defender):
    mute()
    if not attack.get('Unavoidable') and not 'Incapacitated' in getTraits(defender):
        defenseList = getDefenseList(attack, defender)
        if defenseList:
            defenseList = getDefenseModifiers(defenseList, defender)
            # Formatting Choice box
            queryList = ['{}\nSuccess Rate {} | Uses Remaining: {}\nModifiers: {}'.format(
                d['name'].center(68, ' '),
                str(round(((13 - d.get('Threshold')) / 12.0) * 100, 1)) + "%" if d.get('Threshold') else "Auto",
                "Infinite" if d.get('Uses', 0) >= 10 else str(d.get('Uses', 0) - timesHasUsedDefense(defender, d)),
                str(d.get('Modifier')).strip("'[]").replace("'", "")
            ) for d in defenseList]
            colors = ["#996600" for d in queryList]
            queryList.append('I won\'t roll defense')
            colors.append("#000000")
            choice = askChoice('Would you like to use a defense?', queryList, colors)
            
            # Hitting X or choosing "no defense"
            if choice == 0 or choice == len(queryList):
                return False
            
            # Get the chosen Defense
            defense = defenseList[choice - 1]
            
            # Handle costs (mana, Ki, etc.)
            if defense.get('Cost', 0) and me.Mana > defense.get('Cost', 0):
                choice = askChoice("Pay {} Mana to use your defense?".format(defense.get('Cost')), ["Yes", "No"], ["#01603e", "#de2827"])
                if choice == 1:
                    me.Mana -= defense.get('Cost')
                    if defense.get('name') == 'Deflect':
                        toggleDeflect(defender)
                else:
                    return False

            # Handle Symbiotic Orb payment
            if defense.get('name') == 'Symbiotic Orb':
                if not payForSymbioticOrb():
                    return False
            
            # Handle Sohei Disciple Ki Cost from Mage
            if defense.get('name') == 'Sohei Disciple' and defender.name != 'Sohei Disciple':
                if not payForSoheiDisciple():
                    return False
            
            # Toggle Ready marker on the source if not Infinite
            if defense.get('Uses', 0) < 10:
                source_card = Card(defense['Source']) if defense.get('Source') else defender
                if source_card.markers[Ready]:
                    toggleReady(source_card)
            
            # Record the use and roll for success
            rememberDefenseUse(defender, defense)
            notify("{} attempts to avoid the attack".format(defender))
            damageRoll, defenseRoll = rollDice(0)
            if defenseRoll >= defense.get('Threshold', 13):
                notify("{} succeeds in its defense attempt! Attack avoided!\n".format(defender))
                rememberAttackUse(attacker, defender, attack['name'], 0)
                return True
            else:
                notify("{} fails to defend itself...\n".format(defender))
                return False
    return False

def getDefenseList(attack, defender):
    mute()
    defenseList = []
    defTraits = getTraits(defender)

    # Bestowed Defenses from traits (e.g., enchantments or external sources)
    if 'Defense' in defTraits:
        for bDefense in defTraits['Defense']:
            bDefense['Source'] = None  # Default source
            
            # Check attached cards and table cards
            for card in (getAttachedCards(defender) + [c for c in table if c.controller == defender.controller and c != defender]):
                card_traits = eval(card.bTraits) if card.bTraits else {}
                if 'Defense' in card_traits and bDefense in card_traits['Defense']:
                    bDefense['Source'] = card._id
                    break
            else:  # If no source found, default to defender
                bDefense['Source'] = defender._id
            
            # Add if usable and restriction matches or doesnt exist
            if timesHasUsedDefense(defender, bDefense) < bDefense['Uses']:
                if not bDefense.get('Restriction') or attack.get('range Type') == bDefense.get('Restriction'):
                    defenseList.append(bDefense)
    
    # Native Defense from Stat_Defense
    if defender.Stat_Defense != '':
        natDef = eval(defender.Stat_Defense)
        if (timesHasUsedDefense(defender, natDef) < natDef['Uses'] and
            not (natDef.get('Restriction') and attack.get('range Type') != natDef.get('Restriction')) and
            natDef.get('Cost', 0) <= me.mana):
            natDef['Source'] = defender._id
            defenseList.append(natDef)
    
   # Check for Sohei Disciple in the same zone
    mage = getMage()
    othersInZone = getOtherCardsInZoneList(defender)
    if defender.Stat_Defense != 'Sohei Disciple':
        for card in othersInZone:
            if (card.name == 'Sohei Disciple' and card.controller == defender.controller and card.isFaceUp and 'Incapacitated' not in getTraits(card) and mage.markers[Ki] >= 2):
                sohei_defense = {'Threshold': 9, 'Uses': 1000, 'name': 'Sohei Disciple', 'Source': card._id}
                defenseList.append(sohei_defense)
                break  # Only one Sohei Disciple need apply per zone
    return defenseList

def getDefenseModifiers(defenseList, defender):
    mute()
    defTraits = getTraits(defender)
    for defense in defenseList:
        if defense.get('name') == 'Dancing Scimitar':
            continue
        defense['Modifier'] =[]
        if defender.markers[Daze]:
            defense['Threshold'] +=2
            defense['Modifier'] += ['Dazed']
        if 'Restrained' in defTraits:
            defense['Threshold'] += 2
            defense['Modifier'] += ['Restrained']
        if defender.name == 'Dwarf Panzergarde' and defender.markers[Guard] and defense.get('Name') == 'Panzergarde':
            defense['Threshold']-=3
        if 'defenseRing' in getTraits(defender):
            defense['Threshold']-=1
        if 'runeOfShielding' in getTraits(defender):
            defenseCard = getCard(defense.get('name'))
            if defenseCard.markers[RuneofShielding]:
                defense['Threshold'] -=2
    return defenseList

def damageReceiptMenu(attack, attacker, defender, damageRoll, dManaDrain, appliedDmg, actualEffect):
    mute()
    nonBlanks, onesRolled= incorporealDamageDisplay(damageRoll,attack,defender)
    if 'Swarm' in defender.Subtype and not 'Zone Attack' in attack:
            appliedDmg = 1

    totalDice = damageRoll[0]+damageRoll[1]+damageRoll[2]+damageRoll[3]+damageRoll[4]+damageRoll[5]
    normalDamage = damageRoll[2] + 2* damageRoll[3] # calculate the results for Normal Damage
    criticalDamage = damageRoll[4] + 2* damageRoll[5] # calculate the results for Critical Damage
    effectString = formatEffectString(actualEffect)


    choice = askChoice('{}\'s attack will inflict {} damage {}on {}.{} ({} normal damage and {} critical damage were rolled.){}{}\nApply these results?'.format(attacker.Name,
                                                                                                    appliedDmg,
                                                                                                    ('and an effect ({}) '.format(effectString)) if effectString else '',
                                                                                                    defender.Name,
                                                                                                    (' It will also drain {} mana from {}.'.format(
                                                                                                            str(dManaDrain),defender.controller.name) if dManaDrain else ''),
                                                                                                    normalDamage,
                                                                                                    criticalDamage,
                                                                                                    ('({}/{} dice rolled damage.) '.format(str(nonBlanks),str(totalDice)) if nonBlanks else ''),
                                                                                                    ('({}/{} dice rolled ones.) '.format(str(onesRolled),str(totalDice)) if onesRolled else '')),
                    ['Yes',"Other Damage Amount",'No'],
                    ["#01603e","#FF6600","#de2827"])
    if choice == 1:
            return appliedDmg, actualEffect 
    elif choice == 2:
            appliedDmg = askInteger("Apply how much damage?",appliedDmg)
            return appliedDmg, actualEffect
    else:
            notify('{} has elected not to apply auto-calculated battle results\n'.format(me))
            whisper('(Battle calculator not giving the right results? Report the bug to us so we can fix it!)')
            return None, None

def payForSymbioticOrb():
    elligibleC = forceCardsWithDissipate()
    if me.Mana >= 3 and len(elligibleC)>0:
        choice = askChoice('Symbiotic Orb: Would you like to pay Mana or a Dissipate token to avoid the attack?',['Mana (3)', 'Dissipate Token', 'No'],["#01603e","#ffd966","#de2827"])
        if choice == 1:
            paymentType = 'Mana'
        elif choice == 2: 
            paymentType = 'Dissipate'
        else:
            paymentType = None
    elif me.Mana < 3 and len(elligibleC)>0:
        choice = askChoice('Symbiotic Orb: Would you like to pay a Dissipate token to avoid the attack?',['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            paymentType = 'Dissipate'
        else:
            paymentType = None
    elif me.Mana >= 3 and len(elligibleC) == 0:
        choice = askChoice('Symbiotic Orb: Would you like to pay 3 Mana to avoid the attack?',['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            paymentType = 'Mana'
        else:
            paymentType = None
    if paymentType == 'Mana':
        me.Mana -= 3
        rememberPlayerEvent('symbOrb',me)
        notify('{} pays 3 Mana to avoid the attack!'.format(me))
        return True
    elif paymentType == 'Dissipate':
        dialog = cardDlg(elligibleC)
        dialog.title = 'From where would you like to take a dissipate?'
        selected = dialog.show()
        selectedCard = selected[0]
        selectedCard.markers[Dissipate] -=1
        rememberPlayerEvent('symbOrb',me)
        notify('{} takes a Dissipate Token from {} to avoid the attack!'.format(me, selectedCard))
        return True
    else:
        return False

def payForSoheiDisciple():
    choice = askChoice('Would you like to pay 2 Ki for a defense?',['Yes', 'No'],["#01603e","#de2827"])
    if choice == 1:
        mage = getMage()
        mage.markers[Ki] -=2
        return True
    else:
        return False

def voltaricShield(actualDmg, defender):
    mute()
    notify("The Voltaric Shield absorbs {} points of damage!\n".format(str(min(actualDmg,3))))
    actualDmg = max(actualDmg-3,0)
    defender.markers[VoltaricON] = 0
    defender.markers[VoltaricOFF] = 1
    return actualDmg

def incorporealDamageCalc(attack, damageRoll, adjustedEffectRoll):
    mute()
    if attack.get('Ethereal'):
        rawDmg = damageRoll[2] +damageRoll[3]+damageRoll[4]+damageRoll[5]
        effect = computeEffect(attack, adjustedEffectRoll)
    else:
        rawDmg = damageRoll[2] +damageRoll[4]
        effect = None
    return rawDmg, effect

def incorporealDamageDisplay(damageRoll,attack,defender,):
    mute()
    defTraits = getTraits(defender)
    if defTraits.get("Incorporeal"):
        if attack.get('Ethereal'):
            nonBlanks = damageRoll[2] +damageRoll[3]+damageRoll[4]+damageRoll[5]
            onesRolled = None
        else:
            nonBlanks = None
            onesRolled = damageRoll[2]+damageRoll[4]
    else:
        nonBlanks = None
        onesRolled = None
    return nonBlanks, onesRolled

def formatEffectString(actualEffect):
    effectStr = ''
    if actualEffect:
        for effect in actualEffect:
            effectStr += effect
    return effectStr

def fortified_resolve_defense(defender, actualDmg):
    mute()
    for attachedCard in getAttachedCards(defender):
        if attachedCard.isFaceUp and "Fortified Resolve" in attachedCard.Name:
            if attachedCard.markers[Charge]>0:
                FRChoice = askChoice("Spend a charge marker to reduce incoming damage by 2?",["Yes","No"],["#01603e","#de2827"])
                if FRChoice == 1:
                    attachedCard.markers[Charge] -= 1
                    actualDmg -= 2
                    notify("{}\'s Fortified Resolve absorbs 2 damage\n".format(me))
    return actualDmg

def manaDrain(defender, attacker, attack, actualDmg):
    mute()
    attTraits = getTraits(attacker)
    if defender.type == "Creature": 
            dManaDrain = (min(attack.get('Mana Drain',0)+attTraits.get('Mana Transfer',0),defender.controller.Mana) if actualDmg else 0)
    else: 
        dManaDrain = ""
    return dManaDrain

def computeRawDamageAndEffects(damageRoll,effectRoll,attack,attacker,defender):
    mute()
    defTraits = getTraits(defender)
    adjustedEffectRoll = adjustEffectRoll(effectRoll,attack,attacker,defender)
    
    if adjustedEffectRoll and 'temperedFaulds' in defTraits:
        adjustedEffectRoll = temperedFaulds(adjustedEffectRoll, attack)

    if defTraits.get("Incorporeal"):
        if 'hydroEthereal' in defTraits and 'Hydro' in attack.get('damage type', 'None'):
            attack['Ethereal'] = True
        damage, effect = incorporealDamageCalc(attack, damageRoll, adjustedEffectRoll)
        return damage, effect
    
    effectiveArmor = computeEffectiveArmor(attack, attacker, defender)
    normalDamage = damageRoll[2] + 2*damageRoll[3]
    criticalDamage = damageRoll[4] + 2*damageRoll[5]
    
    if attack.get('Critical Damage'):
        criticalDamage +=normalDamage
        normalDamage = 0
    
    if defTraits.get('Resilient'):
        normalDamage = 0
    
    if defTraits.get('vetBelt'):
        reduction = min(criticalDamage, 2)
        criticalDamage -= reduction
        normalDamage += reduction
    
    damage = max(normalDamage - effectiveArmor,0) + criticalDamage
    effect = computeEffect(attack, adjustedEffectRoll)
    return damage, effect

def adjustEffectRoll(effectRoll,attack,attacker,defender):
    attackerTraits = getTraits(attacker)
    defenderTraits = getTraits(defender)
    adjEffectRoll = adjustEffectFromDamageType(effectRoll, attack, defender)
    debug('effect from damage type: '+str(adjEffectRoll))
    adjEffectRoll = adjustEffectForSpecificTargets(adjEffectRoll, attack, attacker,attackerTraits, defender, defenderTraits)
    debug('effect from target: '+str(adjEffectRoll))
    adjEffectRoll = adjustEffectFromAttTraits(adjEffectRoll, attack, attacker, attackerTraits, defender)
    debug('effect from attackerTraits: '+str(adjEffectRoll))
    adjEffectRoll = adjustEffectForTough(adjEffectRoll, defender, defenderTraits)
    debug('effect from Tough: '+str(adjEffectRoll))
    adjEffectRoll = adjustEffectForToL(attack, adjEffectRoll)
    debug('effect from Tol:'+str(adjEffectRoll))
    adjEffectRoll = adjustEffectFromDefTraits(adjEffectRoll, attack, defenderTraits)
    debug('effect from defenderTraits:'+str(adjEffectRoll))
    adjEffectRoll = adjust_effect_for_alandell(attackerTraits, adjEffectRoll)
    debug('effect from Alandell:'+str(adjEffectRoll))
    return adjEffectRoll

def adjustEffectFromDamageType(effectRoll, attack, defender):
    #TODO: track the amount of times it happens in an attack action/round
    #TODO: Deal with immunity
    mute()
    defenderTraits = getTraits(defender)
    if 'damage type' in attack:        
        if attack['damage type'] in defenderTraits:
            effectRoll+= defenderTraits[attack['damage type']]
    return effectRoll

def adjustEffectForSpecificTargets(effectRoll, attack, targetingCard, attackerTraits, targetedCard, defenderTraits):
    mute()
    if 'Target' in attack and canTarget(targetedCard,targetingCard, attack['Target']['target']):
        effectRoll+=attack['Target']['bonus']
    if 'TigerStance' in attackerTraits and defenderTraits.get('Flying',False):
        effectRoll+= 1
    return effectRoll

def adjustEffectFromAttTraits(effectRoll, attack, attacker,attackerTraits, defender):
    if 'ringOfTides' in attackerTraits and checkInit(attacker.controller) and attack.get('damage type') == 'Hydro':
        effectRoll +=2
    if 'galeForce' in attackerTraits and attack.get('damage type') == 'Wind':
        effectRoll +=2
    if 'AirGlyph' in attack:
        effectRoll +=4
    if 'iceRing' in attackerTraits and 'Frost' in attack.get('damage type','None'):
        effectRoll +=3
    effectRoll += attack.get('DragonLance',0)
    return effectRoll

def adjustEffectFromDefTraits(effectRoll, attack, defenderTraits):
    if 'Tundra' in defenderTraits and 'Frost' in attack.get('damage type','None'):
        effectRoll +=1
    return effectRoll

def adjust_effect_for_alandell(attackerTraits, effectRoll):
    return effectRoll + attackerTraits.get('AlEffect',0)

def adjustEffectForTough(effectRoll, defender, defTraits):
    if 'Tough' in defTraits:
        effectRoll -= defTraits['Tough']
    if 'Resolute' in defTraits:
        effectRoll -= 2
    if 'Gargoyle Sentry' in defender.name and defender.markers[Guard]:
        effectRoll -=3
    return effectRoll

def adjustEffectForToL(attack, effectRoll):
    if 'manaPaid' in attack:
        effectRoll += attack['manaPaid']
    return effectRoll

def computeEffect(attack, effectRoll):
    mute()
    effects = attack.get('effects')
    if effects:
        highKey = 0
        for key in effects.keys():
            if effectRoll >= key and key > highKey:
                highKey = key
        if highKey > 0:
            appliedEffect = effects[highKey]
        else:
            appliedEffect = None
        return appliedEffect
    else:
        return None

def computeEffectiveArmor(attack, attacker, defender):
    mute()
    defTraits = getTraits(defender)
    attTraits = getTraits(attacker)
    Piercing = 0
    if defender.Stat_Armor == '-':
        return 0
    defenderArmor = computeDefenderArmor(defender, defTraits)
    if 'Piercing' in attTraits:
        Piercing += attTraits['Piercing']
    if 'Piercing' in attack:
        Piercing += attack['Piercing']
    if 'runeOfPrecision' in attTraits and attack.get('range type') == 'Melee':
        attSource = Card(attack['originalCardSource'])
        if attSource.markers[RuneofPrecision]:
            Piercing += 1
    if 'Vengeful' in attTraits and attack.get('range type') == 'Melee':
        Piercing += 2
    if 'fireAtWill' in attTraits and 'Soldier' in attacker.Subtype and attack.get('range type') == 'Ranged' and not attack.get('Spell') and attacker.controller == me:
        Piercing += 2
    if 'ForceArmor' in defTraits:
        Piercing = min(Piercing-2, 0)
    effectiveArmor = max(defenderArmor - Piercing - defender.markers[Corrode],0)
    return effectiveArmor

def computeDefenderArmor(defender, defTraits):
    baseArmor = 0
    additionalArmor = 0
    if defender.Stat_armor != '':
        baseArmor = eval(defender.Stat_Armor)
    if 'Armor' in defTraits:
        additionalArmor = defTraits['Armor']
    if 'Resolute' in defTraits and defender.name != 'Paladin':
        additionalArmor +=2
    if 'Gargoyle Sentry' in defender.name and defender.markers[Guard]:
        additionalArmor +=3
    if 'StandardBearer' in defTraits:
        standardBearer = getCard('Standard Bearer')
        bearer = Card(int(standardBearer.isAttachedTo))
        if bearer != defender:
            additionalArmor +=1
    if 'digIn' in defTraits and 'Soldier' in defender.Subtype and defender.controller == me:
        additionalArmor +=1
    return baseArmor + additionalArmor

def applyDamageAndEffects(attack,attacker, defender, appliedDmg, adjustedEffects, dManaDrain):
    mute()
    attackerTraits = getTraits(attacker)
    defenderTraits = getTraits(defender)
    if 'divineReversal' in defenderTraits:
        appliedDmg = max((appliedDmg-2),0)
        if appliedDmg > 1:
            appliedDmg-=2
        else:
            healCreatureByAmount(defender,2-appliedDmg,defenderTraits)
        notify('Divine Reversal prevents 2 damage and heals {} by 2!'.format(defender))
    drainSiphonLife(appliedDmg,attack,attacker,defender,attackerTraits,defenderTraits)
    vampiricDrain(appliedDmg, attack, attacker, defender, attackerTraits, defenderTraits)
    if appliedDmg:
        appliedDmg = resolveJoinedStrength(defenderTraits, appliedDmg)
        battle_meditation(attacker, defender, attackerTraits, defenderTraits, appliedDmg)
        fortified_resolve_attack(attacker, defender, attackerTraits, defenderTraits, appliedDmg)
        addDamageAmount(defender, appliedDmg)
        notify('{} deals {} damage to {}'.format(attacker, str(appliedDmg), defender))
    if adjustedEffects:
        applyEffects(attacker, defender, adjustedEffects)
    removeLoadTokens(attacker)
    removeLivingArmorTokens(appliedDmg,defender, defenderTraits)
    bloodReaper(appliedDmg, attacker, attackerTraits, defenderTraits)
    demonicLink(appliedDmg, attacker, attackerTraits, defenderTraits)
    jellyReconstruct(appliedDmg, attacker, defender, defenderTraits)
    malakai_fire(attacker, defender, attack, appliedDmg)
    return

def healTarget(attack, attacker, defender):
    spellCostPaid = False
    if attack.get('source type') in ['Incantation', 'Attack']:
        originalSource = Card(attack.get('originalCardSource')) if attack.get('originalCardSource') else None
        if originalSource:
            debug('OS: {}'.format(originalSource))
            spellCostPaid = castSpell(originalSource)
        else:
            spellCostPaid = castSpell(attacker)
        
    elif attack.get('Cost'):
        choice = askChoice('Would you like to pay {} for {}?'.format(str(attack.get('Cost')), attack.get('name')),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1 and checkAffordAttackCost(attack, attacker):
            me.mana -= attack.get('Cost')
            spellCostPaid = True
    if spellCostPaid or not attack.get('Cost'):
        #TODO revealing pb to stop healing?
        '''attachmentList = getAttachedCards(defender)
        oppAttach = None
        for attachment in attachmentList:
            if attachment.controller != me:
                oppAttach = attachment
        if oppAttach:
            remoteCall(oppAttach.controller, 'revealAttachmentQuery', [attacker, defender])'''
        healingDiceRolled = rollD6(attack['dice'])
        displayRoll(healingDiceRolled,0)
        healingAmount = healingDiceRolled[2] + healingDiceRolled[4] + 2* (healingDiceRolled[3] + healingDiceRolled[5])
        defenderTraits = getTraits(defender)
        damageRemaining = get_total_damage_markers(defender)
        healed = healCreatureByAmount(defender, healingAmount,defenderTraits)
        if healed:
            notify("{} heals {} with {}!\n".format(attacker,defender,attack.get('name','a healing Aura')))
            notify('{} heals by {}'.format(defender, min(healingAmount, damageRemaining)))


def reconstructTarget(attack, targetingCard, targetedCard, targetTraits):
    if 'Skeleton' in targetedCard.Subtype:
        spellCostPaid = False
        if attack.get('source type') in ['Incantation']:
            originalSource = Card(attack.get('originalCardSource')) if attack.get('originalCardSource') else None
            if originalSource:
                #debug('OS: {}'.format(originalSource))
                spellCostPaid = castSpell(originalSource)
            else:
                spellCostPaid = castSpell(targetingCard)
        if spellCostPaid or not attack.get('Cost'):
            healingDiceRolled = rollD6(attack['dice'])
            displayRoll(healingDiceRolled,0)
            healingAmount = healingDiceRolled[2] + healingDiceRolled[4] + 2* (healingDiceRolled[3] + healingDiceRolled[5])
            healed = healCreatureByAmount(targetedCard, healingAmount, targetTraits, 'Reconstruct')
    return

def healCreatureByAmount(creature, amount,creatureTraits = None,reason = None):
    damageRemaining = get_total_damage_markers(creature)
    debug('damageRemaining: {}'.format(damageRemaining))
    if not ('Deathlock' in creatureTraits or 'Finite Life' in creatureTraits or 'Sardonyx' in creatureTraits or 'darkfenneOwl' in creatureTraits) and creatureTraits.get('Living'):
        if damageRemaining and reason == 'Vamp':
            notify('{} has a Vampiric Attack!\n{} heals {} through vampirism'.format(creature,creature, amount))
        elif damageRemaining and reason == 'lifeDrain':
            notify('{} drains {} life from their victim!'.format(creature, amount))
        elif damageRemaining and reason == 'Madrigal':
            notify('Healing Madrigal heals {}!'.format(creature))
        elif damageRemaining and reason == 'Water Glyph':
            notify('{} pays 2 mana and heals {} by {} with the Water Glyph'.format(me, creature, min(damageRemaining, amount)))
        subDamageAmount(creature,amount)
        return True
    elif damageRemaining and reason == 'Reconstruct':
        notify('{} Reconstructs by {}!'.format(creature, amount))
        subDamageAmount(creature,amount)
        return True
    else:
        notify('{} cannot heal because their life is Finite!'.format(creature))
        return False

def healPlayerByAmount(amount, reason = None):
    mage = getMage()
    mageTraits = getTraits(mage)
    if not ('Deathlock' in mageTraits or 'Finite Life' in mageTraits or 'Sardonyx' in mageTraits or 'darkfenneOwl' in mageTraits):
        if reason == 'BR':
            notify('The Blood Reaper\'s demonic power heals the {}!'.format(mage))
        if reason == 'DL':
            notify('The Demonic Link {} has formed heals them for {}'.format(mage, amount))
        subDamageAmount(mage,amount)
        return True
    else:
        notify('{} cannot heal because their life is Finite!'.format(mage))
        return False

def healingCharm(card):
    defenderTraits = getTraits(card)
    healingDiceRolled = rollD6(4)
    displayRoll(healingDiceRolled,0)
    healingAmount = healingDiceRolled[2] + healingDiceRolled[4] + 2* (healingDiceRolled[3] + healingDiceRolled[5])
    damageRemaining = get_total_damage_markers(card)
    healed = healCreatureByAmount(defender, healingAmount,defenderTraits)
    if healed:
        notify("Healing Charm heals {}!\n".format(card))
        notify('{} heals by {}'.format(card, min(healingAmount, damageRemaining)))
    return

def akirosFavor(attacker, damageRoll,effectRoll, previousStep):
    akiroF = getSpecificAttachment(attacker, 'Akiro\'s Favor')
    if akiroF.markers[Ready]:
        newDamageRoll = damageRoll
        newEffectRoll = effectRoll
        if previousStep == 'rollToMissStep':
            choice = askChoice("You have Akiro's Favor! Would you like to re-roll your miss?",["Re-roll Effect Die","Do not Re-roll"],["#ff0000","#171e78"])
            if choice == 1:
                notify("With Akiro looking over their shoulder {} has decided to re-roll the Daze chance!\n".format(me))
                newEffectRoll = rollD12()
                toggleReady(akiroF)
            else:
                effectRoll = effectRoll
        elif previousStep == 'rollDiceStep':
            choice = askChoice("You have Akiro's Favor! What would you like to re-roll?",["Re-roll Attack Dice","Re-roll Effect Die","Do not Re-roll"],["#ff0000","#ebc815","#171e78"])
            if choice == 1:
                notify("With Akiro looking over their shoulder {} has decided to re-roll the Attack Dice!\n".format(me))
                newDamageRoll = rollD6(sum(damageRoll))
                newEffectRoll = effectRoll
                toggleReady(akiroF)
            elif choice == 2:
                notify("With Akiro looking over their shoulder {} has decided to re-roll the Effect Die!\n".format(me))
                newEffectRoll = rollD12()
                toggleReady(akiroF)
        displayRoll(newDamageRoll,newEffectRoll)
        return newDamageRoll, newEffectRoll
    else:
        return damageRoll,effectRoll

def glovesOfSkillRR(damageRoll, effectRoll):
    choice = askChoice("You have Gloves of Skill! Would you like to reroll your attack dice?",["Re-roll Attack Dice","Do not Re-roll"],["#ff0000","#171e78"])
    if choice == 1:
        notify("With exceptional skill bestowed by their gloves, {} has decided to re-roll the Attack Dice!\n".format(me))
        newDamageRoll = rollD6(sum(damageRoll))
        rememberPlayerEvent('Gloves of Skill',me)
        displayRoll(newDamageRoll,effectRoll)
    else:
        newDamageRoll = damageRoll
    
    return newDamageRoll

def temperedFaulds(effect, attack):
    tempF = getCard('Tempered Faulds')
    newEffectRoll = effect
    effects_range = attack.get('effects')
    if tempF.markers[Ready]:
        choice = askChoice('Would you like to reroll the effect die? Current roll: {}'.format(str(effect)),['Yes','No'],["#01603e","#de2827"])
        if choice == 1:
            notify('The effect is rerolled because of the Tempered Faulds')
            newEffectRoll = rollD12()
            toggleReady(tempF)
            attackRoll = [0,0,0,0,0,0]
            displayRoll(attackRoll,newEffectRoll)
    return newEffectRoll

#TODO refactor this some day
def buffWithGlyphs(mageStats,attack, drake = None):
    choiceStr, choiceList, colorsList = formatGlyphChoiceStr(mageStats, drake)
    if choiceStr == "You don't have enough Mana to pay for the buffs":
        whisper(choiceStr)
        return attack
    else:
        choice = askChoice("{}".format(choiceStr), choiceList, colorsList)
    
    if 'Air' in choiceList[choice-1] or ('Air Glyph' in choiceStr and choice == 1):
        me.Mana -=3
        attack['AirGlyph'] = True
        if drake and drake.markers[AirGlyphActive]>0 and drake != mageStats:
            toggleAirGlyph(drake)
        else:
            toggleAirGlyph(mageStats)
        rememberPlayerEvent("AirGlyphDeactivate",mageStats.controller)
        notify("{} has chosen to pay 3 mana and deactivate the Air Glyph to give this attack +4 to the effect roll\n".format(me))
    elif 'Fire' in choiceList[choice-1] or ('Fire Glyph' in choiceStr and choice == 1):
        me.Mana -=3
        attack['dice']+=2
        if drake and drake.markers[FireGlyphActive]>0 and drake != mageStats:
            toggleFireGlyph(drake)
        else:
            toggleFireGlyph(mageStats)
        rememberPlayerEvent("FireGlyphDeactivate",mageStats.controller)
        notify("{} has chosen to pay 3 mana and deactivate the Fire Glyph to give this attack +2 dice\n".format(me))
    elif 'both' in choiceList[choice-1]:
        me.Mana -=6
        if drake and drake.markers[AirGlyphActive]>0 and drake != mageStats:
            toggleAirGlyph(drake)
        else:
            toggleAirGlyph(mageStats)
        if drake and drake.markers[FireGlyphActive]>0 and drake != mageStats:
            toggleFireGlyph(drake)
        else:
            toggleFireGlyph(mageStats)
        attack['AirGlyph'] = True
        attack['dice']+=2
        rememberPlayerEvent("FireGlyphDeactivate",mageStats.controller)
        rememberPlayerEvent("AirGlyphDeactivate",mageStats.controller)
        notify("{} has chosen to pay 6 mana and deactivate both Air and Fire Glyphs to give this attack +2 dice and +4 to the effect roll\n".format(me))
    return attack


def formatGlyphChoiceStr(mageStats, drake):
    if timesHasOccurred("AirGlyphDeactivate",mageStats.controller) and timesHasOccurred("FireGlyphDeactivate",mageStats.controller):
        choiceStr = "You have already deactivated both this round"
        choiceList = ['OK']
        colorsList = ['#FF0000']
    elif timesHasOccurred("FireGlyphDeactivate",mageStats.controller) and me.mana >2:
        choiceStr = "Would you like to deactivate your Air Glyph?"
        choiceList = ['Yes', 'No']
        colorsList = ['#0000FF', '#FF0000']
    elif timesHasOccurred("AirGlyphDeactivate",mageStats.controller) and me.mana > 2:
        choiceStr = "Would you like to deactivate your Fire Glyph?"
        choiceList = ['Yes', 'No']
        colorsList = ['#0000FF', '#FF0000']
    else:
        if me.mana > 6 and (mageStats.markers[AirGlyphActive] or (drake.markers[AirGlyphActive] if drake else False)) and (mageStats.markers[FireGlyphActive] or (drake.markers[FireGlyphActive] if drake else False)):
            choiceStr = "Which buff would you like to apply?"
            choiceList = ['Air (+4 effect)', 'Fire (+2 dice)', 'both' ,'None']
            colorsList = ['#0000FF','#0000FF','#0000FF', '#FF0000']
        elif me.mana > 2:
            choiceStr = "Which buff would you like to apply?"
            choiceList = ['Air (+4 effect)', 'Fire (+2 dice)','None']
            colorsList = ['#0000FF','#0000FF','#FF0000']
        else:
            choiceStr = "You don't have enough Mana to pay for the buffs"
            choiceList = None
            colorsList = None
    return choiceStr, choiceList, colorsList


def bloodReaper(appliedDmg, attacker, attackerTraits, defenderTraits):
    if (appliedDmg and
        attackerTraits.get('BloodReaper') and
        defenderTraits.get('Living') and
        not timesHasOccurred("Blood Reaper",attacker.controller)):
            rememberPlayerEvent("Blood Reaper",attacker.controller)
            remoteCall(attacker.controller, 'healPlayerByAmount',[2, 'BR']) 
    return

def demonicLink(appliedDmg, attacker, attackerTraits, defenderTraits):
    if (appliedDmg and
        attackerTraits.get('demonicLink') and
        defenderTraits.get('Living') and
        not timesHasOccurred("Demonic Link",attacker.controller)):
            rememberPlayerEvent("Demonic Link",attacker.controller)
            remoteCall(attacker.controller, 'healPlayerByAmount',[1, 'DL']) 
    return


def vampiricDrain(appliedDmg, attack, attacker, defender, attackerTraits, defenderTraits):
    if (appliedDmg and
        attackerTraits.get('Living') and 
        defenderTraits.get('Living') and 
        ('Vampiric' in attackerTraits or attack.get('Vampiric')) and 
        attack.get('range type') == 'Melee'):
            damageRemaining = getRemainingLife(defender)
            damageVamp = min(int(math.ceil(appliedDmg/2.0)), damageRemaining)
            attackerDamage = get_total_damage_markers(attacker)
            damageVamp = min(damageVamp, attackerDamage)
            remoteCall(attacker.controller,'healCreatureByAmount',[attacker,damageVamp,attackerTraits,'Vamp'])
    return

def drainSiphonLife(appliedDmg,attack,attacker,defender,attackerTraits,defenderTraits):
    if (appliedDmg and
        attackerTraits.get('Living') and 
        defenderTraits.get('Living') and 
        attack.get('Drain')):
            damageRemaining = getRemainingLife(defender)
            damageVamp = min(appliedDmg, damageRemaining)
            remoteCall(attacker.controller,'healCreatureByAmount',[attacker,damageVamp,attackerTraits,'lifeDrain'])
    return

def jellyReconstruct(appliedDmg, attacker, defender, defenderTraits):
    if (appliedDmg and
        attacker.name == 'Devouring Jelly' and
        not defenderTraits.get('Incorporeal') and
        defender.Type == 'Creature'):
            subDamageAmount(attacker, 2)
            notify('The {} reconstructs!'.format(attacker))
    return

def resolveJoinedStrength(defenderTraits,appliedDmg):
    if 'joinedStr' in defenderTraits and appliedDmg:
        appliedDmg -= 1
        me.Damage +=1
        notify('{} receives a point of damage from Joined Strength!'.format(me))
    return appliedDmg

def holyAvengerBuff(attack, attacker, defender):
    eventList = getEventList('Round')
    for e in eventList:
        if e[0] == 'Attack' and e[1][0] == defender._id and e[1][3] > 0 and e[1][2] not in ['Drain Life', 'Siphon Life', 'Drain Soul']:
            #This is to prevent gaining the HA benefit against conjurations or walls
            conjCheck = Card(e[1][0]).Type
            if "Conjuration" not in conjCheck:
                victim = Card(e[1][1]) if e[1][1] else None
            else: 
                victim = None
            if victim and victim.controller==attacker.controller and (victim.Type == 'Creature' or ('Conjuration' in victim.Type and 'Holy' in victim.School)) and victim != attacker:
                attack['dice']+=2
                attack['Avenger']=True
                if attack.get('Piercing'):
                    attack['Piercing']+=1
                else:
                    attack['Piercing'] = 1
                break
    return attack

def removeLoadTokens(attacker):
    attacker.markers[LoadToken] = 0
    return

def removeLivingArmorTokens(appliedDmg,defender, defenderTraits):
    if 'LivingArmor' in defenderTraits and appliedDmg:
        LivArm = getCard('Living Armor')
        if LivArm.markers[Armor]:
            LivArm.markers[Armor] -=1
            notify('Living Armor weakens!')
    return

def adjustForTempleOfLight(attack, targetingCard):
    if targetingCard.name == 'Temple of Light' and targetingCard.markers[Ready]:
        temples = 0
        for card in table:
            if 'Temple' in card.Subtype and card.controller == me:
                temples +=1
        maximum = min(me.mana, temples)
        manaPaid = askInteger("How much mana would you like to pay? (max: {})".format(maximum),maximum)
        if manaPaid == None or manaPaid <1:
            attack = None
        if attack:
            me.mana -= min(me.mana, manaPaid)
            attack['dice'] += min(manaPaid, maximum)
            attack['manaPaid'] = min(manaPaid, maximum)
    return attack

def elementalResonance(targetingCard):
    attackChosen = {'range':[0,0],'name':'None','Cost':50000000}
    eleAttackList = []
    choiceList = []
    elementalList = getElementals(targetingCard)
    if 'Elementalist' in targetingCard.name and elementalList:
        choice = askChoice('Would you like to use Elemental Resonance?',['Yes','No'],["#01603e","#de2827"])
        if choice == 1:
            eleDialog = cardDlg(elementalList)
            eleDialog.min = 0
            eleDialog.max = 1
            eleDialog.title = 'From which elemental would you like to use an attack?'
            selectedEle = eleDialog.show()
            if selectedEle:
                selectedEle = selectedEle[0]
                eleAttackList = getAttackList(selectedEle)
                for attack in eleAttackList:
                    choiceList.append(attack['name']+', Dice: '+str(attack['dice']))
                choiceText = 'Which attack would you like to use?'
                colors = [getActionColor(eleAttackList[i]) for i in range(len(eleAttackList))]
                attackChoice = askChoice(choiceText, choiceList,colors)-1
                attackChosen = eleAttackList[attackChoice]
            damage = getTotalCardLevel(selectedEle) -1
            mageDamage = askInteger('How much damage would you like to take?',max(damage,0))
            elementalDamage = abs(mageDamage - damage)
            if mageDamage:
                mage = getMage()
                addDamageAmount(mage, mageDamage)
            if elementalDamage:
                addDamageAmount(selectedEle,elementalDamage)
            notify('{} uses Elemental Resonance putting {} damage on {} while taking {} themselves!'.format(me, elementalDamage, selectedEle, mageDamage))
    return attackChosen

def malakai_fire(attacker, defender, attack, appliedDmg):
    defTraits = getTraits(defender)
    if (attacker.Name=="Priest" and attack.get("damage type")=="Light" and appliedDmg and "Conjuration" not in defender.Type and not timesHasOccurred("Malakai's Fire",attacker.controller) and "Flame" not in defTraits.get("Immunity",[])):
        remoteCall(attacker.controller,"malakaisFirePrompt",[defender])

def follow_up(defender):
    mage = getMage()
    defTraits = getTraits(defender)
    if mage.markers[Ki] > 1 and 'CobraStance' in defTraits:
        choice = askChoice('Would you like to pay 2 Ki to give {} counterstrike?'.format(defender.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            mage.markers[Ki] -= 2
            notify('{} follows through!'.format(defender))
            EOATraits = getEOATraits(defender)
            newEOATraits = {'Counterstrike':True}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', defender, mage)
            update_traits(traitParams)
    return

def resilience(defender):
    mage = getMage()
    defTraits = getTraits(defender)
    if mage.markers[Ki] > 1 and 'HorseStance' in defTraits:
        choice = askChoice('Would you like to pay 2 Ki to give {} Tough -2?'.format(defender.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            mage.markers[Ki] -= 2
            notify('{} uses monk resilience!'.format(defender))
            EOATraits = getEOATraits(defender)
            newEOATraits = {'Tough':1}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', defender, mage)
            update_traits(traitParams)
    return

def strike_through(attacker):
    mage = getMage()
    attTraits = getTraits(attacker)
    if mage.markers[Ki] > 1 and 'HorseStance' in attTraits:
        choice = askChoice('Would you like to pay 2 Ki to give {} Piercing +2 from your stance?'.format(attacker.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            mage.markers[Ki] -= 2
            notify('{} strikes through!'.format(attacker))
            EOATraits = getEOATraits(attacker)
            newEOATraits = {'Piercing':2}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', attacker, mage)
            update_traits(traitParams)
    return

def bo_staff(defender):
    defTraits = getTraits(defender)
    if 'boStaff' in defTraits and defender.markers[Ki]>1:
        choice = askChoice('Would you like to pay 2 Ki to use your defense from the Bo Staff?'.format(defender.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            defender.markers[Ki] -= 2
            EOATraits = getEOATraits(defender)
            newEOATraits = {'Defense':[{'Threshold':7, 'Uses':10000,'Restriction':'Ranged', 'name':'Bo Staff'}]}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', defender, defender)
            update_traits(traitParams)
    return

def Sai(targetingCard):
    attTraits = getTraits(targetingCard)
    if 'Sai' in attTraits and targetingCard.markers[Ki]:
        choice = askChoice('Would you like to pay 1 Ki to give {} Piercing +2 from your Sai?'.format(targetingCard.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            targetingCard.markers[Ki] -= 1
            notify('{} uses the Sai!'.format(targetingCard))
            EOATraits = getEOATraits(targetingCard)
            newEOATraits = {'Piercing':2}
            traitParams = create_trait_params(EOATraits,newEOATraits,'EOA', targetingCard, targetingCard)
            update_traits(traitParams)
    return

def Nunchucks(attack, targetingCard):
    attTraits = getTraits(targetingCard)
    if 'Nunchucks' in attTraits and targetingCard.markers[Ki]:
        choice = askChoice('Would you like to pay 1 Ki to give {} 1 extra die on the attack?'.format(targetingCard.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            targetingCard.markers[Ki] -= 1
            notify('{} uses Nunchucks!'.format(targetingCard))
            attack['dice'] +=1
    return attack

def dragons_lance(attack, targetingCard):
    if attack.get('name') == 'Dragon\'s Bite' and targetingCard.markers[Ki]:
        choice = askChoice('Would you like to pay 1 Ki to give {} +6 on the effect roll?'.format(targetingCard.name),['Yes', 'No'],["#01603e","#de2827"])
        if choice == 1:
            targetingCard.markers[Ki] -= 1
            notify('{}\'s Dragon\'s Lance burns hot!'.format(targetingCard))
            attack['DragonLance'] = 6
    return attack

def battle_meditation(attacker, defender, attackerTraits, defenderTraits, appliedDmg):
    if appliedDmg > 0 and "BattleMeditation" in attackerTraits and not timesHasOccurred("BMAttack",attacker.controller):
        attacker.markers[Ki]+=1
        rememberPlayerEvent("BMAttack",attacker.controller)
        notify("{}\'s Battle Meditation generates 1 Ki from the attack!".format(attacker.name))
    if appliedDmg > 0 and "BattleMeditation" in defenderTraits and not timesHasOccurred("BMDefense",defender.controller):
        defender.markers[Ki]+=1
        rememberPlayerEvent("BMDefense",defender.controller)
        notify("{}\'s Battle Meditation generates 1 Ki!".format(attacker.name))
    return

def fortified_resolve_attack(attacker, defender, attackerTraits, defenderTraits, appliedDmg):
    if 'FortRes' in attackerTraits and appliedDmg and defender.Type == 'Creature' and not timesHasOccurred("FortRes",attacker.controller):
        attachmentList = getAttachedCards(attacker)
        for card in attachmentList:
            if card.name == 'Fortified Resolve':
                card.markers[Charge] += 1
                rememberPlayerEvent("FortRes",attacker.controller)
                notify("Fortified Resolve charges up. It now has {} charges\n".format(card.markers[Charge]))
    return 

def ketsuro_attack_buff(attack, mage):
    choice = askChoice('Would you like to pay 1 Ki to give Ketsuro Sentinel 1 extra attack die?',['Yes', 'No'],["#01603e","#de2827"])
    if choice == 1:
        mage.markers[Ki] -= 1
        notify('Ketsuro Sentinel\'s attack is buffed by the Monk\'s Ki')
        attack['dice'] += 1
    return attack

def adjust_dice_for_strongest(attack, targetingCard, targetedCard, attackerTraits):
    strongest = determine_strongest_enemy()
    if 'Knight of the Red Helm' in targetingCard.name and (targetedCard in strongest or (not strongest and 'Mage' in targetedCard.Subtype)):
        attack['dice'] += 2
    if 'KnightsCourage' in attackerTraits and (targetedCard in strongest or (not strongest and 'Mage' in targetedCard.Subtype)):
        attack['dice'] += 2
        if attack.get('Piercing'):
            attack['Piercing'] += 1
        else:
            attack['Piercing'] = 1
    return attack

def determine_strongest_enemy():
    strongest_cost = 0
    strongest = []
    for card in table:
        if 'Mage' not in card.Subtype and card.Type == 'Creature' and card.isFaceUp and int(card.Cost)>strongest_cost and card.controller != me:
            strongest_cost = int(card.Cost)
            strongest = [card]
        elif 'Mage' not in card.Subtype and card.Type == 'Creature' and card.isFaceUp and int(card.Cost)==strongest_cost and card.controller != me:
            strongest.append(card)
    return strongest

    