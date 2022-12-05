import logging
from brownie import accounts, network, config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract


NON_FORKED_LOCAL_CHAIN = ["development", "ganache-dadaia"]
FORKED_LOCAL_CHAIN = ["mainnet-fork"]
LOCAL_CHAIN_ENV = NON_FORKED_LOCAL_CHAIN + FORKED_LOCAL_CHAIN


def get_account(**kwargs):
    is_local = network.show_active() in LOCAL_CHAIN_ENV
    if is_local and kwargs.get('index'): return accounts[kwargs["index"]]
    elif is_local and not kwargs.get('index'): return accounts[0]
    elif not is_local and kwargs.get("id"): return accounts.load(kwargs["id"])
    else: return accounts.add(config["wallets"]["from_key"])
   

def deploy_MockV3Aggregator(owner, decimals, initial_value):
    logging.info("Deploying new MockV3Aggregator...")
    price_feed_contract = MockV3Aggregator.deploy(decimals, initial_value, {"from": owner})
    logging.info("New MockV3Aggregator Deployed!")
    return price_feed_contract


def get_V3Aggregator(owner, decimals=18, initial_value=0):
    chain = network.show_active()
    if chain not in LOCAL_CHAIN_ENV:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
        logging.info(f"V3Aggregator address on {chain} network deployed at {price_feed_address}")
        return price_feed_address
    elif len(MockV3Aggregator) == 0:
        new_mock_v3_aggregator = deploy_MockV3Aggregator(owner, decimals, initial_value)
        return new_mock_v3_aggregator.address
    else:
        latest_mock_v3_aggregator = MockV3Aggregator[-1].address
        logging.info(f"MockV3Aggregator address already deployed on address {latest_mock_v3_aggregator}")
        return latest_mock_v3_aggregator


def get_contract(contract_name):
    ACTIVE_NETWORK = config["networks"][network.show_active()]
    CONTRACTS_TO_MOCK = {
        "link_token": LinkToken,"eth_usd_price_feed": MockV3Aggregator,
        "vrf_coordinator": VRFCoordinatorMock,
    }
    contract_type = CONTRACTS_TO_MOCK[contract_name]
    if network.show_active() in NON_FORKED_LOCAL_CHAIN:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = ACTIVE_NETWORK[contract_name]
            contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
        except KeyError:
            print(f"{network.show_active()} address not found!\n",
                  "perhaps you should add it to the config or deploy mocks?",
                  f"brownie run scripts/deploy_mocks.py --network {network.show_active()}")
    return contract


# def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):
#     account =account if account else get_account()
#     link_token = link_token if link_token else get_contract('link_token')
#     tx = link_token.transfer(contract_address, amount, {'from': account})
#     tx.wait(1)
#     print("Fund contract")
#     return tx



#########################################    MOCKS    #######################################


def deploy_LinkToken(deployer):
    print("Deploying LinkToken...")
    link_token_contract = LinkToken.deploy({"from": deployer})
    print("LinkToken Deployed!")
    return link_token_contract

def deploy_VRFCoordinatorMock(deployer, link_token):
    print("Deploying VRFCoordinatorMock...")
    vrf_coordinator_contract = VRFCoordinatorMock.deploy(link_token.address, {"from": deployer})
    print("VRFCoordinatorMock Deployed!")
    return vrf_coordinator_contract


##############################################################################################

def deploy_mocks(decimals=18, initial_value=2000):
    account = get_account()
    deploy_MockV3Aggregator(account, decimals=8, initial_value=200000000000)
    link_token = deploy_LinkToken(account)
    deploy_VRFCoordinatorMock(account, link_token)
    #return mock_price_feed
