from enum import Enum
import random
import time
from openai import OpenAI

slptm = 3


#------------------------------- AGENTS ----------------
transcript = ""

client = OpenAI()

def addToTranscript(ts):
    global transcript
    transcript = transcript + f" \n {ts}"

def chooseAction(caller):
    
    summary = summarizer(transcript, caller)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a player in a game of Coup. You need to select an action to do based on the commands available to you, the context of the situation. Please select which action you would like to perform and why."},
            {"role": "system", "content": "Please answer all queries in first person, starting with I."},
            {"role": "system", "content": f"Here is a summary of the game so far: {summary}"},
            {"role": "system", "content": "Here are the commands available to you: 0:Income, 1:Foreign Aid, 2:Coup, 3:Tax, 4:Assasinate, 5:Steal, 6:Exchange"},
            {"role": "user", "content": f"You are player {caller}. Choose an action and explain why you chose it"},
        ]
    )
    # print(f"Summary: {summary}")
    print(f"Player {caller}: {response.choices[0].message.content}")
    temp = decode(response.choices[0].message.content, "0:Income, 1:Foreign Aid, 2:Coup, 3:Tax, 4:Assasinate, 5:Steal, 6:Exchange")
    # print(temp)
    return temp


def decode(prompt, context):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a action analyzer. You are to analyze which action from a given action set a player is wishing to do. Please output a single number, with no punctuation or letters at all, the number that corresponds to the action the user wishes to do."},
            {"role": "system", "content": context},      
            {"role": "user", "content": prompt},
        ]
    )
    
    return int(response.choices[0].message.content)


def summarizer(prompt, player):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarizer. You summarize games of Coup that have been laid out from the direction of a certain player."},   
            {"role": "user", "content": f"Please summarize the following game of coup so far from the perspective of player {player} in second person format. if there is nothing there, please say that the game has just begun. \n {prompt}"},
            {"role": "user", "content": f"Here are everyone's coins right now. If a person has -1 coins, it means they are dead. Player 1:{coins[0]}, Player 2:{coins[1]}, Player 3:{coins[2]}, Player 4:{coins[3]}"},
        ]
    )
    
    return response.choices[0].message.content

def selectTarget(prompt, player):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a player in a game of Coup. You have just selected to perform a certain action, and now must choose a target for that action."}, 
            {"role": "system", "content": "Please answer all queries in first person, starting with I."},              
            {"role": "user", "content": f"You are player {player}. Please select a target. You can choose player 1, player 2, player 3, player 4. Simply make sure they are not dead already."},
            {"role": "assistant", "content": f"Here is a summary of the game so far: {summarizer(transcript, player)}"},
            {"role": "user", "content": prompt},
        ]
    )
    print(f"Player {player}: {response.choices[0].message.content}")
    return decode(response.choices[0].message.content, "1:Player 1, 2:Player 2, 3:Player 3, 4:Player 4")-1

def makeDecision(prompt, player):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a player in a game of Coup. You are given a decision to make, and you must choose whether you do or do not want to make the decision. Remember that you are answering the question, not asking it. Please choose your option."},   
            {"role": "system", "content": "Please answer all queries in first person, starting with I."},
            {"role": "system", "content": f"You are player {player}"},
            {"role": "assistant", "content": f"Here is a summary of the game so far: {summarizer(transcript, player)}"},
            {"role": "user", "content": prompt},
        ]
    )
    print(f"Player {player}: {response.choices[0].message.content}")
    x = decode(response.choices[0].message.content, "1:Yes, 0:No")
    # print(f"decoded {x}")
    return x

def chooseToKill(prompt, cards, player):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a player in a game of Coup. You must now choose an influence to lose. Please select an influence to lose from your current cards. You cannot choose a card that is None"},   
            {"role": "system", "content": "Please answer all queries in first person, starting with I."},
            {"role": "system", "content": f"You are player {player}"},
            {"role": "assistant", "content": f"Here are your cards: {cards}"},
            {"role": "user", "content": prompt},
        ]
    )
    print(f"Player {player}: {response.choices[0].message.content}")
    # print(cards)
    x = decode(response.choices[0].message.content, cards)
    # print(f"kills {x}")
    return x

def exchangeCards(cardprompt, player, neq):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a player in a game of Coup. You have just chosen the Ambassador's exchange action, and must now choose two cards to exchange your cards for."},   
            {"role": "system", "content": "Please answer all queries in first person, starting with I."},
            {"role": "system", "content": f"You are player {player}"},
            {"role": "assistant", "content": cardprompt},
            {"role": "assistant", "content": f"Please do not choose the following option: {neq}. If this is -1, then ignore this message"},
            {"role": "user", "content": "Please choose a card"},
        ]
    )
    print(f"Player {player}: {response.choices[0].message.content}")
    x = decode(response.choices[0].message.content, cardprompt)
    return x

