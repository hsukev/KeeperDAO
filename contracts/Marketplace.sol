// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.6.12;

import "../interfaces/marketplace.sol";
import "../interfaces/uniswap.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import {SafeERC20, SafeMath, IERC20, Address} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";


pragma experimental ABIEncoderV2;

contract Marketplace is IMarketplaceV1, Ownable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address constant public weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

    IUniswapV2Router02 public uniswapRouter;

    constructor(address _router) public {
        uniswapRouter = IUniswapV2Router02(_router);
    }

    function swap(IERC20 _fromToken, IERC20 _toToken, uint256 _amountIn, uint256 _amountMinOut, address to) external override {
        if (_amountIn > 0) {
            _fromToken.safeTransferFrom(msg.sender, address(this), _amountIn);
            _fromToken.approve(address(uniswapRouter), _amountIn);
            address[] memory _sellPath = _getPath(address(_fromToken), address(_toToken));
            uniswapRouter.swapExactTokensForTokens(_amountIn, _amountMinOut, _sellPath, to, now);
        }
    }

    function getExpectedReturn(IERC20 _fromToken, IERC20 _toToken, uint256 _amountIn) external view override returns (uint256 returnAmount){
        if (_fromToken == _toToken) {
            return _amountIn;
        }

        if (_amountIn > 0) {
            address[] memory _sellPath = _getPath(address(_fromToken), address(_toToken));
            return uniswapRouter.getAmountsOut(_amountIn, _sellPath)[_sellPath.length - 1];
        } else {
            return 0;
        }
    }

    function currentMarket() external override returns (address){
        return address(uniswapRouter);
    }

    function _getPath(address assetIn, address assetOut) internal view returns (address[] memory path) {
        if (assetIn == weth || assetOut == weth) {
            path = new address[](2);
            path[0] = assetIn;
            path[1] = assetOut;
        } else {
            path = new address[](3);
            path[0] = assetIn;
            path[1] = weth;
            path[2] = assetOut;
        }
    }

    function setUniswap(address _uniswap) external onlyOwner {
        uniswapRouter = IUniswapV2Router02(_uniswap);
    }
}
