#Attack Sequence:
def attackSequence(attack, attacker, defender):
    mute()
    '''this has to be set up in a weird way since each step needs to be called by a different player and you can't return values with a remoteCall'''
    #0.1 Check for guards
    defender = guardAndInterceptCheck(attack, attacker, defender)
    if defender:
        #1. Declare Attack
        if attack.get('Zone Attack') == True:
            upkeepFilter = "#ABFFFFFF"
            defender.filter = upkeepFilter #Light Blue - R=126 G=198 B=222
            targets = getAllCardIDsInZoneList(defender)
            targets = filter_for_creatures_and_conjurations(targets)
            attack['targets'] = targets
        elif attack.get('Zone Attack') == 'Other':
            upkeepFilter = "#ABFFFFFF"
            defender.filter = upkeepFilter #Light Blue - R=126 G=198 B=222
            targets = getOtherCardIDsInZoneList(attacker)
            targets = filter_for_creatures_and_conjurations(targets)
            attack['targets'] = targets
        declareAttackStep(attack, attacker, defender)
        #10. Attack Ends
    return

# def checkForFlyingAndReach(attack, attacker, defender):
#     mute()
#     #Creature without Flying cannot melee attack creatures with Flying, unless melee attack has Reach
#     if attack.get('range type') == 'Melee' and attack.get('')

def guardAndInterceptCheck(attack, attacker, defender):
    mute()
    attTraits = getTraits(attacker)
    #Guards for melee attacks
    if attack.get('range type') == 'Melee' and not 'Elusive' in attTraits and not defender.markers[Guard] and checkForGuardsInZone(attack, attacker, defender):
        targetChoiceList = ["Continue, ignore the guards","Change targets","Cancel Attack"]
        targetChoice = askChoice("There appear to be guards in this zone. Continue with attack, change targets, or cancel attack?", targetChoiceList,["#009933","#ff0000",'#0000FF'])
        if targetChoice == 2:
            defender = redirectTarget(attacker, defender)    
        elif targetChoice != 1:
            return None
    elif attack.get('range type') == 'Ranged' and not 'Zone Attack' in attack and checkForInterceptorsInZone(attack, attacker, defender):
        targetChoiceList = ["Continue","Cancel Attack"]
        menu_text = "{} has a guarding interceptor in the zone.\nWould you like to continue with the Attack?".format(defender.controller)
        targetChoice = askChoice(menu_text, targetChoiceList,["#009933","#ff0000"])
        if targetChoice == 1:
            defender = remoteCall(defender.controller,'redirectIntercept',[attack, attacker, defender])
        else:
            return None
    return defender

def checkForInterceptorsInZone(attack, attacker, defender):
    mute()
    othersInZone = getOtherCardsInZoneList(defender)
    for otherCard in othersInZone:
        cardTraits = getTraits(otherCard)
        if (otherCard.markers[Guard] and
            otherCard.controller != attacker.controller and
            not ('Restrained' in cardTraits or 'Incapacitated' in cardTraits) and
            'Intercept' in cardTraits):
                return True
    return False

def checkForGuardsInZone(attack, attacker, defender):
    mute()
    othersInZone = getOtherCardsInZoneList(defender)
    for otherCard in othersInZone:
        cardTraits = getTraits(otherCard)
        if (otherCard.markers[Guard] and
            otherCard.controller != attacker.controller and
            not ('Restrained' in cardTraits or 'Incapacitated' in cardTraits)):
                return True
    return False

def redirectTarget(attacker, defender):
    mute()
    othersInZone = getOtherCardsInZoneList(defender)
    choiceList = []
    idList = []
    for card in othersInZone:
        cardTraits = getTraits(card)
        if (card.markers[Guard] and
            card.controller != attacker.controller and
            not ('Restrained' in cardTraits or 'Incapacitated' in cardTraits)):
                choiceList.append(card.name)
                idList.append(card._id)
    choice = askChoice("Choose a new target for the attack", choiceList,'#0000FF')
    defender = Card(idList[choice-1])
    return defender

