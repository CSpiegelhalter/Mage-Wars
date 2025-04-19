def defaultAction(card):
    mute()
    if card.controller == me:
        if not card.isFaceUp: #Is this If needed?
            #is this a face-down enchantment? if so, prompt before revealing
            if "Mage" in card.Subtype or card.Type == "Magestats":
                flipcard(card)
            elif card.Type == "Enchantment": revealEnchantment(card) #Need to write
            else: castSpell(card) #Need to finish
        else:
            if card.Type == "Incantation" or card.Type == "Attack": castSpell(card) #They can cancel in the castSpell prompt; no need to add another menu
    return

def flipcard(card, x = 0, y = 0):
    mute()
    mageDict = eval(me.getGlobalVariable("MageDict"))
    if card.Type in typeIgnoreList or card.Name in typeIgnoreList: return
    if card.isFaceUp == False:
        card.isFaceUp = True

        if card.Type != "Enchantment" and "Conjuration" not in card.Type: #leaves the highlight around Enchantments and Conjurations
            card.highlight = None

        if card.Type == "Creature" and "Mage" in card.Subtype and mageDict["MageRevealed"] == "False":
            mageSetup() 

        if getZoneContaining(card):
            addCardToCurrentZone(card)
        
        placeMarkersOnCard(card)	
            
    elif card.isFaceUp and hasAlternates(card):
        currentCardAlt = card.alternate
        if currentCardAlt == "":
            card.alternate = "2"
            notify("{} flips {} to an Alternate Art\n".format(me, card))
            addDefaultTraits(card)
        else:
            if int(currentCardAlt) < len(card.alternates):
                card.alternate = str(int(currentCardAlt)+1)
                notify("{} flips {} to an Alternate Art\n".format(me, card))
                addDefaultTraits(card)
            else:
                turnCardFaceDown(card)
    else:
        turnCardFaceDown(card)

    return

def turnCardFaceDown(card):
    card.alternate = ""
    for marker in card.markers: card.markers[marker] = 0
    if (card.isAttachedTo != '' and card.bTraits != ''):
        target = Card(int(card.isAttachedTo))
        traitsToRemove = eval(card.bTraits)
        currentTraits = getAttachedTraits(target)
        traitParams = create_trait_params(currentTraits,traitsToRemove,'Attached',target,card,0,True)
        update_traits(traitParams)
    elif (card.Type == 'Equipment' and card.bTraits != ''):
        target = getMage()
        traitsToRemove = eval(card.bTraits)
        currentTraits = getEquipmentTraits(target)
        traitParams = create_trait_params(currentTraits,traitsToRemove,'Equipment',target,card,0,True)
        update_traits(traitParams)
    notify("{} turns {} face down.\n".format(me, card.name))
    card.isFaceUp = False

def hasAlternates(card):
    if len(card.alternates)>1:
        return True
    else:
        return False

# New function to calculate prevention cost
def calculate_prevention_cost(targetObject):
    pCost = 0
    controller = targetObject.controller
    
    # Object-specific prevention costs
    if targetObject.name == "Champion's Gauntlets":
        pCost += 2
    elif targetObject.name == "Echo of the Depths":
        song_enchantments = len([s for s in table if s.controller == controller and 'Song' in s.Subtype and s.Type == 'Enchantment' and s.isFaceUp])
        pCost += 2 * song_enchantments
    elif targetObject.name == "Redistributed Power":
        pCost += 3
    
    # Global prevention costs for equipment
    if targetObject.Type == "Equipment":
        mage = getMage()
        if mage.controller == targetObject.controller and "ArmorWard" in getTraits(mage):
            pCost += 4
    
    # Global prevention costs for enchantments
    if targetObject.Type == "Enchantment":
        wardstone_count = getEnchantersWardstoneCount(controller)
        pCost += 2 * wardstone_count
    
    return pCost

# New function to count face-up "Enchanter's Wardstone" cards controlled by the player
def getEnchantersWardstoneCount(player):
    count = 0
    for card in table:
        if card.name == "Enchanter's Wardstone" and card.controller == player and card.isFaceUp:
            count += 1
    return count

