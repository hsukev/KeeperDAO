// SPDX-License-Identifier: AGPL-3.0
pragma solidity >=0.6.0 <0.7.0;
pragma experimental ABIEncoderV2;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IOneSplit {
    function swap(IERC20 fromToken, IERC20 toToken, uint256 amount, uint256 minReturn, uint256[] memory distribution, uint256 disableFlags) external payable;
    function getExpectedReturn(IERC20 fromToken, IERC20 toToken, uint256 amount, uint256 parts, uint256 disableFlags) external view returns (uint256 returnAmount, uint256[] memory distribution);
}