#------------------------------------------------------

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
    cardprompt = ""
    cardprompt += "Here are your cards: \n"
    count = 0
    if(players[caller][0] != None):
        count += 1
        cardprompt += f"0: {players[caller][0]} \n"
    if(players[caller][1] != None):
        count += 1
        cardprompt += f"1: {players[caller][1]} \n"
    cardprompt += "Here are the cards in the deck \n"
    cardprompt += "2: {deck[0]} \n"
    cardprompt += f"3: {deck[1]} \n"
    cardprompt += f"You can switch {count} cards \n"
    n = [None, None]
    
    first = exchangeCards(cardprompt, caller, -1)
    second = -1
    if count == 2 :
        second = exchangeCards(cardprompt, caller, first)

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
    print(caller, f"Your new cards: {n[0]}, {n[1]}")

    
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
    print(f"Your cards are: {'None' if players[turn][0] == None else players[turn][0]}, {'None' if players[turn][1] == None else players[turn][1]}")
    for i in range(0, 7):
        print(f"{i}: {Actions._member_names_[i]}{'' if cardCanPerformAction(players[turn][0], list(Actions)[i]) or cardCanPerformAction(players[turn][1], list(Actions)[i]) else '(!)'}")



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
    cds = f"Your Cards: "
    cds += f"\n 0: {players[p][0]}"
    cds += f"\n 1: {players[p][1]}"
    
    if not isAlive(p): return
    # print(players[p])
    # print(f"neq: {neq}")
    kill = chooseToKill("Please choose an influence to kill", cds, p+1)
    while(players[p][kill] == None):
        kill = chooseToKill("That card is already dead. Please choose another influence to kill", cds, p+1)
    # print(f"Kills: {kill}")
    # print(kill)
    print(f"Player {p+1} chose to kill {players[p][kill]}")
    time.sleep(slptm)
    players[p][kill] = None;
    if players[p][0] == None and players[p][1] == None: 
        coins[p] = -1
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
        
        print("")
        print(f"Coins: {coins}")
        print(f"Player {turn+1}'s turn")
        printUserPreamble()
        inpt = int(chooseAction(turn+1))
        act = list(Actions)[inpt]

        while(not checkAction(act, turn)):
            print("Cannot perform this action, try again")
            inpt = int(chooseAction(turn+1))
            act = list(Actions)[inpt]

        target = -1 

        if hasTarget(act):
            print(f"Please select a target to perform {act} on")
            target = int(selectTarget(f"Please select a target to perform {act} on", turn+1))

        while (hasTarget(act) and ((not isAlive(target)) or target == turn)):
            target = selectTarget(f"Player {target} is already dead or target is yourself. Please select a different target to perform {act} on", turn+1)

        time.sleep(slptm)
        print(f"Player {turn+1} executes {act} {f'on player {target+1}' if target != -1 else ''}")
        addToTranscript(f"Player {turn+1} executes {act} {f'on player {target+1}' if target != -1 else ''}")

        time.sleep(slptm)

        challengeSuccessful = False

        if(act != Actions.COUP and act != Actions.INCOME and act != Actions.FOREIGNAID):
            print("Would anyone like to challenge?")
            addToTranscript("Would anyone like to challenge?")
            for i in range(0, 4):
                if i == turn or not isAlive(i): continue
                res = makeDecision(f"Would you like to challenge the last action by player {turn+1} to {act}? 1:YES 0:NO ", i+1)
                if(res == 1):
                    addToTranscript(f"Player {i+1} is challenging Player {turn+1}")
                    print(f"Player {i+1} is challenging Player {turn+1}")
                    time.sleep(slptm)
                    challengeSuccessful = challengeAction(i, turn, act)
                    break
                else :
                    print(f"Player {i+1} declines to challenge")
                    addToTranscript(f"Player {i+1} declines to challenge")
                    time.sleep(slptm)


        blocked = False
        if(not(challengeSuccessful) and (act == Actions.FOREIGNAID or act == Actions.STEAL or act == Actions.ASSASINATE)):
            print("Would anyone like to block?")
            addToTranscript("Would anyone like to block?")
            for i in range(0, 4):
                if i == turn or not isAlive(i): continue
                blockCards = checkBlocked(act)
                res = makeDecision(f"Would you like to block the last action by player {turn+1} to {act}? 1:YES 0:NO ", i+1)
                if(res == 1):
                    addToTranscript(f"Player {i+1} is blocking Player {turn+1}")
                    print(f"Player {i+1} is blocking Player {turn+1}")
                    time.sleep(slptm)
                    blocked = True
                    print(f"Would player {turn+1} like to challenge this block?")
                    addToTranscript("Would anyone like to challenge?")
                    blockRes = makeDecision(f"Would you like to challenge the block by player {i+1} on your {act}? 1:YES 0:NO ", turn+1)
                    if blockRes == 1:
                        print(f"Player {turn+1} is challenging Player {i+1}'s block")
                        addToTranscript(f"Player {turn+1} is challenging Player {i+1}'s block")
                        time.sleep(slptm)
                        blocked = not(challengeBlock(turn, i, act))
                        break
                    else:
                        print(f"Player {turn+1} declines to challenge")
                        addToTranscript(f"Player {turn+1} declines to challenge")
                        time.sleep(slptm)
                    break
                else :
                    print(f"Player {i+1} declines to block")
                    addToTranscript(f"Player {i+1} declines to block")
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



