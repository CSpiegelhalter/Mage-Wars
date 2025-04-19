def getEventList(roundOrTurn):
		return (eval(getGlobalVariable("roundEventList")) if roundOrTurn =='Round' else eval(getGlobalVariable("turnEventList")))

def setEventList(roundOrTurn,eventList):
		if roundOrTurn =='Round': setGlobalVariable("roundEventList",str(eventList))
		else: setGlobalVariable("turnEventList",str(eventList))

def appendEventList(roundOrTurn,event):
		eventList = getEventList(roundOrTurn)
		eventList.append(event)
		setEventList(roundOrTurn,str(eventList))

def clearLocalTurnEventList(): #Clears the part of the turnList pertaining to the local player
		eventList = getEventList('Turn')
		for e in list(eventList):
				if (e[0] in ('Attack','Defense') and Card(e[1][0]).controller == me): eventList.remove(e)
		setEventList('Turn',eventList)

def hasAttackedThisTurn(card):
		eventList = getEventList('Turn')
		for e in eventList:
				if e[0] == 'Attack' and e[1][0] == card._id: return True

def hasAttackedThisRound(card):
		eventList = getEventList('Round')
		for e in eventList:
				if e[0] == 'Attack' and e[1][0] == card._id: return True

def hasAttackedTargetThisTurn(targetingCard, targetedCard):
    eventList = getEventList('Round')
    for e in eventList:
        if e[0] == 'Attack' and e[1][0] == targetingCard._id and e[1][1] == targetedCard._id: 
            return True

def timesHasUsedDefense(card,defenseDict):
		"""Counts how many times defense has been used this ROUND"""
		eventList = getEventList('Round')
		count = 0
		for e in eventList:
				if e[0] == 'Defense' and e[1][0] == card._id and e[1][1]['name'] == defenseDict['name']: count += 1
		return count

def timesHasOccurred(event,player=me):
		eventList = getEventList('Round')
		count = 0
		for e in eventList:
				if e[0] == 'Event' and e[1][0] == player._id and e[1][1]==event: count += 1
		return count

def timesHasUsedAttack(card,attack):
		"""Counts how many times attack has been used this TURN"""
		eventList = getEventList('Turn')
		count = 0
		for e in eventList:
				if e[0] == 'Attack' and e[1][0] == card._id and e[1][2] == attack: count += 1
		return count

def timesHasUsedAbility(card,number=0):
		"""Counts how many times untargeted ability has been used this ROUND"""
		eventList = getEventList('Round')
		count = 0
		for e in eventList:
				if e[0] == 'Ability' and e[1][0] == card._id and e[1][1] == number: count += 1
		return count

def timesHasUsedDiscount(card,discount,number=0):
		"""Counts how many times untargeted ability has been used this ROUND"""
		eventList = getEventList('Round')
		count = 0
		for e in eventList:
				if e[0] == 'Discount' and e[1][0] == card._id and e[1][1] == discount and e[1][2] == number: count += 1
		return count

def hasCharged(card):
		"""returns whether this card has charged this TURN"""
		eventList = getEventList('Turn')
		if ['Charge',[card._id]] in eventList: return True

def rememberDefenseUse(card,defense):
		appendEventList('Round',['Defense', [card._id,defense]])
		appendEventList('Turn',['Defense', [card._id,defense]])

def rememberAttackUse(attacker,defender,attack,damage=0):
		appendEventList('Round',['Attack', [attacker._id,defender._id,attack,damage]])
		appendEventList('Turn',['Attack', [attacker._id,defender._id,attack,damage]])
		
def rememberBattleMed(attacker,defender,Att = False,Def = False):
		appendEventList('Round',['Attack', [attacker._id,defender._id,Att,Def]])
		appendEventList('Turn',['Attack', [attacker._id,defender._id,Att,Def]])

def rememberCharge(attacker):
		appendEventList('Round',['Charge', [attacker._id]])
		appendEventList('Turn',['Charge', [attacker._id]])

def rememberAbilityUse(card,number=0):
		appendEventList('Round',['Ability', [card._id,number]])
		appendEventList('Turn',['Ability', [card._id,number]])

def rememberDiscountUse(card, discount,number=0):
	appendEventList('Round',['Discount', [card._id,discount,number]])
	appendEventList('Turn',['Discount', [card._id,discount, number]])

def rememberPlayerEvent(event,player=me): #For misc. string events associated with a player. Useful for 'the first time per round...' effects.
		appendEventList('Round',['Event', [player._id,event]])
		appendEventList('Turn',['Event', [player._id,event]])