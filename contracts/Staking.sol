// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20Minimal {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
    function transfer(address to, uint256 value) external returns (bool);
    function approve(address spender, uint256 value) external returns (bool);
    function balanceOf(address who) external view returns (uint256);
}

interface IRewardToken {
    function mint(address to, uint256 value) external;
}

contract Staking {
    IERC20Minimal public stakeToken;
    IRewardToken public rewardToken;
    address public owner;

    uint256 public rewardRatePerSecond; // reward units per staked token per second, scaled by 1e18
    uint256 public totalStaked;

    struct StakeInfo {
        uint256 amount;
        uint256 rewardPending;
        uint256 lastUpdated;
    }

    mapping(address => StakeInfo) public stakes;

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);
    event RewardRateUpdated(uint256 newRate);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    // Simple reentrancy guard
    uint8 private locked = 1;
    modifier nonReentrant() {
        require(locked == 1, "Reentrant call");
        locked = 2;
        _;
        locked = 1;
    }

    constructor(address _stakeToken, address _rewardToken, uint256 _rewardRatePerSecond) {
        owner = msg.sender;
        stakeToken = IERC20Minimal(_stakeToken);
        rewardToken = IRewardToken(_rewardToken);
        rewardRatePerSecond = _rewardRatePerSecond;
    }

    function _updateRewards(address user) internal {
        StakeInfo storage s = stakes[user];
        if (s.amount > 0) {
            uint256 dt = block.timestamp - s.lastUpdated;
            if (dt > 0) {
                // earned = amount * rewardRatePerSecond * dt / 1e18
                uint256 earned = (s.amount * rewardRatePerSecond * dt) / 1e18;
                s.rewardPending += earned;
            }
        }
        s.lastUpdated = block.timestamp;
    }

    function stake(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot stake zero");
        _updateRewards(msg.sender);
        require(stakeToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        stakes[msg.sender].amount += amount;
        totalStaked += amount;
        emit Staked(msg.sender, amount);
    }

    function withdraw(uint256 amount) external nonReentrant {
        require(amount > 0, "Cannot withdraw zero");
        StakeInfo storage s = stakes[msg.sender];
        require(s.amount >= amount, "Insufficient staked amount");
        _updateRewards(msg.sender);
        s.amount -= amount;
        totalStaked -= amount;
        require(stakeToken.transfer(msg.sender, amount), "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }

    function claimRewards() external nonReentrant {
        _updateRewards(msg.sender);
        StakeInfo storage s = stakes[msg.sender];
        uint256 reward = s.rewardPending;
        if (reward == 0) {
            return;
        }
        s.rewardPending = 0;
        // mint reward tokens to user
        rewardToken.mint(msg.sender, reward);
        emit RewardPaid(msg.sender, reward);
    }

    function setRewardRate(uint256 _newRate) external onlyOwner {
        rewardRatePerSecond = _newRate;
        emit RewardRateUpdated(_newRate);
    }

    // Emergency withdraw by owner (not recommended)
    function rescueToken(address token, address to, uint256 amount) external onlyOwner returns (bool) {
        (bool success, bytes memory data) = token.call(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
        return (success && (data.length == 0 || abi.decode(data, (bool))));
    }
}