def pay_prevention_cost(destroyer, pCost, targetObject):
    choice = askChoice('Would you like to pay {} Mana to destroy {}?'.format(pCost, targetObject.name), ['Yes', 'No'], ["#01603e", "#de2827"])
    if choice == 1:
        if destroyer.Mana >= pCost:
            destroyer.Mana -= pCost
            notify('{} pays {} mana to destroy {}'.format(destroyer, pCost, targetObject))
            return True
        else:
            notify('{} does not have enough mana to pay the prevention cost.'.format(destroyer))
            return False
    else:
        notify('{} chooses not to pay the prevention cost. Destruction of {} is prevented.'.format(destroyer, targetObject))
        return False

def destroy_with_prevention(destroyer, targetObject):
    if destroyer != targetObject.controller:
        pCost = calculate_prevention_cost(targetObject)
        if pCost > 0:
            # Prompt the destroyer to pay the prevention cost
            success = remoteCall(destroyer, 'pay_prevention_cost', [destroyer, pCost, targetObject])
            if success:
                targetObject.target()
                return True  # Destruction proceeds
            else:
                return False  # Destruction prevented
        else:
            targetObject.target()
            return True  # No prevention cost, destruction proceeds
    else:
        # If destroyer is the controller, proceed with destruction without prevention cost
        targetObject.target()
        return True

