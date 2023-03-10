// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBaseV2, Ownable {
    AggregatorV3Interface internal ethUsdPriceFeed;
    VRFCoordinatorV2Interface immutable COORDINATOR;
    address payable[] private players;
    mapping(address => uint) private Transac_logs;
    address payable public recentWinner;
    enum STATE {
        OPEN,
        CALCULATING,
        CLOSED
    }
    uint32 public immutable callbackGasLimit = 100000;
    uint16 public immutable requestConfirmations = 3;
    uint32 public immutable numWords = 1;
    uint256 public constant usdEntryFee = 5 * (10 ** 18);

    uint64 private subscriptionId;
    bytes32 private keyHash;
    STATE private lottery_state;

    event ReturnedRandomness(uint256 indexed requestId, uint256[] randomWords);
    event LotteryStart(uint256 indexed time);
    event PlayerEnter(address indexed player);
    event WinnerPicked(address indexed player);

    constructor(
        uint64 _subscriptionId,
        address _priceFeedAddress,
        address _vrfCoordinator,
        bytes32 _keyHash
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        subscriptionId = _subscriptionId;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        keyHash = _keyHash;
        lottery_state = STATE.CLOSED;
    }

    function getEntranceFee() public view returns (uint256 costToEnter) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        uint adjust_price = uint(price) * (10 ** 10);
        costToEnter = (usdEntryFee * (10 ** 18)) / adjust_price;
    }

    function get_lottery_state() public view returns (string memory cur_state) {
        if (lottery_state == STATE.OPEN) cur_state = "Opening";
        else if (lottery_state == STATE.CALCULATING)
            cur_state = "Calculating Winner";
        else cur_state = "Closed";
    }

    function get_ith_player(uint idx) public view returns (address) {
        require(idx < players.length, "Index out of range");
        return players[idx];
    }

    function get_player_payment(address player) public view returns (uint) {
        require(
            Transac_logs[player] > 0,
            "That player didn't join our Lottery!"
        );
        return Transac_logs[player];
    }

    function enter() public payable {
        // $5 minimum
        require(lottery_state == STATE.OPEN, "Not open yet!");
        require(msg.value >= getEntranceFee(), "Not enough ETH!");
        players.push(payable(msg.sender));

        emit PlayerEnter(msg.sender);
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lottery_state = STATE.OPEN;

        emit LotteryStart(block.timestamp);
    }

    function endLottery() public onlyOwner {
        require(
            lottery_state != STATE.CALCULATING,
            "Please wait for Lottery finding a Winner!"
        );
        require(lottery_state != STATE.CLOSED, "The lottery didn't start!");
        require(players.length > 0, "Please wait for players entering first!");

        lottery_state = STATE.CALCULATING;
        uint256 requestId = COORDINATOR.requestRandomWords(
            keyHash,
            subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
    }

    function fulfillRandomWords(
        uint256 requestId,
        uint256[] memory randomWords
    ) internal override {
        emit ReturnedRandomness(requestId, randomWords);

        uint256 indexOfWinner = randomWords[0] % players.length;
        recentWinner = players[indexOfWinner];
        players = new address payable[](0);
        lottery_state = STATE.CLOSED;
        (bool success, ) = recentWinner.call{value: address(this).balance}("");
        require(success, "Transfer failed");

        emit WinnerPicked(recentWinner);
    }
}
