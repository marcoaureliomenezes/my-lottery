// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract Lottery is Ownable {

    address payable[] public players;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    } 

    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash; 
    event RequestedRandomness(bytes32 requestId);

    constructor(uint256 _usdEntryFee, address _priceFeedAddress) public {
            usdEntryFee = _usdEntryFee * (10**18);
            ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
            lottery_state = LOTTERY_STATE.CLOSED;
    }

    function getDecimals() public view returns (uint8) {
        return ethUsdPriceFeed.decimals();
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = ethUsdPriceFeed.latestRoundData();
        return uint256(answer * 10**10);
    }

    function getEntranceFee() public view returns (uint256) {
        uint256 adjustedPrice = getPrice();
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }
    
    function enter() payable public {
        // $50,00
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery needs to be open");
        require(msg.value >= getEntranceFee(), "You have no money to enter the Lottery");
        players.push(msg.sender);
    }



    function startLottery() public onlyOwner {
        require(lottery_state == LOTTERY_STATE.CLOSED, "Lottery needs to be closed before open it");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        uint256 sorted_number = uint256(keccak256(abi.encodePacked(
            block.coinbase, msg.sender, block.difficulty, block.timestamp)));
        givePrize(sorted_number);
    }
    
    function givePrize(uint256 _sorted_number) private {
        require(_sorted_number > 0, "random-not-found");
        uint256 indexOfWinner = _sorted_number % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer((30 * address(this).balance) / 40);
        msg.sender.transfer(address(this).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _sorted_number;
    }
}