def castSpell(card, target=None):
    
    #1. Check that mage is revealed/setup
    mageDict = eval(me.getGlobalVariable("MageDict"))
    if not mageDict['MageRevealed']:
        whisper("You need to play a mage before casting a spell.")
        return
    else:
        mage = Card(mageDict['MageID'])

    #2 
    caster = determineCaster(card)
    #debug('caster: {}'.format(caster))
    if not caster or (caster.Type == 'Equipment' and caster.Stat_Channeling == ''):
        caster = mage

    #3. Determine base Cost
    baseCost, selectedEquipment = computeBaseCost(card, target)  # Expects (cost, equipment)
    if baseCost is None:
        costQuery = askInteger("Non-standard cost detected. Please enter base cost of this spell.\n(Close this menu to cancel)", 0)
        if costQuery is not None:
            baseCost = costQuery
            selectedEquipment = None  # No equipment selected
        else:
            return
    
    #4. Determine discounts
    costAdjustment, discountsApplied = computeCostAdjustment(caster,mage, card, target)
    #debug('costAdjustment: {}'.format(costAdjustment))
    #debug('discountsApplied: {}'.format(discountsApplied))
    totalToPay = baseCost + costAdjustment
    
    #5. Prompt cost confirmation
    cost = askInteger("This spell is calculated to cost {} mana. \n\n".format(str(totalToPay))+
                        "How much would you like to pay?", totalToPay)
    if cost == None: 
        if target:
            card.arrow(target,False)
        return False
    
    #6. Pay mana
    if caster != mage:
        casterMana = caster.markers[Mana]
    else:
        casterMana = 0 
    #debug('caster: {}'.format(caster.name))
    ownerMana = me.Mana
    manaPool = ownerMana + casterMana
    if not checkEnoughMana(cost, manaPool): #CHECK: THis looks funky to me. return later
        return
    
    if caster!=mage:
        unbind(card)
        if cost >= casterMana:
            notify('{} pays {} mana'.format(caster, casterMana))
            cost = cost - casterMana
            caster.markers[Mana] = 0
        else:
            notify('{} pays {} mana'.format(caster, str(casterMana-cost)))
            caster.markers[Mana] -= cost
            cost = 0
    
    me.Mana = me.Mana-cost
    if discountsApplied:
        for discount in discountsApplied:
            rememberDiscountUse(mage, discount)

    # 7. Check for counter spells (Jinx, Nullify, Arcane Ward)
    spellCountered = check_for_counter_spells(card, caster, target)
    if spellCountered:
        return False  # Spell was countered, exit early

    #8. Flip the card over
    if card.Type != "Enchantment" and not card.isFaceUp: 
        flipcard(card)
        addDefaultTraits(card)

    #9. Add Equipment Traits to the Mage
    if card.Type == 'Equipment':
        addEqTraitsToMage(card)
        addEqAttacksToMage(card)

    if card.bMageTraits not in ['','{}']:
        addToMageTraits(card)
    
    if card.baTraits not in ['','{}']:
        addTraitsToArena(card)

    if card.bfaTraits not in ['','{}']:
        addFriendlyArenaTraits(card)

    #Add arena traits that already exist
    arenaTraitsList = findArenaTraitsList()
    if arenaTraitsList != []:
        for traitCard in arenaTraitsList:
            if traitCard.baTraits not in ['','[]']:
                currentTraits = getArenaTraits(card)
                newArenaTraits = eval(traitCard.baTraits)
                traitParams = create_trait_params(currentTraits,newArenaTraits,'Arena', card, traitCard)
                update_traits(traitParams)
            if traitCard.bfaTraits not in ['','[]']:
                currentTraits = getArenaTraits(card)
                newArenaTraits = eval(traitCard.baTraits)
                traitParams = create_trait_params(currentTraits,newArenaTraits,'Arena', card, traitCard)
                update_traits(traitParams)

    # Check for Magebane and Magebane Effect
    casterTraits = getTraits(caster)
    if 'Magebane' in casterTraits:
        addDamage(caster)
        notify("{} takes damage from Magebane!\n".format(caster))
    notify("{} pays {} for {}".format(me,str(cost),card))

    if not spellCountered: # If Nullify or Arcane Ward was not reveals -> continue with cards effects
        # Card Effects (Crumble, Defend, etc)
        if getCard('Crumble'):
            crumble(caster)
        if card.name == "Defend":
            defend(target)
        if card.name == "Meltdown":
            meltdown(target)
        if card.name == "Rapid Dismantle":
            selectedEquipment = rapiddismantle(target) # We do this so the prevention cost mechanic can function without changing too much
        if card.name == "Ritual of Kallek":
            ritualofkallek(caster)
        if card.name == "Destroy Magic" and card.isFaceUp:
            destroy_magic(card)

        # Handle destruction spells with prevention costs
        if card.name == "Crumble" and target:
            if destroy_with_prevention(me, target):
                notify('{} destroys {}'.format(me, target))
            else:
                notify('Destruction of {} is prevented'.format(target))
        
        elif card.name == "Dissolve" and selectedEquipment:
            if destroy_with_prevention(me, selectedEquipment):
                notify('{} destroys {}'.format(me, selectedEquipment))
            else:
                notify('Destruction of {} is prevented'.format(selectedEquipment))
        
        elif card.name == "Explode" and selectedEquipment:
            if destroy_with_prevention(me, selectedEquipment):
                notify('{} destroys {}'.format(me, selectedEquipment))
                # Proceed with the attack on the target Mage
                target_mage = getMage()
                attack = getAttackList(card)[0]  # Assuming Explode has one attack defined
                if checkAttackTargetInRange(attack, card, target_mage):
                    computed_attack = computeAttack(attack, card, target_mage)
                    damage_roll, effect_roll = rollDice(computed_attack['dice'])
                    damage, effects = computeRawDamageAndEffects(damage_roll, effect_roll, computed_attack, card, target_mage)
                    d_mana_drain = manaDrain(target_mage, card, computed_attack, damage)
                    applied_dmg, applied_effects = damageReceiptMenu(computed_attack, card, target_mage, damage_roll, d_mana_drain, damage, effects)
                    if applied_dmg is not None:
                        applyDamageAndEffects(computed_attack, card, target_mage, applied_dmg, applied_effects, d_mana_drain)
                        rememberAttackUse(card, target_mage, attack['name'], applied_dmg)
            else:
                notify('Destruction of {} is prevented'.format(selectedEquipment))
        
        elif card.name == "Rapid Dismantle" and selectedEquipment:
            if isinstance(selectedEquipment, list):
                for eq in selectedEquipment:
                    if destroy_with_prevention(me, eq):
                        notify('{} destroys {}'.format(me, eq))
                    else:
                        notify('Destruction of {} is prevented'.format(eq))
        
        elif card.name == "Corrosive Orchid" and selectedEquipment:
            if destroy_with_prevention(me, selectedEquipment):
                notify('{} destroys {}'.format(me, selectedEquipment))
            else:
                notify('Destruction of {} is prevented'.format(selectedEquipment))
        
        elif card.name == "Curse Item" and target:
            if destroy_with_prevention(me, target):
                notify('{} destroys {}'.format(me, target))
            else:
                notify('Destruction of {} is prevented'.format(target))
        
        elif card.name == "Dispel" and target:
            if destroy_with_prevention(me, target):
                notify('{} destroys {}'.format(me, target))
            else:
                notify('Destruction of {} is prevented'.format(target))
        
        elif card.name == "Disperse" and target:
            if destroy_with_prevention(me, target):
                notify('{} destroys {}'.format(me, target.name))
            else:
                notify('Destruction of {} is prevented'.format(target))
        
        elif card.name == "Purge Magic" and target:
            attachments = getAttachedCards(target)
            for attachment in attachments:
                if attachment.Type == 'Enchantment':
                    if destroy_with_prevention(me, attachment):
                        notify('{} destroys {}'.format(me, attachment))
                    else:
                        notify('Destruction of {} is prevented'.format(attachment))

        elif card.name == "Seeking Dispel" and target:
            if destroy_with_prevention(me, target):
                notify('{} destroys {}'.format(me, target))
            else:
                notify('Destruction of {} is prevented'.format(target))
        
        elif card.name == "Remove Curse" and target:
            # Assuming target is a list of selected enchantments for simplicity
            if isinstance(target, list):
                for enchantment in target:
                    if destroy_with_prevention(me, enchantment):
                        notify('{} destroys {}'.format(me, enchantment))
                    else:
                        notify('Destruction of {} is prevented'.format(enchantment))
        
        # Note: Other spells like Meltdown, Clear Mind, Purify, etc., need specific handling in computeBaseCost or separate effect functions

    return not spellCountered

