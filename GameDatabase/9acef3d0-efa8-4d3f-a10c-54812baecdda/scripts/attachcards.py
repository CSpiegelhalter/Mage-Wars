
def attach(card,target):
    """Controller of <card> may attach it to <target>."""
    mute()
    if card.controller == me:
        #debug('attach')
        addToAttachmentsList(card, target)
        remoteCall(target.controller,'alignAttachments',[target])
        return card,target
    return card,None

def detach(card):
    #debug('detaching {}'.format(card))
    if card.controller == me and not card.isAttachedTo in ['','[]']:
        target = Card(int(card.isAttachedTo))
        updateAdraCurse(card)
        removeFromAttachmentsList(Card(int(card.isAttachedTo)),card)
        removeBestowedAttack(card)
        if card.bTraits != '':
            traitsToRemove = eval(card.bTraits)
            currentTraits = getAttachedTraits(target)
            traitParams = create_trait_params(currentTraits,traitsToRemove,'Attached',target,card,0,True)
            update_traits(traitParams)
        if card.name == 'Drown':
            traitsToRemove = {'Life':-2*card.markers[Suffocate]}
            currentTraits = getTokenTraits(target)
            traitParams = create_trait_params(currentTraits,traitsToRemove,'Token',target,card,0,True)
            update_traits(traitParams)
    elif card.controller != me and not card.isAttachedTo in ['','[]']:
        remoteCall(card.controller, 'removeFromAttachmentsList',[Card(int(card.isAttachedTo)),card])
    return

def getAttachedCards(card):
    attachmentList = []
    if card.Attachments not in ['','[]']:
        for attachment in eval(card.Attachments):
            attachmentList.append(Card(attachment))
    return attachmentList

def addToAttachmentsList(card, target):
    ##debug('adding to list')
    ##debug('card: {}'.format(card))
    ##debug('target: {}'.format(target))
    if len(target.Attachments)==0:
        target.Attachments = str([card._id])
        card.isAttachedTo = str(target._id)
    else:
        attachmentsList = eval(target.Attachments)
        attachmentsList += [card._id]
        target.Attachments = str(attachmentsList)
        card.isAttachedTo = str(target._id)
    return

def removeFromAttachmentsList(cardAttachedTo, removedCard):
    attachmentsList = eval(cardAttachedTo.Attachments)
    attachmentsList.remove(removedCard._id)
    cardAttachedTo.Attachments = str(attachmentsList)
    removedCard.isAttachedTo = ''
    alignAttachments(cardAttachedTo)
    return

def alignAttachments(card):
    #debug('aligning attachments for: {}'.format(card))
    """
    Aligns the attachments of input card.
    Requires that input card belong to calling player

    """
    mute()

    #1: Retrieve attachments and end function if there are none.
    attachmentsString = card.Attachments
    if not attachmentsString or attachmentsString == '[]': return
    attachmentsList = eval(card.Attachments)
    
    #2: Controller of first attachment calls alignCards
    attachmentsList.insert(0, card._id)
    firstAttachment = Card(attachmentsList[1])

    remoteCall(firstAttachment.controller,"alignCards",[attachmentsList,0,-12])

def alignCards(cardList,xOffset,yOffset):
    """
    Input is a list of card objects that need to be aligned. The first card in the list is the card against which the second will be aligned.
    This function is recursive. When called, the first call should be on the card to which the rest are attached.
    The input MUST be a list of length at least 2.
    """
    mute()
    
    #1: Align the second card in the list with the first
    c0,c1 = Card(cardList[0]),Card(cardList[1])
    x0,y0 = c0.position
    x1,y1 = x0 + xOffset, y0 + yOffset

    c1.moveToTable(x1,y1)

    #2: Move the second card beneath the first
    c1.index = c0.index

    #3: Slice the list. If it is now shorter than 2 cards, we are done.
    cardList = cardList[1:]
    if len(cardList)<2: return

    #4: Otherwise, the owner of the second card in the new list calls this function.
    nextCard = Card(cardList[1])
    remoteCall(nextCard.controller,"alignCards",[cardList,xOffset,yOffset])

