def sayYes(group, x=0, y=0):
    notify("{} says Yes".format(me.name))

def sayNo(group, x=0, y=0):
    notify("{} says No".format(me.name))

def sayPass(group, x=0, y=0):
    notify("{} says Pass".format(me.name))

def sayThinking(group, x=0, y=0):
    notify("{} says I am thinking....".format(me.name))

def askThinking(group, x=0, y=0):
    notify("{} asks are you thinking?".format(me.name))

def askYourTurn(group, x=0, y=0):
    notify("{} asks is it your turn?".format(me.name))

def askMyTurn(group, x=0, y=0):
    notify("{} asks is it my turn?".format(me.name))

def askRevealEnchant(group, x=0, y=0):
    notify("{} asks do you wish to Reveal your Enchantment?".format(me.name))

def playerDone(group, x=0, y=0):
	notify("{} is done\n".format(me.name))