def check_for_counter_spells(card, caster, target):
    """
    Check for all possible counter spells (Jinx, Nullify, Arcane Ward) and return True if the spell is countered.
    """
    spellCountered = False

    # Check for Jinx (attached to caster, counters Quick spells)
    if card.Action == "Quick" and check_for_jinx(caster):
        spellCountered = True
        notify('{} was countered by Jinx.'.format(card.name))
        return spellCountered

    # Check for Nullify and Arcane Ward (attached to target, counter Incantations/Enchantments)
    if target and card.Type in ['Incantation', 'Enchantment']:
        if card.controller != target.controller:
            if check_for_nullify(target, card.Type == 'Enchantment'):
                spellCountered = True
                notify('{} was countered by Nullify.'.format(card.name))
                return spellCountered
        if check_for_arcaneward(target, card.Type == 'Enchantment'):
            spellCountered = True
            notify('{} was countered by Arcane Ward.'.format(card.name))
            return spellCountered

    return spellCountered

def determineCaster(card):
    if card.isBoundTo:
        caster = Card(int(card.isBoundTo))
    else:
        caster = None
    return caster

def computeBaseCost(card, target):
    costStr = card.Cost
    params = {'card':card,'target':target}
    if target and 'X' in costStr:
        variable_dict = {
            'Quicksand'         :   determine_quicksand_cost,
            'Crumble'           :   determine_crumble_cost,
            'Defend'            :   determine_defend_cost,
            'Disarm'            :   determine_disarm_cost,
            'Disperse'          :   determine_disperse_cost,
            'Dispel'            :   determine_dispel_cost,
            'Dissolve'          :   determine_dissolve_cost,
            'Explode'           :   determine_explode_cost,
            'Fizzle'            :   determine_fizzle_cost,
            'Rouse the Beast'   :   determine_rouse_cost,
            'Shift Enchantment' :   determine_shift_enchant_cost,
            'Sleep'             :   determine_sleep_cost,
            'Soul Harvest'      :   determine_SH_cost,
            'Steal Enchantment' :   determine_steal_enchant_cost,
            'Steal Equipment'   :   determine_steal_equipment_cost,
            'Upheaval'          :   determine_upheaval_cost
        }
        if variable_dict.get(card.name):
            correct_op = variable_dict.get(card.name)
            result = correct_op(params) # Expect tuple or single value
            if isinstance(result, tuple):
                return result # (cost, equipmentChoice)
            return result, None # (cost, None) this is here so that we can check equipmentChoice in castSpell for pCost
        else:
            cost = askInteger("This Spell has a variable Cost. \n\n"+
                        "How much would you like to pay?", 0)
    elif not target and 'X' in costStr:
        cost = askInteger("This Spell has a variable Cost. \n\n"+
                        "How much would you like to pay?", 0)
    else:
        cost = int(card.Cost)
    return cost, None