def redirectIntercept(attack, attacker, defender):
    mute()
    targetChoice = askChoice("{} is being targeted by {}'s {}.\n\n Would you like to intercept?".format(defender.Name,attacker.Name,attack.get("name")),["Yes", "No"],["#009933","#ff0000"])
    if targetChoice == 1:
        othersInZone = getOtherCardsInZoneList(defender)
        choiceList = []
        idList = []
        for card in othersInZone:
            cardTraits = getTraits(card)
            if (card.markers[Guard] and
                card.controller == me and
                not ('Restrained' in cardTraits or 'Incapacitated' in cardTraits) and
                'Intercept' in cardTraits):
                    choiceList.append(card.name)
                    idList.append(card._id)
        choice = askChoice("Choose a new target for the attack", choiceList,'#0000FF')
        defender = Card(idList[choice-1])
        defender.markers[Guard] = 0
    remoteCall(attacker.controller,'declareAttackStep',[attack, attacker, defender])
    return 

def interimStep(attack, attacker, defender, previousStep, nextStep, nextPlayer, damageRoll = None, effectRoll = None):
    mute()
    #TODO Enchantment reveal windows, reroll opportunities (Akiro, gloves of skill, press the attack)
    #1.a DeclareAttack, 2.a Pay Costs, 3.a Roll To Miss, 4.d Avoid Attack, 5.a Roll Dice, 6.d Damage and Effects, 7.a add'l Strikes, 8.d Damage Barrier, 9.a Counter
    
    #verbose = askChoice('Would you like to be asked after each step to reveal an enchantment?')
    #debug('Interim')
    #debug('previous Step {}'.format(previousStep))
    #debug('next Step {}'.format(nextStep))
    #debug('next Player {}'.format(nextPlayer))
    if previousStep == 'declareAttackStep':
        #Attacker
        revealedAttachment = revealAttachmentQuery(attacker, defender)
        if revealedAttachment:
            attack['dice'] = attack['unmodDice']
            attack = computeAttack(attack, attacker, defender)
        if not attack.get('strikes'):
            attack['strikes'] = 1
    elif previousStep == 'rollToMissStep':
        #Defender
        revealedAttachment = revealAttachmentQuery(attacker, defender)
        if revealedAttachment:
            attack['dice'] = attack['unmodDice']
            attack = computeAttack(attack, attacker, defender)
    elif previousStep == 'rollDiceStep':
        #Defender
        revealedAttachment = revealAttachmentQuery(attacker, defender)
    elif previousStep == 'additionalStrikesStep' and nextStep == 'declareAttackStep':
        attack['dice'] = attack['unmodDice']
        attack['strikes'] += 1
        attack = computeAttack(attack, attacker, defender)
    elif previousStep == 'payCostsStep' and nextStep == 'attack_ends_step':
        remoteCall(attacker.controller, 'attack_ends_step', [attacker])
        remoteCall(defender.controller, 'attack_ends_step', [defender])
    remoteCall(nextPlayer,nextStep,[attack, attacker, defender]+([damageRoll,effectRoll] if (damageRoll != None and effectRoll != None) else []))
    return

#1. Declare Attack
def declareAttackStep(attack, attacker, defender, previousStep = None):
    mute()
    #Current Player: Attacker    
    notify("\n{} attacks {} with {}!\n".format(attacker,defender,attack.get('name','a nameless attack')))

    mage = getMage()
    if mage.name == 'Elementalist':
        mageStats = getMageStats()
        drake = getCard('Elemental Drake')
        if ((mageStats.markers[AirGlyphActive] or mageStats.markers[FireGlyphActive]) 
        or ((drake.markers[AirGlyphActive] or drake.markers[FireGlyphActive]) if drake else False)):
            notifystr = "Would you like Deactivate a Glyph to buff this attack?"
            choiceList = ['Yes', 'No']
            colorsList = ['#0000FF', '#FF0000']
            choice = askChoice("{}".format(notifystr), choiceList, colorsList)
            if choice == 1:
                attack = buffWithGlyphs(mageStats, attack, drake)
    if attack.get('Zone Attack',False) and attack.get('strikes',0):
        upkeepFilter = "#ABFFFFFF"
        defender.filter = upkeepFilter #Light Blue - R=126 G=198 B=222
    if attack.get("name") == "Arcane Zap" and ("Wizard" in attacker.Name): rememberPlayerEvent("Arcane Zap",attacker.controller)
    if attacker.name == 'Ketsuro Sentinel' and mage.markers[Ki]:
        ketsuro_attack_buff(attack, mage)
    
    nextPlayer = attacker.controller
    if attack.get('strikes',0) == 0:
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'declareAttackStep', 'payCostsStep', nextPlayer])
    else:
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'declareAttackStep', 'rollToMissStep', nextPlayer])
    return

