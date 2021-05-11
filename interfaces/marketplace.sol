// SPDX-License-Identifier: AGPL-3.0
pragma solidity >=0.6.0 <0.7.0;
pragma experimental ABIEncoderV2;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IMarketplaceV1 {
    function swap(IERC20 fromToken, IERC20 toToken, uint256 amountIn, uint256 amountOutMin, address to) external;
    function getExpectedReturn(IERC20 fromToken, IERC20 toToken, uint256 amountIn) external view returns (uint256 returnAmount);
    function currentMarket() external returns (address);
}