def computeCostAdjustment(caster, mage, spell, target = None):#TODO Test this more
    costAdj = 0
    discountsApplied = []
    traits = getTraits(mage)
    if traits.get('Discount'):
        discountList = traits.get('Discount')
    else:
        discountList = False
        
    if discountList:
        #Once per round discounts:
        for discount in discountList:
            timesUsed = timesHasUsedDiscount(caster, discount)
            if timesUsed < discount['Qty']:
                if mage == caster and canTarget(spell,mage,discount['target'], target) and discount['Caster'] == 'Mage' and not (spell.Type == 'Enchantment' and discount.get('Reveal')):
                    costAdj -= 1
                    discountsApplied.append(discount)
                elif canTarget(spell,mage,discount['target']) and discount['Caster'] == 'Any' and not (spell.Type == 'Enchantment' and discount.get('Reveal')):
                    costAdj -= 1
                    discountsApplied.append(discount)

    if spell.name == 'Slavorg, Fang of the First Moon':
        for card in me.piles['Discard Pile']:
            if 'Animal' in card.Subtype:
                costAdj -= 2

    if caster.markers[RuneofPower]:
        costAdj -= 1
    if target:
        if 'HarshforgePlate' in getTraits(target) and spell.Type in ['Enchantment', 'Incantation'] and caster.controller != target.controller:
            costAdj += 2
    return costAdj, discountsApplied

def checkEnoughMana(cost, manaPool):
    if cost > manaPool:
        whisper('You do not have enough mana to cast that!')
        return False
    else:
        return True

def revealEnchantment(card):
    debug('card: {}'.format(card.name))
    if not card.isFaceUp:
        if card.isAttachedTo not in ['','[]']:
            target = Card(int(card.isAttachedTo))
        else: 
            target = None
        
        if target:
            currentAttachments = eval(target.Attachments)
        else:
            currentAttachments = []
        
        if target and [True for attachment in currentAttachments if Card(attachment).Name==card.Name and Card(attachment).isFaceUp]:
            whisper("There is already a copy of {} attached to {}!".format(card.Name, target.Name))
            return
        rCost = computeRevealCost(card)
        rCost += computeRevealDiscounts(card)
        cost = askInteger("This spell is calculated to cost {} mana. \n\n".format(str(rCost))+
                        "How much would you like to pay?", rCost)
        if cost == None: return
        if not checkEnoughMana(cost, me.Mana): #CHECK: This looks funky to me. return later
            return
        else:
            me.Mana = max(me.Mana-cost,0)
            mage = getMage()
            traits = getTraits(mage)
            discountDict = traits.get('Discount')
            rememberDiscountUse(mage, discountDict)
            notify("{} pays {} mana.\n".format(me,str(cost)))
        
        flipcard(card)
        if card.name == 'Healing Charm':
            healingCharm(target)
        if card.bTraits not in ['','{}'] and target:
            newAttachedTraits = eval(card.bTraits)
            currentTraits = getAttachedTraits(target)
            traitParams = create_trait_params(currentTraits,newAttachedTraits,'Attached', target, card)
            update_traits(traitParams)
        if card.zTraits not in ['','{}']:
            addTraitsToZone(card)
        if card.zfTraits not in ['','{}']:
            addTraitsToZone(card)
        if card.baTraits not in ['','{}']:
            addTraitsToArena(card)
        if eval(getGlobalVariable('adramelechWarlock')) and 'Curse' in card.Subtype and 'Enchantment' in card.Type:
            add_adra_curse(card)
        if card.bAttack != '' and target:
            bestowAttackSpell(card,target)
        
        notify("{} reveals {}!\n".format(me,card))
    return

def computeRevealCost(card):
    if 'X' in card.Reveal_Cost:
        costQuery = askInteger('Non-Standard cost detected. Please enter the base cost of revealing the enchantment.',0)
        if costQuery != None: 
            cost = costQuery
        else:
            return 0
    else:
        traits = getTraits(card)
        attachedTarget = Card(eval(card.isAttachedTo))
        if 'Mage' in attachedTarget.Subtype:
            extraCost = traits.get('Magebind',0)
        else:
            extraCost = 0
        cost = int(card.Reveal_Cost) + extraCost
    return cost

def computeRevealDiscounts(spell):
    mage = getMage()

    costAdj = 0
    traits = getTraits(mage)
    discountList = traits.get('Discount')
    
    if discountList:
        for discount in discountList:

            #debug('discountDict found in reveal')
            timesUsed = timesHasUsedDiscount(mage, discount)
            #Once per round discounts:
            if timesUsed < discount['Qty']:
                if canTarget(spell,mage,discount['target']) and (spell.Type == 'Enchantment' and discount.get('Reveal')):
                    costAdj -=1
    return costAdj

