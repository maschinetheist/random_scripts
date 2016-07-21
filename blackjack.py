#!/usr/bin/env python

import random
import sys
from fabulous.color import magenta, red, blue, blue_bg, red_bg, white, yellow

class CardDeck(object):
    def __init__(self):
        self.card_suits = [ "hearts", "diamonds", "clubs", "spades" ]
        self.card_ranks = {
            "rank_card2": 2,
            "rank_card3": 3,
            "rank_card4": 4,
            "rank_card5": 5,
            "rank_card6": 6,
            "rank_card7": 7,
            "rank_card8": 8,
            "rank_card9": 9,
            "rank_card10": 10,
            "ace": 1,
            "jack": 10,
            "queen": 10,
            "king": 10
        }

    def deal_card(self):
        card_suits = self.card_suits
        card_ranks = self.card_ranks
        
        r_cardsuit = random.choice(card_suits)
        r_cardrank = random.choice(card_ranks.keys())
        if r_cardrank.startswith('rank_card'):
            card = r_cardrank, r_cardsuit, card_ranks[r_cardrank] #, random.randint(2,10)
        elif r_cardrank == 'ace':
            r_ace_suit = random.choice([1,11]) 
            card = r_cardrank, r_cardsuit, r_ace_suit 
        else:
            card = r_cardrank, r_cardsuit, card_ranks[r_cardrank]

        return card


def main():
    dollar_amt = 300
    rounds = 0

    cards = CardDeck()

    def prompt(question):
        print red("\nDraw another card?")
        reply = str(raw_input("[y/n]:")).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False
        else:
            return prompt("Please answer [y|n]")

    def make_bet():
        while True:
            bet = raw_input(" ")
            try: 
                return int(bet)
            except ValueError: 
                print "Enter a real number, fool."

    print blue("\nDraw a hand?")
    reply = str(raw_input("[y/n]:")).lower().strip()
    if reply[0] == 'y':
        while True:
            rounds += 1
            print yellow("Round #: " + str(rounds))
            print "Enter a bet:"

            bet = make_bet()

            print magenta("\nDrawing a random card.")
            dealt_card_1 = cards.deal_card()
            print dealt_card_1
            dealt_card_2 = cards.deal_card()
            print dealt_card_2
            print dealt_card_1[2] + dealt_card_2[2]
            dealt_hand = dealt_card_1[2] + dealt_card_2[2]

            while True:
                if dealt_hand == 21:
                    print blue_bg(white("Blacjack!\n"))
                    dollar_amt = dollar_amt + ( bet * 2 )
                    print "You won: " + str(bet * 2)
                    print "Cash on hand: " + str(dollar_amt)
                    break
                elif dealt_hand <= 21:
                    answer = prompt("Play another card? Please enter Y or N.") 
                    if answer is True:
                        another_card = cards.deal_card()
                        dealt_hand = dealt_hand + another_card[2]
                        print magenta("\nDrawing another card:")
                        print str(another_card)
                    elif answer is False:
                        break
                    #if prompt("Play another card? Please enter Y or N.") is False:
                    #    break
                    else:
                        prompt("Please answer [y|n]")
                elif dealt_hand >= 21:
                    dollar_amt = dollar_amt - bet
                    print "You lose: " + str(bet)
                    print "Cash on hand: " + str(dollar_amt)

                    print red_bg(white("Busted!\n"))
                    break

                print dealt_hand
    if reply[0] == 'n':
        sys.exit(1)
    else:
        return prompt("Please answer [y|n]")

if __name__ == "__main__":
    main()
