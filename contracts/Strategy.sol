// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import {SafeERC20, SafeMath, IERC20, Address} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import {Math} from "@openzeppelin/contracts/math/Math.sol";

import "../interfaces/keeperDao.sol";
import "../interfaces/uniswap.sol";
import "./BaseStrategyEdited.sol";

interface IName {
    function name() external view returns (string memory);
}

contract Strategy is BaseStrategyInitializable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IUniswapV2Router02 constant public uniswapRouter = IUniswapV2Router02(address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D));
    IUniswapV2Router02 constant public sushiswapRouter = IUniswapV2Router02(address(0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F));
    IERC20 public constant weth = IERC20(address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2));
    IERC20 public constant rook = IERC20(address(0xfA5047c9c78B8877af97BDcb85Db743fD7313d4a));
    IUniswapV2Router02 public router;
    IDistributeV1 public distributor;
    IKToken public kToken;
    ILiquidityPool public pool;
    address public treasury;
    address[] public path;
    address[] public wethWantPath;

    // unsigned. Indicates the losses incurred from the protocol's deposit fees
    uint256 public incurredLosses;
    // amount to send to treasury. Used for future governance voting power
    uint256 public percentKeep;
    uint256 public constant _denominator = 10000;

    constructor(address _vault,
        address _strategist,
        address _rewards,
        address _keeper,
        address _pool,
        address _voter,
        address _rewardDistributor,
        address payable _oldStrategy
    ) public BaseStrategyInitializable(_vault) {
        _init(_vault, _strategist, _rewards, _keeper, _pool, _voter, _rewardDistributor, _oldStrategy);
    }

    function clone(
        address _vault,
        address _strategist,
        address _rewards,
        address _keeper,
        address _pool,
        address _voter,
        address _rewardDistributor,
        address payable _oldStrategy
    ) external returns (address payable newStrategy) {
        // Copied from https://github.com/optionality/clone-factory/blob/master/contracts/CloneFactory.sol
        bytes20 addressBytes = bytes20(address(this));

        assembly {
        // EIP-1167 bytecode
            let clone_code := mload(0x40)
            mstore(clone_code, 0x3d602d80600a3d3981f3363d3d373d3d3d363d73000000000000000000000000)
            mstore(add(clone_code, 0x14), addressBytes)
            mstore(add(clone_code, 0x28), 0x5af43d82803e903d91602b57fd5bf30000000000000000000000000000000000)
            newStrategy := create(0, clone_code, 0x37)
        }

        Strategy(newStrategy).init(_vault, _strategist, _rewards, _keeper, _pool, _voter, _rewardDistributor, _oldStrategy);
        emit Cloned(newStrategy);
    }

    function init(
        address _vault,
        address _strategist,
        address _rewards,
        address _keeper,
        address _pool,
        address _voter,
        address _rewardDistributor,
        address payable _oldStrategy
    ) external {
        super._initialize(_vault, _strategist, _rewards, _keeper);
        _init(_vault, _strategist, _rewards, _keeper, _pool, _voter, _rewardDistributor, _oldStrategy);
    }

    function _init(
        address _vault,
        address _strategist,
        address _rewards,
        address _keeper,
        address _pool,
        address _voter,
        address _rewardDistributor,
        address payable _oldStrategy
    ) internal {
        if (_oldStrategy != address(0x0)) {
            Strategy _oldStrategy = Strategy(_oldStrategy);
            require(_oldStrategy.want() == want, "want mismatch");
            incurredLosses = _oldStrategy.incurredLosses();
        }

        // You can set these parameters on deployment to whatever you want
        // maxReportDelay = 6300;
        // profitFactor = 100;
        // debtThreshold = 0;

        // check to see if KeeperDao can actually accept want (renBTC, DAI, USDC, ETH, WETH)
        pool = ILiquidityPool(address(_pool));
        kToken = pool.kToken(address(want));
        require(address(kToken) != address(0x0), "Protocol doesn't support this token!");
        want.safeApprove(address(pool), uint256(- 1));
        kToken.approve(address(pool), uint256(- 1));
        treasury = address(_voter);
        router = uniswapRouter;
        rook.approve(address(uniswapRouter), uint256(- 1));
        rook.approve(address(sushiswapRouter), uint256(- 1));
        distributor = IDistributeV1(address(_rewardDistributor));

        if (address(want) == address(weth)) {
            path = [address(rook), address(weth)];
        } else {
            path = [address(rook), address(weth), address(want)];
            wethWantPath = [address(weth), address(want)];
        }
    }

    function name() external view override returns (string memory) {
        return string(
            abi.encodePacked("StrategyRook ", IName(address(want)).name())
        );
    }

    function estimatedTotalAssets() public view override returns (uint256) {
        return valueOfStaked().add(balanceOfUnstaked()).add(valueOfReward());
    }

    function balanceOfUnstaked() public view returns (uint256){
        return want.balanceOf(address(this));
    }

    // valued in wants
    function valueOfStaked() public view returns (uint256){
        return pool.underlyingBalance(address(want), address(this));
    }

    // kTokens have different virtual prices. Balance != want
    function balanceOfStaked() public view returns (uint256){
        return kToken.balanceOf(address(this));
    }

    function balanceOfReward() public view returns (uint256){
        return rook.balanceOf(address(this));
    }

    function valueOfReward() public view returns (uint256){
        return _estimateAmountsOut(rook.balanceOf(address(this)), path);
    }

    // only way to find out is thru calculating a virtual price this way
    function _inKTokens(uint256 wantAmount) internal view returns (uint256){
        return wantAmount.mul(balanceOfStaked()).div(valueOfStaked());
    }

    function prepareReturn(uint256 _debtOutstanding) internal override returns (uint256 _profit, uint256 _loss, uint256 _debtPayment){
        // NOTE: Return `_profit` which is value generated by all positions, priced in `want`
        // NOTE: Should try to free up at least `_debtOutstanding` of underlying position

        // sell any reward, leave some for treasury
        uint256 rewards = balanceOfReward();
        if (rewards > 0) {
            uint256 rewardsForVoting = rewards.mul(percentKeep).div(_denominator);
            if (rewardsForVoting > 0) {
                IERC20(rook).safeTransfer(treasury, rewardsForVoting);
            }
            uint256 rewardsRemaining = balanceOfReward();
            if (rewardsRemaining > 0) {
                _sell(rewardsRemaining);
            }
        }

        // from selling rewards
        uint256 profit = balanceOfUnstaked();
        // this should be guaranteed if called by keeper. See {harvestTrigger()}
        if (profit > incurredLosses) {
            // we want strategy to pay off its own incurredLosses from deposit fees first so it doesn't have to report _loss to the vault
            _profit = profit.sub(incurredLosses);
        } else {
            _loss = incurredLosses.sub(profit);
        }

        // loss has been recorded.
        incurredLosses = 0;

        if (_debtOutstanding > 0) {
            // withdraw just enough to pay off debt
            uint256 _toWithdraw = Math.min(_debtOutstanding, valueOfStaked());
            pool.withdraw(address(this), kToken, _inKTokens(_toWithdraw));
            uint256 _unstakedWithoutProfit = balanceOfUnstaked().sub(_profit);
            if (_debtOutstanding > _unstakedWithoutProfit) {
                _debtPayment = _unstakedWithoutProfit;
                _loss = _debtOutstanding.sub(_unstakedWithoutProfit);
                if (_profit > _loss) {
                    _profit = _profit.sub(_loss);
                    _loss = 0;
                } else {
                    _profit = 0;
                    _loss = _loss.sub(_profit);
                }
            } else {
                _debtPayment = _debtOutstanding;
                _loss = 0;
            }
        }
    }

    function adjustPosition(uint256 _debtOutstanding) internal override {
        // NOTE: Try to adjust positions so that `_debtOutstanding` can be freed up on *next* harvest (not immediately)
        // deposit any loose balance
        uint256 unstaked = balanceOfUnstaked();
        if (unstaked > 0) {
            _provideLiquidity(unstaked);
        }
    }

    // NAV premium of 0.64% when depositing everytime. Need to keep track of this for _loss calculation.
    function _provideLiquidity(uint256 _amount) private {
        uint256 stakedBefore = valueOfStaked();
        pool.deposit(address(want), _amount);
        uint256 stakedAfter = valueOfStaked();
        uint256 stakedDelta = stakedAfter.sub(stakedBefore);
        uint256 depositFee = _amount.sub(stakedDelta);
        incurredLosses = incurredLosses.add(depositFee);
    }

    function liquidatePosition(uint256 _amountNeeded) internal override returns (uint256 _liquidatedAmount, uint256 _loss) {
        // if _amountNeeded is more than currently available, need to unstake some and/or sell rewards to free up assets
        uint256 unstaked = balanceOfUnstaked();
        if (_amountNeeded > unstaked) {
            uint256 desiredWithdrawAmount = _amountNeeded.sub(unstaked);

            // can't withdraw more than staked
            uint256 actualWithdrawAmount = Math.min(desiredWithdrawAmount, valueOfStaked());

            pool.withdraw(address(this), kToken, _inKTokens(actualWithdrawAmount));

            _liquidatedAmount = balanceOfUnstaked();
            // already withdrew all that it could, any difference left is considered _loss,
            // which is possible because of KeeperDao's initial deposit NAV premium of 0.64%
            // i.e initial 10,000 deposit -> 9,936 in pool. If withdraw immediately, _loss = 64
            _loss = _amountNeeded.sub(_liquidatedAmount);

        } else {
            // already have all of _amountNeeded unstaked
            _liquidatedAmount = _amountNeeded;
            _loss = 0;
        }

        return (_liquidatedAmount, _loss);
    }

    // NOTE: Can override `tendTrigger` and `harvestTrigger` if necessary
    // Since claiming reward is done asynchronously, rewards could sit idle in strategy before next harvest() call
    // See {claimRewards()} for detail
    function prepareMigration(address _newStrategy) internal override {
        kToken.transfer(_newStrategy, balanceOfStaked());
        rook.transfer(_newStrategy, balanceOfReward());
    }

    // Trigger harvest only if strategy has rewards, otherwise, there's nothing to harvest.
    // This logic is added on top of existing gas efficient harvestTrigger() in the parent class
    function harvestTrigger(uint256 callCost) public override view returns (bool) {
        return super.harvestTrigger(_estimateAmountsOut(callCost, wethWantPath)) && balanceOfReward() > 0 && netPositive();
    }

    // Indicator for whether strategy has earned enough rewards to offset incurred losses.
    // Adding this to harvestTrigger() will ensure that strategy will never have to report a positive _loss to the vault and lower its trust
    function netPositive() public view returns (bool){
        return valueOfReward() > incurredLosses;
    }

    // Has to be called manually since this requires off-chain data.
    // Needs to be called before harvesting otherwise there's nothing to harvest.
    function claimRewards(uint256 _earningsToDate, uint256 _nonce, bytes memory _signature) external onlyKeepers {
        require(_earningsToDate > 0, "You are trying to claim 0 rewards");
        distributor.claim(address(this), _earningsToDate, _nonce, _signature);
    }

    function claimRewards(uint256 _earningsToDate, uint256 _nonce, bytes memory _signature, address _distributor) external onlyKeepers {
        require(_earningsToDate > 0, "You are trying to claim 0 rewards");
        IDistributeV1(address(_distributor)).claim(address(this), _earningsToDate, _nonce, _signature);
    }

    function sellSome(uint256 _amount) external onlyAuthorized {
        require(_amount <= balanceOfReward());
        _sell(_amount);
    }

    function _sell(uint256 _amount) internal {
        // since claiming is async, no point in selling if strategy hasn't claimed rewards
        router.swapExactTokensForTokens(_amount, uint256(0), path, address(this), now);
    }

    function _estimateAmountsOut(uint256 _amount, address[] memory sellPath) public view returns (uint256){
        uint256 amountOut = 0;
        if (sellPath.length <= 0) {
            return _amount;
        }

        if (_amount > 0) {
            amountOut = router.getAmountsOut(_amount, sellPath)[sellPath.length - 1];
        }
        return amountOut;
    }

    function protectedTokens() internal view override returns (address[] memory){
        address[] memory protected = new address[](2);
        protected[0] = address(kToken);
        protected[1] = address(rook);
        return protected;
    }

    function setKeep(uint256 _percentKeep) external onlyGovernance {
        percentKeep = _percentKeep;
    }

    function setDistributor(address _distributor) external onlyGovernance {
        distributor = IDistributeV1(address(_distributor));
    }

    function setTreasury(address _treasury) external onlyGovernance {
        treasury = _treasury;
    }

    function setLiquidityPool(address _pool) external onlyGovernance {
        want.safeApprove(address(_pool), uint256(- 1));
        kToken.approve(address(_pool), uint256(- 1));
        pool = ILiquidityPool(_pool);
    }

    function currentDepositFee() external view returns (uint256){
        return pool.depositFeeInBips();
    }

    function switchDex(bool isUniswap) external onlyAuthorized {
        if (isUniswap) router = uniswapRouter;
        else router = sushiswapRouter;
    }

    receive() external payable {}
}