def onCardControllerChanged(args):
    card = args.card
    #debug(args.player.name)
    #debug(args.oldPlayer.name)
    if card.Type == 'Equipment' and card.bTraits != '':
        addEqTraitsToMage(card)
        remoteCall(args.oldPlayer,"remove_eq_traits_from_mage",[card])
    elif card.Type == 'Equipment' and card.bAttack != '':
        addEqAttacksToMage(card)
        remoteCall(args.oldPlayer,"removeBestowedAttack",[card])
    return

def revealAttachmentQuery(attacker, defender = None):
    attackerAttachments = getAttachedCards(attacker)
    if defender:
        defenderAttachments = getAttachedCards(defender)
    else:
        defenderAttachments = []
    attachments = attackerAttachments + defenderAttachments
    recurText = 'an'
    if attachments:
        while True:
            choiceList = []
            for attachment in attachments:
                if attachment.controller == me and not attachment.isFaceUp:
                    choiceList.append(attachment)
            if not choiceList:
                return (False if recurText=='an' else True)
            options = ['{}\n{}'.format(c.Name.center(68,' '),(('('+Card(int(c.isAttachedTo)).Name+')').center(68,' '))) for c in choiceList]
            colors = ['#CC6600' for i in options] #Orange
            options.append('I would not like to reveal an enchantment.')
            colors.append("#de2827")
            choice = askChoice('Would you like to reveal {} enchantment?'.format(recurText),options,colors)
            if choice == len(options): 
                return (False if recurText == 'an' else True)
            revealEnchantment(choiceList[choice-1])
            recurText = 'another'

# Orignal 'check_for_nullify' function as a backup
# def check_for_nullify(target, Enchantment=False):
#     attachmentList = getAttachedCards(target)
#     if attachmentList:
#         for card in attachmentList:
#             if card.name == 'Nullify' and not card.isFaceUp:
#                 if card.controller != target.controller:
#                     return False
#                 return remoteCall(card.controller, 'reveal_nullify', [target, card, Enchantment])
#     return False

def check_for_nullify(target, Enchantment=False):
    attachmentList = getAttachedCards(target)
    if attachmentList:
        for card in attachmentList:
            if card.name == 'Nullify' and not card.isFaceUp:
                if card.controller != target.controller:
                    return False
                return remoteCall(card.controller, 'reveal_nullify', [target, card, Enchantment])
    return False

def reveal_nullify(target, nullify, Enchantment=False):
    rCost = computeRevealCost(nullify)
    choice = askChoice('Would you like to reveal Nullify for {} mana to counter the spell?'.format(rCost), ['Yes', 'No'], ["#01603e", "#de2827"])
    if choice == 1:
        revealEnchantment(nullify)
        notify('{} has countered the spell.'.format(me))
        return True
    else:
        flipcard(nullify)
        notify('{} has chosen for {} to fizzle'.format(me, nullify))
        discard(nullify)
        return False

def check_for_arcaneward(target, Enchantment=False):
    attachmentList = getAttachedCards(target)
    if attachmentList:
        for card in attachmentList:
            if card.name == 'Arcane Ward' and not card.isFaceUp:
                return remoteCall(card.controller, 'reveal_arcaneward', [target, card, Enchantment])
    return False

def reveal_arcaneward(target, arcaneward, Enchantment=False):
    rCost = computeRevealCost(arcaneward)
    choice = askChoice('Would you like to reveal Arcane Ward for {} mana to counter the spell?'.format(rCost), ['Yes', 'No.'], ["#01603e", "#de2827"])
    if choice == 1:
        revealEnchantment(arcaneward)
        notify('{} has countered the spell.'.format(me))
        return True
    else:
        flipcard(arcaneward)
        notify('{} has chosen for {} to fizzle'.format(me, arcaneward))
        discard(arcaneward)
        return False

# New function to check for Jinx
def check_for_jinx(caster):
    attachmentList = getAttachedCards(caster)
    if attachmentList:
        for card in attachmentList:
            if card.name == 'Jinx' and not card.isFaceUp:
                return remoteCall(card.controller, 'reveal_jinx', [caster, card])
    return False