#2. Pay Costs
def payCostsStep(attack, attacker, defender):
    mute()
    #Current Player: Attacker
    if attack.get('Cost') and attack.get('Spell') and attack.get('source type') in ['Incantation', 'Attack']:
        originalSource = Card(attack.get('originalCardSource'))
        spellCast = castSpell(originalSource)
    elif attack.get('Cost') and attack.get('Spell'):
        me.mana -= attack.get('Cost')
        spellCast = True
    nextPlayer = attacker.controller
    if attack.get('Spell') and not spellCast:
        notify('{} has chosen to cancel the spell'.format(me))
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'payCostsStep','attack_ends_step', nextPlayer])
    else:
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'payCostsStep','rollToMissStep', nextPlayer])
    return

#3. Roll To miss - Daze
def rollToMissStep(attack, attacker, defender):#TODO refactor
    mute()
    #Current Player: Attacker
    nextPlayer = defender.controller
    #rememberAttackUse
    if attacker.markers[Daze] and 'Autonomous' not in attack and attack.get('range type') != 'Damage Barrier':
        notify("{} is rolling the Effect Die to check for the Dazed condition.\n".format(attacker))
        damageRoll,effectRoll = rollDice(0)
        attachmentsList = getAttachedCards(attacker)
        if effectRoll < 7 and attachmentsList:
            attachmentReveal = revealAttachmentQuery(attacker, defender)
            attTraits = getTraits(attacker)
            if 'akirosFavor' in attTraits and attacker.controller == me:
                damageRoll,effectRoll = akirosFavor(attacker,damageRoll,effectRoll, 'rollToMissStep')
            if effectRoll < 7:
                dazeMiss(attacker)
                nextPlayer = attacker.controller
                rememberAttackUse(attacker,defender,attack['name'],0)
                remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'rollToMissStep','additionalStrikesStep', nextPlayer])
                return
            else:
                notify("Though dazed, {} manages to avoid fumbling the attack.\n".format(attacker))
                remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'rollToMissStep', 'avoidAttackStep', nextPlayer])
        elif effectRoll < 7:
            dazeMiss(attacker)
            rememberAttackUse(attacker,defender,attack['name'],0)
            nextPlayer = attacker.controller
            remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'rollToMissStep','additionalStrikesStep', nextPlayer])
        else:
            notify("Though dazed, {} manages to avoid fumbling the attack.\n".format(attacker))
            remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'rollToMissStep', 'avoidAttackStep', nextPlayer])
    else:
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'rollToMissStep', 'avoidAttackStep', nextPlayer])
    return

#4. Avoid Attack
def avoidAttackStep(attack, attacker, defender):
    #Current Player: Defender
    nextPlayer = attacker.controller
    follow_up(defender)
    resilience(defender)
    strike_through(attacker)
    bo_staff(defender)
    if forcefieldBlock(attack, attacker, defender):
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'avoidAttackStep', 'additionalStrikesStep', nextPlayer])
    
    elif symbioticOrbDefense(attack, attacker, defender):
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'avoidAttackStep', 'additionalStrikesStep', nextPlayer])

    elif checkEnchantmentDefenses(attack, attacker, defender):
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'avoidAttackStep', 'additionalStrikesStep', nextPlayer])
    
    elif checkReverseAttack(attack, attacker, defender):
        attack = computeAttack(attack, attacker, attacker)
        remoteCall(nextPlayer,'interimStep',[attack, attacker, attacker,'avoidAttackStep', 'rollDiceStep', nextPlayer])
    
    elif checkChosenDefenses(attack, attacker, defender):
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'avoidAttackStep', 'additionalStrikesStep', nextPlayer])

    else:
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender,'avoidAttackStep', 'rollDiceStep', nextPlayer])
    return

