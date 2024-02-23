from enum import Enum
import random
import time

slptm = 3


def playerInput(player, inpt, hi, lo, neq) -> int:
    if player == 0:
        i = int(input(inpt))
        if i > hi or i < lo or i == neq:
            print("Illegal input, try again")
            return playerInput(player, inpt, hi, lo, neq)
        return i
    else:
        rand = random.randint(lo, hi)
        while(rand == neq):
            rand = random.randint(lo, hi)
        return rand
    
def playerOutput(i, outpt):
    if i == 0:
        print(outpt)

class Cards(Enum):
    DUKE = 0
    AMBASSADOR = 1
    CONTESSA = 2
    CAPTAIN = 3
    ASSASSIN = 4

class Actions(Enum):
    INCOME = 0
    FOREIGNAID = 1
    COUP = 2
    TAX = 3
    ASSASINATE = 4
    STEAL = 5
    EXCHANGE = 6


gameOn = True
turn = 0
coins = [5, 5, 5, 5]
deck = [Cards.DUKE, Cards.DUKE, Cards.DUKE, Cards.ASSASSIN, Cards.ASSASSIN, Cards.ASSASSIN, Cards.CONTESSA, Cards.CONTESSA, Cards.CONTESSA, Cards.CAPTAIN, Cards.CAPTAIN, Cards.CAPTAIN, Cards.AMBASSADOR, Cards.AMBASSADOR, Cards.AMBASSADOR]
random.shuffle(deck)
p1 = [deck.pop(), deck.pop()]
p2 = [deck.pop(), deck.pop()]
p3 = [deck.pop(), deck.pop()]
p4 = [deck.pop(), deck.pop()]
players = [p1, p2, p3, p4]


def exchange(caller):
    playerOutput(caller, "Here are your cards: ")
    count = 0
    if(players[caller][0] != None):
        count += 1
        playerOutput(caller, f"0: {players[caller][0]}")
    if(players[caller][1] != None):
        count += 1
        playerOutput(caller, f"1: {players[caller][1]}")
    playerOutput(caller, "Here are the cards in the deck")
    playerOutput(caller, f"2: {deck[0]}")
    playerOutput(caller, f"3: {deck[1]}")
    playerOutput(caller, f"You can switch {count} cards")
    n = [None, None]
    
    first = playerInput(caller, "Please choose a card ", 3, 0, -1)
    second = -1
    if count == 2 :
        second = playerInput(caller, "Please choose anther card ", 3, 0, first)

    if first == 0 or first == 1:
        n[0] = players[caller][first]
    else:
        n[0] = deck.pop(first-2)

    if second != -1 :
        if second == 0 or second == 1:
            n[1] = players[caller][second]
        else:
            n[1] = deck.pop(second-2)
    else: n[1] = None

    players[caller] = n
    playerOutput(caller, f"Your new cards: {n[0]}, {n[1]}")

    
def isAlive(p) -> bool :
    return players[p][0] != None or players[p][1] != None

def execute(action, caller, target = -1):
    if not(isAlive(caller)) or (target != -1 and not isAlive(target)):
        return
    if action == Actions.INCOME:
        coins[caller] += 1
    elif action == Actions.FOREIGNAID:
        coins[caller] += 2
    elif action == Actions.COUP:
        coins[caller] -= 7
        queryKill(target)
    elif action == Actions.TAX:
        coins[caller] += 3
    elif action == Actions.ASSASINATE:
        coins[caller] -= 3
        queryKill(target)
    elif action == Actions.STEAL:
        c = min(coins[target], 2)
        coins[target] -= c
        coins[caller] += c
    elif action == Actions.EXCHANGE:
        exchange(caller)

