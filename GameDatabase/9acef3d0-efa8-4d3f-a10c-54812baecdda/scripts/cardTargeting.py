def onCardArrowTargeted(args):
    #args = player,fromCard,toCard,targeted,scripted
    mute()
    targetingCard, targetedCard = args.fromCard, args.toCard
    if targetedCard:
        targetTraits = getTraits(targetedCard)
    if args.player == me == targetingCard.controller and args.targeted:
        if canDeclareAttack(targetingCard) and ('Conjuration' in targetedCard.type or 'Creature' in targetedCard.type):
            attack = chooseAttack(targetingCard, targetedCard)
            ##debug('attack: {}'.format(str(attack)))
            if attack and not (attack.get('Heal') or attack.get('Reconstruct')):
                Sai(targetingCard)
                attack = Nunchucks(attack, targetingCard)
                attack = dragons_lance(attack, targetingCard)
                attack, charge = adjustForCharging(attack, targetingCard)
                if charge:
                    attack = computeAttack(attack, targetingCard, targetedCard)
                    attackSequence(attack, targetingCard, targetedCard)
                else:
                    attackSequence(attack, targetingCard, targetedCard)
            if attack and attack.get('Heal'):
                healTarget(attack,targetingCard, targetedCard)
            if attack and attack.get('Reconstruct'):
                reconstructTarget(attack, targetingCard, targetedCard, targetTraits)
            targetingCard.arrow(targetedCard,False)
        elif canDeclareHeal(targetingCard) and ('Conjuration' in targetedCard.type or 'Creature' in targetedCard.type) and targetTraits.get('Living'):
            heal = chooseAttack(targetingCard, targetedCard)
            #debug('heal: {}'.format(heal))
            if heal:
                healTarget(heal,targetingCard, targetedCard)
            targetingCard.arrow(targetedCard,False)
        elif canDeclareReconstruct(targetingCard) and 'Skeleton' in targetedCard.Subtype:
            rCon = chooseAttack(targetingCard, targetedCard)
            if rCon:
                reconstructTarget(rCon,targetingCard, targetedCard, targetTraits)
            targetingCard.arrow(targetedCard,False)
        else:
            if targetedCard.Type in typeIgnoreList or targetedCard.Name in typeIgnoreList or targetedCard.Type == "Magestats":
                publicChatMsg("{} is not a legal target".format(targetedCard.Name))
            elif canAttach(targetingCard, targetedCard) and castSpell(targetingCard,targetedCard):
                    c,t = attach(targetingCard,targetedCard)
            elif targetingCard.Type !="Enchantment" and canTarget(targetedCard, targetingCard):
                    castSpell(targetingCard,targetedCard) #Assume that player wants to cast card on target
            targetingCard.arrow(targetedCard,False)
    return

def chooseAttack(targetingCard = None, targetedCard = None, counterstrike = False):
    if targetingCard:
        attackList = getAttackList(targetingCard)
    legalAttackList = []
    choiceList = []
    if targetedCard:
        for attack in attackList:
            if attack.get('name') == 'Elemental Resonance':
                attack = elementalResonance(targetingCard)
                #debug('attack: {}'.format(str(attack)))
            if 'Temple of Light' in targetingCard.name and targetingCard.markers[Ready]:
                attack = adjustForTempleOfLight(attack, targetingCard)
                if attack:
                    attack['unmodDice'] = attack['dice']
                    attack = computeAttack(attack,targetingCard, targetedCard)
                    legalAttackList.append(attack)
                    choiceList.append(attack['name']+', Dice: '+str(attack['dice']))
            elif (checkAttackTargetInRange(attack, targetingCard, targetedCard) and
                checkAffordAttackCost(attack, targetingCard) and 
                not attack.get('range type',None) == 'Damage Barrier' and
                not counterstrike and
                not 'Light Blast' in attack['name']):
                attack['unmodDice'] = attack['dice']
                attack = computeAttack(attack,targetingCard, targetedCard)
                legalAttackList.append(attack)
                choiceList.append(attack['name']+', Dice: '+str(attack['dice']))
            elif (counterstrike and
                    checkAttackTargetInRange(attack, targetingCard, targetedCard) and
                    ('Counterstrike' in attack or 'Counterstrike' in getTraits(targetingCard)) and
                    attack.get('range type') == 'Melee' and
                    attack.get('action type') == 'Quick'):
                attack['unmodDice'] = attack['dice']
                attack = computeAttack(attack,targetingCard, targetedCard)
                legalAttackList.append(attack)
                choiceList.append(attack['name']+', Dice: '+str(attack['dice']))
    else:
        legalAttackList = [{'dice':i+1} for i in range(7)]
        for attack in legalAttackList:
            choiceList.append('Dice: '+str(attack['dice']))
    #TODO check for Immunity
    if len(choiceList)==0:
        choiceText = "No legal attacks detected!"
        choiceList = ['Roll anyway','Cancel']
    else:
        choiceText = 'Which attack would you like to use?'
        choiceList += ['Roll Other Dice Amount','Cancel']
    colors = [getActionColor(legalAttackList[i]) for i in range(len(legalAttackList))]+ ['#666699','#000000']
    if legalAttackList:
        attackChoice = askChoice(choiceText, choiceList,colors)-1
        if attackChoice < 0 or attackChoice == len(choiceList)-1:
            return None
        elif attackChoice == len(choiceList)-2:
            attackChosen={}
            attackChosen['dice'] = min(askInteger('How many dice would you like to roll?', 8), 50)
            return attackChosen
        else:
            attackChosen = legalAttackList[attackChoice]
            if attackChosen.get('name')== 'Light Blast':
                toggleReady(targetingCard)
            return attackChosen
    else:
        whisper('No Legal attacks detected')
        return None

