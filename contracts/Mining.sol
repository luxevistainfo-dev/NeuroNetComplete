// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Minimal ERC20 implementation used for on-chain rewards.
contract RewardToken {
    string public name = "NeuroNet Reward";
    string public symbol = "NNR";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    address public owner;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function transfer(address to, uint256 value) public returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) public returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) public returns (bool) {
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Allowance exceeded");
        allowance[from][msg.sender] -= value;
        balanceOf[from] -= value;
        balanceOf[to] += value;
        emit Transfer(from, to, value);
        return true;
    }

    function mint(address to, uint256 value) external onlyOwner {
        totalSupply += value;
        balanceOf[to] += value;
        emit Transfer(address(0), to, value);
    }

    function burn(address from, uint256 value) external onlyOwner {
        require(balanceOf[from] >= value, "Insufficient balance to burn");
        balanceOf[from] -= value;
        totalSupply -= value;
        emit Transfer(from, address(0), value);
    }
}

// Mining contract that rewards simple proof-of-work submissions with RewardToken.
contract Mining {
    RewardToken public rewardToken;
    address public owner;

    // Compact target for proof-of-work. Lower = harder.
    uint256 public target;
    uint256 public rewardAmount; // expressed in token smallest unit (wei-like)

    event Mined(address indexed miner, uint256 reward, bytes32 digest, uint256 nonce);
    event TargetUpdated(uint256 newTarget);
    event RewardUpdated(uint256 newReward);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 _initialTarget, uint256 _rewardAmount) {
        owner = msg.sender;
        target = _initialTarget;
        rewardAmount = _rewardAmount;
        // Deploy a RewardToken owned by this contract owner
        rewardToken = new RewardToken();
        // transfer ownership of token to this contract so it can mint? keep owner as deployer to avoid surprises
    }

    // Simple PoW: miner supplies a nonce; hash(msg.sender, nonce, previousBlockHash) must be < target
    function mine(uint256 nonce) external {
        bytes32 digest = keccak256(abi.encodePacked(msg.sender, nonce, blockhash(block.number - 1)));
        require(uint256(digest) < target, "Digest does not meet target");

        // Mint reward to miner.
        // NOTE: rewardToken.owner is the deployer; to allow this contract to mint, the deployer must call rewardToken.approve or mint directly.
        // To keep this demo self-contained, we mint by calling mint on the token contract (owner is this contract when token deployed here),
        // but in our constructor above the deployer becomes owner; to avoid ownership mismatch we mint by calling mint through the token's interface
        // only if this contract is owner. In the deployed flow, you may set token ownership appropriately.
        address tokenOwner = address(rewardToken);
        // If this contract is not the token owner, minting will revert. For real deployments, set up token minting policy appropriately.
        try rewardToken.mint(msg.sender, rewardAmount) {
            // minted
        } catch {
            // If mint fails, do not revert the whole transaction: emit event and return
            emit Mined(msg.sender, 0, digest, nonce);
            return;
        }

        emit Mined(msg.sender, rewardAmount, digest, nonce);
    }

    function setTarget(uint256 _target) external onlyOwner {
        target = _target;
        emit TargetUpdated(_target);
    }

    function setRewardAmount(uint256 _reward) external onlyOwner {
        rewardAmount = _reward;
        emit RewardUpdated(_reward);
    }

    // Allow the owner to withdraw any ERC20 tokens accidentally sent here.
    function rescueToken(address token, address to, uint256 amount) external onlyOwner returns (bool) {
        (bool success, bytes memory data) = token.call(abi.encodeWithSignature("transfer(address,uint256)", to, amount));
        return (success && (data.length == 0 || abi.decode(data, (bool))));
    }
}
