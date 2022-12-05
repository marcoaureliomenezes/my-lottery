from scripts.deploy import deploy_lottery
from scripts.utils import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, fund_with_link
from brownie import network
from scripts.deploy import deploy_lottery
import pytest, time


def test_can_be_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        lottery = deploy_lottery()
        account = get_account()
        lottery.startLottery({'from': account})
        lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
        lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
        fund_with_link(lottery)
        lottery.endLottery({'from': account})
        time.sleep(60)
        assert lottery.recentWinner() == account
        assert lottery.balance() == 0

if __name__ == '__main__':
    test_can_be_pick_winner()