def checkAction(action, caller) -> bool:
    if action == Actions.INCOME:
        return True
    elif action == Actions.FOREIGNAID:
        return True
    elif action == Actions.COUP:
        return coins[caller] >= 7
    elif action == Actions.TAX:
        return True
    elif action == Actions.ASSASINATE:
        return coins[caller] >= 3
    elif action == Actions.STEAL:
        return True
    elif action == Actions.EXCHANGE:
        return True

def checkBlocked(action):
    if action == Actions.INCOME:
        return None
    elif action == Actions.FOREIGNAID:
        return [Cards.DUKE]
    elif action == Actions.COUP:
        return None
    elif action == Actions.TAX:
        return True
    elif action == Actions.ASSASINATE:
        return [Cards.CONTESSA]
    elif action == Actions.STEAL:
        return [Cards.AMBASSADOR, Cards.CAPTAIN]
    elif action == Actions.EXCHANGE:
        return None
    
def cardCanPerformAction(card, action) -> bool:
    if action == Actions.INCOME:
        return True
    elif action == Actions.FOREIGNAID:
        return True
    elif action == Actions.COUP:
        return True
    elif action == Actions.TAX:
        return card == Cards.DUKE
    elif action == Actions.ASSASINATE:
        return card == Cards.ASSASSIN
    elif action == Actions.STEAL:
        return card == Cards.CAPTAIN
    elif action == Actions.EXCHANGE:
        return card == Cards.AMBASSADOR

def hasTarget(action) -> bool:
    return action == Actions.COUP or action == Actions.ASSASINATE or action == Actions.STEAL

def printUserPreamble():
    playerOutput(turn, f"Your cards are: {'None' if players[turn][0] == None else players[turn][0]}, {'None' if players[turn][1] == None else players[turn][1]}")
    for i in range(0, 7):
        playerOutput(turn, f"{i}: {Actions._member_names_[i]}{'' if cardCanPerformAction(players[turn][0], list(Actions)[i]) or cardCanPerformAction(players[turn][1], list(Actions)[i]) else '(!)'}")



def challengeAction(challenger, target, action) -> bool:
    if cardCanPerformAction(players[turn][0], action) or cardCanPerformAction(players[turn][1], action):
        print("The challenge was unsuccessful")
        time.sleep(slptm)
        queryKill(challenger)
        return False
    else:
        print("The challenge was successful")
        time.sleep(slptm)
        queryKill(target)
        return True
    
def challengeBlock(challenger, target, action) -> bool:
    blockCards = checkBlocked(action)
    if blockCards.count(players[target][0]) != 0 or blockCards.count(players[target][1]) != 0:
        print("The challenge was unsuccessful")
        time.sleep(slptm)
        queryKill(challenger)
        return False
    else:
        print("The challenge was successful")
        time.sleep(slptm)
        queryKill(target)
        return True
    
def queryKill(p):
    if p == 0:
        playerOutput(p, "Your Cards: ")
        playerOutput(p, f"0: {players[p][0]}")
        playerOutput(p, f"1: {players[p][1]}")
    neq = -1
    if not isAlive(p): return
    # if players[p][0] == None and players[p][0] == None : print("error")
    if players[p][0] == None : neq = 0
    if players[p][1] == None : neq = 1
    # print(players[p])
    # print(f"neq: {neq}")
    kill = playerInput(p, "Please choose a card to kill: ", 1, 0, neq)
    # print(kill)
    print(f"Player {p+1} chose to kill {players[p][kill]}")
    time.sleep(slptm)
    players[p][kill] = None;
    if players[p][0] == None and players[p][1] == None: 
        coins[p] = 0
        print(f"Player {p+1} is dead")
        time.sleep(slptm)

