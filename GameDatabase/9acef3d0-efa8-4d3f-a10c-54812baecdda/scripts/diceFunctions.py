def populateDiceBanks(attack,effect):
    global attackDiceBank
    global effectDieBank
    if attack:
        attackDiceBank = list(rndArray(0,5,500))
    if effect:
        effectDieBank = list(rndArray(1,12,500))
    return

def rollD6(dice):
    '''takes "dice" D6 results from the attackDiceBank and turns it into a list of frequencies of each # rolled'''
    mute()
    global attackDiceBank
    if (len(attackDiceBank) < dice):
        populateDiceBanks(True,False)
    MWDiceRoll = [0,0,0,0,0,0]
    for x in range(dice):
        roll = attackDiceBank.pop()
        MWDiceRoll[roll] += 1
    notify("{} rolls {} attack dice.\n".format(me,dice))
    return MWDiceRoll

def rollD12():
    mute()
    global effectDieBank
    if (len(effectDieBank)) <= 1:
        populateDiceBanks(False,True)
    effectRoll = int(effectDieBank.pop())
    return effectRoll

def rollDice(dice):
	mute()
	if dice == 0: attackRoll = [0,0,0,0,0,0]
	else: attackRoll = rollD6(dice)
	effectRoll = rollD12()
	displayRoll(attackRoll,effectRoll)
	return (attackRoll, effectRoll)

def displayRoll(attackRoll,effectRoll):
	mute()
	mapDict = eval(getGlobalVariable('Map'))
	for c in table:
			if c.model == "c752b2b7-3bc7-45db-90fc-9d27aa23f1a9" and c.controller == me: c.delete()
	dieCardX, dieCardY = mapDict.get('DiceBoxLocation',(0,0))
	dieCard = table.create("c752b2b7-3bc7-45db-90fc-9d27aa23f1a9", dieCardX, dieCardY) #dice field
	dieCard.anchor = (True)

	normalDamage = attackRoll[2] + 2* attackRoll[3] # calculate the results for Normal Damage
	criticalDamage = attackRoll[4] + 2* attackRoll[5] # calculate the results for Critical Damage

	#defines the markers that will be displayed in the RDA
	dieCard.markers[attackDie[0]] = attackRoll[0]+attackRoll[1] # Blank Dice
	dieCard.markers[attackDie[2]] = attackRoll[2] # display 1 Normal Damage
	dieCard.markers[attackDie[3]] = attackRoll[3] # display 2 Normal Damage
	dieCard.markers[attackDie[4]] = attackRoll[4] # display 1 Critical Damage
	dieCard.markers[attackDie[5]] = attackRoll[5] # display 2 Critical Damage
	dieCard.markers[effectDie] = effectRoll
	playSound('Dice')
	notify("{} rolled {} Normal Damage, {} Critical Damage, and {} on the effect die\n".format(me, normalDamage, criticalDamage, effectRoll))

def dazeMiss(attacker):
	notify("{} is so dazed that it completely misses!\n".format(attacker))
	
def DivineChallengeReroll(attacker, damageRoll, effectRoll):
	blanks = damageRoll[0] + damageRoll[1]
	normalDamage = damageRoll[2] + 2* damageRoll[3] # calculate the results for Normal Damage
	criticalDamage = damageRoll[4] + 2* damageRoll[5] # calculate the results for Critical Damage
	numNorm1s = damageRoll[2]
	numcrit1s = damageRoll[4]
	#debug(str(damageRoll))
	askStr = 'The attack rolled: \n{} blanks, \n{} normal damage ({} 1s) and \n{} critical damage ({} 1s))\nWould you like to reroll any dice?'.format(blanks, normalDamage, numNorm1s, criticalDamage, numcrit1s)
	rrChoices = ['All blanks', 'Blanks and normal 1s','Blanks and Normals', 'Blanks, all normal damage, and crit 1s', 'All non-1s','No']
	colors = ['#ff1100','#ff1100','#ff1100','#ff1100','#ff1100','#aeaeff']
	choice = askChoice(askStr, rrChoices, colors)
	if choice == 1:
		#'All blanks'
		dice = blanks
		damageRoll[0:2] = [0,0]
		newDamageRoll = divineChallengeResult(dice,attacker, damageRoll, effectRoll)
	elif choice == 2:
		#'Blanks and normal 1s'
		dice = blanks + numNorm1s
		damageRoll[0:3] = [0,0,0]
		newDamageRoll = divineChallengeResult(dice,attacker, damageRoll, effectRoll)
	elif choice == 3:
		#'Blanks and Normals' 
		dice = blanks + normalDamage
		damageRoll[0:4] = [0,0,0,0]
		newDamageRoll = divineChallengeResult(dice,attacker, damageRoll, effectRoll)
	elif choice == 4: 
		#'Blanks, all normal damage, and crit 1s'
		dice = blanks + normalDamage + numcrit1s
		damageRoll[0:5] = [0,0,0,0,0]
		newDamageRoll = divineChallengeResult(dice,attacker, damageRoll, effectRoll)
	elif choice == 5:
		#'All non-1s'
		dice = blanks + damageRoll[3] + damageRoll[5]
		damageRoll[0:2] = [0,0]
		damageRoll[3] = [0]
		damageRoll[5]= [0]
		newDamageRoll = divineChallengeResult(dice,attacker, damageRoll, effectRoll)
	else:
		newDamageRoll = damageRoll
	return newDamageRoll

def divineChallengeResult(dice,attacker, damageRoll, effectRoll):
	newTempRoll = rollD6(dice)
	newNormal = newTempRoll[2]+2*newTempRoll[3]
	newCritical = newTempRoll[4]+2*newTempRoll[5]
	notify("The Divine Challenge gained {} Normal Damage, {} Critical Damage\n".format(newNormal, newCritical))
	newDamageRoll = [i+j for i,j in zip(damageRoll, newTempRoll)]
	#debug(str(newDamageRoll))
	displayRoll(newDamageRoll,effectRoll)
	rememberPlayerEvent("Divine Challenge",attacker)
	return newDamageRoll