#5. Roll Dice
    #Current Player: Attacker
def rollDiceStep(attack, attacker, defender):
    mute()
    #debug('Roll Dice')
    damageRoll,effectRoll = rollDice(attack['dice'])
    attachmentReveal = revealAttachmentQuery(attacker, defender)
    attTraits = getTraits(attacker)
    if 'akirosFavor' in attTraits and attacker.controller == me:
        damageRoll,effectRoll = akirosFavor(attacker,damageRoll,effectRoll, 'rollDiceStep')
    
    if  (('Paladin' in attacker.name and 'Mage' in attacker.subtype and defender.markers[DivineChallenge] and attack.get('range type') == 'Melee' and not timesHasOccurred('Divine Challenge', attacker)) or 
        (attacker.markers[DivineChallenge] and 'Paladin' in defender.name and 'Mage' in defender.Subtype and attack.get('range type') == 'Melee' and not timesHasOccurred('Divine Challenge', attacker))):
            damageRoll = DivineChallengeReroll(attacker, damageRoll, effectRoll)
    
    if 'glovesOfSkill' in attTraits and attack.get('range type') == 'Ranged' and not timesHasOccurred('Gloves of Skill',me):
        damageRoll = glovesOfSkillRR(damageRoll, effectRoll)

    nextPlayer = defender.controller
    setGlobalVariable("avoidAttackTempStorage","Hit")
    remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'rollDiceStep', 'damageAndEffectsStep', nextPlayer, damageRoll, effectRoll])
    return

#6. Damage and Effects
def damageAndEffectsStep(attack, attacker, defender, damageRoll, effectRoll):
    #Current Player: Defender
    mute()
    rawDmg, actualEffect = computeRawDamageAndEffects(damageRoll,effectRoll,attack,attacker,defender)
    dManaDrain = manaDrain(defender, attacker, attack, rawDmg)
    if defender.markers[VoltaricON] and rawDmg:
        rawDmg = voltaricShield(rawDmg, defender)

    if 'FortRes' in getTraits(defender) and rawDmg: 
        rawDmg = fortified_resolve_defense(defender, rawDmg)
    
    if actualEffect:
        adjustedEffects = adjustEffects(attacker, defender, actualEffect)
    else:
        adjustedEffects = None
    #debug(str(adjustedEffects))
    appliedDmg, adjustedEffects = damageReceiptMenu(attack, attacker, defender, damageRoll, dManaDrain, rawDmg, adjustedEffects)
    
    applyDamageAndEffects(attack,attacker, defender, appliedDmg, adjustedEffects, dManaDrain)
    
    rememberAttackUse(attacker,defender,attack['name'] if attack.get('name') else 'Generic',appliedDmg)

    if attack.get('Avenger'):
        rememberPlayerEvent("Holy Avenger",attacker.controller)
    
    if attacker.name == 'Paladin' and appliedDmg > 0 and attack.get('range type') == 'Melee' and not timesHasOccurred('Valor', attacker.controller):
        debug('give paladin valor')
        remoteCall(attacker.controller,'give_paladin_valor',[attacker, defender])

    nextPlayer = attacker.controller
    remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'damageAndEffectsStep', 'additionalStrikesStep', nextPlayer])
    return

#7. Additional Strikes