def game():
    global gameOn, turn, coins, deck, p1, p2, p3, p4, players
    gameOn = True
    turn = 0
    coins = [5, 5, 5, 5]
    deck = [Cards.DUKE, Cards.DUKE, Cards.DUKE, Cards.ASSASSIN, Cards.ASSASSIN, Cards.ASSASSIN, Cards.CONTESSA, Cards.CONTESSA, Cards.CONTESSA, Cards.CAPTAIN, Cards.CAPTAIN, Cards.CAPTAIN, Cards.AMBASSADOR, Cards.AMBASSADOR, Cards.AMBASSADOR]
    random.shuffle(deck)
    p1 = [deck.pop(), deck.pop()]
    p2 = [deck.pop(), deck.pop()]
    p3 = [deck.pop(), deck.pop()]
    p4 = [deck.pop(), deck.pop()]
    players = [p1, p2, p3, p4]

    while(gameOn):
        if not(isAlive(turn)):
            turn += 1
            turn = turn % 4
            continue

        win = True
        for i in range(0, 4):
            if i == turn: continue
            if isAlive(i): 
                win = False
                break

        if(win):
            print(f"Player {turn+1} wins")
            gameOn = False
            break

        print()
        print(f"Coins: {coins}")
        print(f"Player {turn+1}'s turn")
        printUserPreamble()
        inpt = playerInput(turn, "Please choose an action: ", 6, 0, -1)
        act = list(Actions)[inpt]

        while(not checkAction(act, turn)):
            playerOutput(turn, "Cannot perform this action, try again")
            inpt = playerInput(turn, "Please choose an action: ", 6, 0, -1)
            act = list(Actions)[inpt]

        target = -1

        if hasTarget(act):
            target = playerInput(turn, "Select a target: ", 4, 1, turn+1)-1

        while (hasTarget(act) and not isAlive(target)):
            playerOutput(turn, "Target is dead")
            target = playerInput(turn, "Select a target: ", 4, 1, turn+1)-1

        time.sleep(slptm)
        print(f"Player {turn+1} executes {act} {f'on player {target+1}' if target != -1 else ''}")

        time.sleep(slptm)

        challengeSuccessful = False

        if(act != Actions.COUP and act != Actions.INCOME and act != Actions.FOREIGNAID):
            for i in range(0, 4):
                if i == turn or not isAlive(i): continue
                res = playerInput(i, "Would you like to challenge? 1:YES 0:NO ", 1, 0, -1)
                if(res == 1):
                    print(f"Player {i+1} is challenging Player {turn+1}")
                    time.sleep(slptm)
                    challengeSuccessful = challengeAction(i, turn, act)
                    break
                else :
                    print(f"Player {i+1} declines to challenge")
                    time.sleep(slptm)


        blocked = False
        if(not(challengeSuccessful) and (act == Actions.FOREIGNAID or act == Actions.STEAL or act == Actions.ASSASINATE)):
            for i in range(0, 4):
                if i == turn or not isAlive(i): continue
                blockCards = checkBlocked(act)
                res = playerInput(i, f"Would you like to block?{'' if blockCards.count(players[i][0]) != 0 or blockCards.count(players[i][1]) != 0 else '(!)'} 1:YES 0:NO ", 1, 0, -1)
                if(res == 1):
                    print(f"Player {i+1} is blocking Player {turn+1}")
                    time.sleep(slptm)
                    blocked = True
                    blockRes = playerInput(turn, "Would you like to challenge the block? 1:YES 0:NO ", 1, 0, -1)
                    if blockRes == 1:
                        print(f"Player {turn+1} is challenging Player {i+1}'s block")
                        time.sleep(slptm)
                        blocked = not(challengeBlock(turn, i, act))
                        break
                    else:
                        print(f"Player {turn+1} declines to challenge")
                        time.sleep(slptm)
                    break
                else :
                    print(f"Player {i+1} declines to block")
                    time.sleep(slptm)

        if (not challengeSuccessful) and (not blocked): execute(act, turn, target)
        time.sleep(slptm)
        turn += 1
        turn = turn % 4
    
    print("GAME OVER")
    rest = int(input("Restart? 1:YES 0:QUIT "))
    if(rest == 1):
        game()
    else: return


game()