def getActionColor(action):
        if action.get('Heal'): return "#fa7d00"                                 #Heal is always in orange
        if action.get('Spell'): return "#9900FF"                                #Spell attacks are purple
        if action.get('range type') == 'Ranged': return '#0f3706'               #Nonspell ranged attacks are green
        if action.get('Reconstruct'): return '#2b2b2b'
        return '#CC0000'

def getCardTypeColor(card):
    if 'Conjuration' in card.Type: return "#b6d7a8"
    if 'Creature' in card.Type: return "#783f04"
    if 'Attack' in card.Type: return "#cc0000"
    if 'Incantation' in card.Type: return "#8e7cc3"
    if 'Equipment' in card.Type: return "#bcbcbc"
    if 'Enchantment' in card.Type: return "#ffe599"

def canTarget(target, card=None, targetLine = '', castTarget = None):#TODO refactor
    compareDict = {}
    if not targetLine:
        cardTargetingDict = eval(card.Cast_Target)
    else:
        cardTargetingDict = targetLine
    for key in cardTargetingDict:
        if key == 'Traits':
            targetTraitsDict = getTraits(target) #eval(getattr(target,key))
            for targetTrait in cardTargetingDict[key]:
                traitBool, targetTrait = checkNotTarget(targetTrait)
                compareDict[targetTrait] = traitBool
                if (targetTrait not in targetTraitsDict) and traitBool:
                    return False
                elif (targetTrait not in targetTraitsDict) and not traitBool:
                    pass
                elif (compareDict[targetTrait] != targetTraitsDict[targetTrait]):
                    return False
        elif key in ['Type', 'Subtype']:
            foundTarget = False
            for targetVal in cardTargetingDict[key]:

                #debug('targetVal: {}'.format(targetVal))
                compare, targetVal = checkNotTarget(targetVal)
                #debug('targetVal: {}'.format(targetVal))
                #debug('compare: {}'.format(compare))
                if targetVal in getattr(target,key) and compare:
                    foundTarget = True
                elif targetVal not in getattr(target,key) and not compare:
                    foundTarget = True
            if not foundTarget:
                return False
        elif key == 'Owner':#Currently only works for 1 on 1
            targetVal = cardTargetingDict[key]
            if targetVal =='!me' and target.controller == me:
                return False
            elif targetVal == 'me' and not target.controller == me:
                return False
        elif key == 'Level':
            targetLevel = getTotalCardLevel(target)
            if targetLevel > cardTargetingDict[key]:
                return False
        elif key == 'Name':
            if cardTargetingDict[key] not in target.name:
                return False
        elif key == 'Target':
            if cardTargetingDict[key] == 'Friendly' and castTarget:
                if not castTarget.controller == me:
                    return False
    return True         


def checkNotTarget(targetTrait):
    if "!" in targetTrait:
        targetTrait = targetTrait.replace("!","")
        compare = False
    else:
        compare = True
    return compare, targetTrait

def notValidTarget(card, target):
    notify("That is not a valid Target")
    card.arrow(target,False)
    return