# New function to handle revealing Jinx
def reveal_jinx(caster, jinx):
    rCost = computeRevealCost(jinx)
    choice = askChoice('Would you like to reveal Jinx for {} mana to counter the spell?'.format(rCost), ['Yes', 'No'], ["#01603e", "#de2827"])
    if choice == 1:
        revealEnchantment(jinx)
        if jinx.isFaceUp:
            notify('{} has countered the spell cast by {}'.format(me, caster))
            return True
        else:
            return False
    else:
        flipcard(jinx)
        notify('{} has chosen for {} to fizzle'.format(me, jinx))
        jinx.target()
        return False

# New functions go below here; mostly going to be incantations

def crumble(caster):
    if caster.controller == me:
        me.Mana += 2
        notify("{} gains 2 mana.".format(me))
    return

def defend(target):
    if target.markers[Guard] == 0:
        target.markers[Guard] = 1
    return

def ritualofkallek(caster):
    if caster.controller == me:
        me.Life -= 2
        me.Mana += 3
        notify("{} loses 2 life gains 3 mana (now {} Life and {} Mana).".format(me, me.Life, me.Mana))
    return

def rapiddismantle(target):
    equipmentList = get_faceup_equipment_list(target)
    # Filter for Level 1 equipment only
    level1_equipment = [eq for eq in equipmentList if getTotalCardLevel(eq) == 1]
    if not level1_equipment:
        notify("No Level 1 equipment found on {}.".format(target.name))
        return
    selectedEquipment = create_card_dialog(level1_equipment, 'Select up to 2 Level 1 equipment to destroy', 0, 2)
    if selectedEquipment:
        for eq in selectedEquipment:
            eq.target()
        return selectedEquipment
    return None

def meltdown(target):
    # If the target is controlled by the local player, handle locally
    if target.controller == me:
        meltdown_local(target)
    else:
        # Delegate to the target Mage's controller
        remoteCall(target.controller, 'meltdown_local', [target])
    return

def meltdown_local(target):
    while True:
        equipmentList = get_faceup_equipment_list(target)
        if not equipmentList:
            notify("No equipment found on {}.".format(target.name))
            return
        selectedEquipment = create_card_dialog(equipmentList, 'Select equipment to keep (others will be destroyed)', 0, len(equipmentList))
        if selectedEquipment is None:  # Player canceled
            notify("{} canceled Meltdown's equipment selection.".format(target.controller))
            return
        lifeLoss = len(selectedEquipment)
        confirmText = "You chose to keep {} equipment. You will lose {} Life. Are you sure?".format(lifeLoss, lifeLoss)
        if askChoice(confirmText, ['Yes', 'No'], ["#01603e", "#de2827"]) == 1:
            # Destroy equipment not selected
            destroyedAny = False
            for eq in equipmentList:
                if eq not in selectedEquipment:
                    if destroy_with_prevention(me, eq):
                        notify('{} destroys {}'.format(me, eq))
                        destroyedAny = True
                    else:
                        notify('Destruction of {} is prevented'.format(eq))
            # Apply life loss
            if lifeLoss > 0:
                target.controller.Life -= lifeLoss
                notify("{} loses {} life for keeping {} equipment.".format(target.controller, lifeLoss, lifeLoss))
            if destroyedAny or lifeLoss > 0:
                notify("Meltdown resolves for {}.".format(target))
            return
        # If No, loop back to selection
        notify("{} reconsiders Meltdown's equipment selection.".format(target.controller))

def destroy_magic(card):
    mute()
    # Get the zone where the card is placed
    target_zone = getZoneContaining(card)
    if not target_zone:
        notify("Destroy Magic must be placed in a valid zone to cast.")
        return
    # Get all cards in the target zone
    zone_cards = [c for c in table if getZoneContaining(c) == target_zone]
    # Filter for enchantments (both face-up and face-down)
    enchantments = [c for c in zone_cards if c.Type == 'Enchantment']
    if not enchantments:
        notify("No enchantments found in the target zone.")
        return
    # Attempt to destroy each enchantment with prevention cost checks
    destroyed_any = False
    for enchantment in enchantments:
        if destroy_with_prevention(me, enchantment):
            notify('{} destroys {}'.format(me, enchantment))
            destroyed_any = True
        else:
            notify('Destruction of {} is prevented'.format(enchantment))
    if destroyed_any:
        notify("Destroy Magic resolves, destroying enchantments in zone {}.".format(target_zone['Name']))
    else:
        notify("Destroy Magic resolves, but no enchantments were destroyed in zone {}.".format(target_zone['Name']))
    return