def canAttach(card,target):
    #debug('canAttach')
    """Determines whether <card> may be attached to <target>"""
    nonEnchantList = ['Tanglevine','Stranglevine','Quicksand','Reinforce']
    if canTarget(target,card) and (card.Type == 'Enchantment' or card.Name in nonEnchantList):    
        if (card==target or not target in table or not card in table): 
            return False
        elif target.attachments not in ['','[]']:
            return checkDuplicateAttachment(card, target)
        else:
            return True
    return False

def checkDuplicateAttachment(card, target):
    for attachment in eval(target.attachments):
        if (Card(attachment).isFaceUp or Card(attachment).controller == me) and Card(attachment).Name == card.Name: 
            return False
        else:
            return True


'''Binding'''
def canBind(card,target):
    """Determines whether <card> may be attached to <target>"""
    if (card==target or not target in table	or not card in table or not target.isFaceUp): 
        return False
    '''Familiars, spawnpoints, spellbind'''
    targetTraits = getTraits(target)
    if 'Familiar' in targetTraits and checkBindTarget(target,card,targetTraits['Familiar']):
        return True
    elif 'Spawnpoint' in targetTraits and checkBindTarget(target,card,targetTraits['Spawnpoint']):
        return True
    elif 'Spellbind' in targetTraits and checkBindTarget(target,card, targetTraits['Spellbind']):
        return True
    return False

def checkBindTarget(target,card,bindReqs):
    ''''Familiar':[{'Type':['Attack'],'School':['Fire'],'Level':2},{'Type':['Enchantment'],'Subtype':['Curse],'Level':2}]'''
    ''''Spawnpoint':[{'Type':['Equipment']}]'''
    ''''Spellbind':[{'Type':['Incantation']}]'''
    for condition in bindReqs:
        if canTarget(card,target,condition):
            return True
    return False

def bind(card,target):
    """Controller of <card> may attach it to <target>."""
    mute()
    if card.controller == me:
        addToBoundList(card, target)
        if card.Type == 'Attack' and 'Familiar' in target.nativeTraits:
            bestowAttackSpell(card, target)
            removeBestowedAttack(card)
        remoteCall(target.controller,'alignBound',[target])
        return card,target
    return card,None

def unbind(card):
    if card.controller == me and not card.isBoundTo in ['','[]']:
        target = Card(int(card.isBoundTo))
        removeFromBoundList(target,card)
        removeBestowedAttack(card, target)
    elif card.controller != me and not card.isBoundTo in ['','[]']:
        remoteCall(card.controller, 'removeFromBoundList',[target,card])
    return

def addToBoundList(card, target):
    if len(target.Bindings)==0:
        target.Bindings = str([card._id])
        card.isBoundTo = str(target._id)
    else:
        notify("{} already has something bound to it".format(target))
    return

def removeFromBoundList(target, card):
    #debug('removing Binding from: {}'.format(target))
    target.Bindings = ''
    card.isBoundTo = ''
    return

def alignBound(card):
    """
    Aligns the card bound to input card.
    Requires that input card belong to calling player

    """
    mute()

    #1: Retrieve bound card and end function if there are none.
    boundStr = card.Bindings
    
    if not boundStr or boundStr == '[]': 
        return
    bound = eval(card.Bindings)

    #2: Align the cards
    cardList = [card._id,bound[0]]
    alignCards(cardList,0,30)


def getSpecificAttachment(card, desiredCard):
    attachments = getAttachedCards(card)
    if attachments:
        for attachment in attachments:
            if attachment.name == desiredCard:
                return attachment


def find_if_cursed_by_me(card):
    cursed = False
    attachments = getAttachedCards(card)
    if attachments:
        for attachment in attachments:
            if 'Curse' in attachment.Subtype and attachment.isFaceUp and me == attachment.controller:
                cursed = True
    return cursed