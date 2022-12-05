import logging
from brownie import Lottery, network, config
from scripts.utils import get_account, get_contract, LOCAL_CHAIN_ENV, get_V3Aggregator
from web3 import Web3

logging.basicConfig(level='INFO')

def deploy_lottery(owner, enter_price, **kwargs):
    is_verified = config["networks"][network.show_active()].get("verify")
    price_feed_address = get_V3Aggregator(owner, decimals=kwargs['decimals'], initial_value=kwargs['initial_value'])
    lottery = Lottery.deploy(enter_price, price_feed_address, {'from': owner}, publish_source=is_verified)
    logging.info(f"Lotery Contract deployed by {owner}\nContract Address: {lottery.address}")
    return lottery


def main():
    OWNER = get_account()
    MIN_FEE_USD, DECIMALS, INIT_VALUE = (100, 18, 2000)
    to_wei = lambda amount: Web3.toWei(amount, 'ether')
    deploy_lottery(OWNER, to_wei(MIN_FEE_USD), decimals=DECIMALS, initial_value=to_wei(INIT_VALUE))
