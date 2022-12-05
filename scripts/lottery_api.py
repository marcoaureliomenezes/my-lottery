from brownie import Lottery, network, config
import time
from scripts.utils import get_account, get_contract, fund_with_link


def start_lottery(owner):
    starting_tx = Lottery[-1].startLottery({"from": owner})
    starting_tx.wait(1)
    print("Lottery started!!!")

def enter_lottery(account):
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You enter the lottery!")

def everyone_enter_lottery():
    for i in range(9):
        enter_lottery(get_account(index=i))

def end_lottery(owner):
    lottery = Lottery[-1]
    ending_tx = lottery.endLottery({'from': owner})
    print(f'{lottery.recentWinner()} is the winner!')

def main():
    owner = get_account(index=0)
    start_lottery(owner)
    everyone_enter_lottery()
    end_lottery(owner)
