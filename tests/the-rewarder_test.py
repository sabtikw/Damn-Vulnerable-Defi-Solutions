import pytest
from brownie import FlashLoanerPool, TheRewarderPool, DamnValuableToken, RewardToken, AccountingToken, chain, TheRewarderAttack

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def alice(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def bob(accounts):
    return accounts[2]

@pytest.fixture(scope='module')
def charlie(accounts):
    return accounts[3]

@pytest.fixture(scope='module')
def david(accounts):
    return accounts[4]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[5]

@pytest.fixture(scope='module')
def users(alice,bob,charlie,david):
    return [alice,bob,charlie,david]

@pytest.fixture(scope='module')
def liquidityToken(deployer):
    return DamnValuableToken.deploy({'from': deployer})


@pytest.fixture(scope='module')
def flashloanPool(deployer,liquidityToken):  
    return FlashLoanerPool.deploy(liquidityToken.address,{'from': deployer})


@pytest.fixture(scope='module')
def rewardPool(deployer,liquidityToken):  
    return TheRewarderPool.deploy(liquidityToken.address,{'from': deployer})

@pytest.fixture(scope='module')
def rewardToken(rewardPool):  
    return RewardToken.at(rewardPool.rewardToken())


@pytest.fixture(scope='module')
def accountingToken(rewardPool):  
    return AccountingToken.at(rewardPool.accToken())

@pytest.fixture(scope='module',autouse=True)
def setup(liquidityToken,rewardToken,flashloanPool,rewardPool,accountingToken,deployer,users): 
    ''' [Challenge] the rewarder '''

    TOKENS_IN_LENDER_POOL = 1000000e18

    # Set initial token balance of the pool offering flash loans
    liquidityToken.transfer(flashloanPool.address,TOKENS_IN_LENDER_POOL,{'from':deployer})
    
    # Alice, Bob, Charlie and David deposit 100 tokens each
    for user in users:

        amount = 100e18

        liquidityToken.transfer(user.address,amount,{'from':deployer})
        liquidityToken.approve(rewardPool.address,amount,{'from': user})
        rewardPool.deposit(amount,{'from':user})

        assert accountingToken.balanceOf(user) == amount
    
    assert accountingToken.totalSupply() == 400e18
    assert rewardToken.totalSupply() == 0
    
    
    # Advance time 5 days so that depositors can get rewards 
    chain.mine(timedelta=5 * 24 * 60 * 60)
    
    # Each depositor gets 25 reward tokens
    for user in users:

        rewardPool.distributeRewards({'from':user})

        assert rewardToken.balanceOf(user.address) == 25e18

    
    assert rewardToken.totalSupply() == 100e18

    # Two rounds should have occurred so far
    assert rewardPool.roundNumber() == 2


def test_exploit(liquidityToken,flashloanPool,rewardPool,accountingToken,rewardToken,attacker):
    # Exploit goes here
    

    # Advance time 5 days for the  3 round 
    chain.mine(timedelta=5 * 24 * 60 * 60)

    theAttackContract = TheRewarderAttack.deploy(flashloanPool,rewardPool,liquidityToken,rewardToken,{'from':attacker})

    theAttackContract.attack()
    

   

    

    

def test_success(rewardPool,rewardToken,users,attacker):
    # SUCCESS CONDITION 
    
    # Only one round should have taken place
    assert rewardPool.roundNumber() == 3

    # Users should not get more rewards this round
    for user in users:

        rewardPool.distributeRewards({'from':user})

        assert rewardToken.balanceOf(user.address) == 25e18

    # Rewards must have been issued to the attacker account
    rewardToken.totalSupply() > 100e18
    rewardToken.balanceOf(attacker.address) > 0    