def additionalStrikesStep(attack, attacker, defender):
    mute()
    #debug('additional Strikes')
    #Current Player: Attacker
    attackerTraits = getTraits(attacker)
    strikes = attack.get('strikes', 1)
    strikeLimit = 1
    if attack.get('Doublestrike'):
        strikeLimit = 2
    elif 'badgerFrenzy' in attackerTraits:
        strikeLimit = 2
    elif attacker.name == 'Sohei Disciple' and attacker.attachments not in ['', '[]']:
        strikeLimit = 2
    elif attack.get('Triplestrike'):
        strikeLimit = 3
    if attacker.name == 'Wall of Thorns':
        level = getTotalCardLevel(defender)
        strikeLimit = (level -1 if level>1 else 1)
    if "Swarm" in attackerTraits:
        strikeLimit = (int(attacker.Stat_Life)-attacker.markers[Damage]+1)
    if attack.get('Zone Attack',False):
        targets = attack['targets']
        targets.remove(defender._id)
        defender.filter = None
        if targets:
            defender = Card(targets[0])
            attack['targets'] = targets
    if strikes < strikeLimit or len(attack.get('targets',[])) > 0: #timesHasUsedAttack(attacker,attack['name'] if attack.get('name') else 'Generic')
        interimStep(attack, attacker, defender, 'additionalStrikesStep', 'declareAttackStep', attacker.controller)
    else: 
        nextPlayer = defender.controller
        remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'additionalStrikesStep', 'damageBarrierStep', nextPlayer])
    return

#8. Damage Barrier

def damageBarrierStep(attack, attacker, defender):
    mute()
    #debug('damage Barrier')
    #Current Player: Defender
    choiceList = []
    legalDamageBarriersList = []
    if attack.get('range type') == 'Melee' and getGlobalVariable('avoidAttackTempStorage') == 'Hit':
        attackList = getAttackList(defender)
        for attack in attackList:
            if attack.get('range type') == 'Damage Barrier':
                computeAttack(attack,defender, attacker)
                legalDamageBarriersList.append(attack)
                attack['unmodDice'] = attack['dice']
                choiceList.append(attack['name']+', Dice: '+str(attack['dice']))
    if len(legalDamageBarriersList) > 1:
        choiceText = 'Which damage barrier would you like to use?'
        choiceList += ['Roll Other Dice Amount','Cancel']
        colors = [getActionColor(legalDamageBarriersList[i]) for i in range(len(legalDamageBarriersList))]+ ['#666699','#000000']
        attackChoice = askChoice(choiceText, choiceList,colors)-1
        attack = legalDamageBarriersList[attackChoice]
        declareAttackStep(attack, defender, attacker)
    elif len(legalDamageBarriersList) == 1:
        attack = legalDamageBarriersList[0]
        declareAttackStep(attack, defender, attacker)
    nextPlayer = defender.controller
    remoteCall(nextPlayer,'interimStep',[attack, attacker, defender, 'damageBarrierStep', 'counterstrikeStep', nextPlayer])
    return

#9. Counterstrike
def counterstrikeStep(attack, attacker, defender):
    #debug('Counterstrike')
    #Current Player: Defender
    if attack.get('range type') == 'Melee' and not attack.get('counterStrike') and not defender.isDestroyed:
        counterAttack = chooseAttack(defender, attacker, True)
        if defender.markers[Guard]:
            defender.markers[Guard] = 0
        if counterAttack:
            declareAttackStep(counterAttack, defender, attacker)
        else:
            remoteCall(attacker.controller, 'attack_ends_step',[attacker])
            attack_ends_step(defender)
    # Burning Cuirass effect
    if 'Mage' in defender.Subtype and attack.get('range type') == 'Melee':
        defTraits = getTraits(defender)
        attTraits = getTraits(attacker)
        if 'bCuirass' in defTraits:
            for card in table:
                if card.name == "Burning Cuirass" and card.controller == defender.controller and card.markers[Ready] > 0:
                        toggleReady(card)
                        if "Flame" not in attTraits.get("Immunity",[]):  
                            attacker.markers[Damage] += 1
                            notify("{}'s {} inflicts 1 point of direct flame damage to {}.".format(defender, card, attacker))
                        else:
                            notify("{} is immune to the flame damage from {}'s {}.".format(attacker, defender, card))
                        break
    else:
        remoteCall(attacker.controller, 'attack_ends_step',[attacker])
        attack_ends_step(defender)
    return

#10. Attack Ends Step
def attack_ends_step(card):
    mute()
    reset_EOA_traits(card)
    '''if getRemainingLife(card) <1 and getGlobalVariable("GameSetup") == "True":
        remoteCall(card.controller, 'deathPrompt',[card])'''
    return