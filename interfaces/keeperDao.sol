// SPDX-License-Identifier: AGPL-3.0

pragma solidity >=0.6.0 <0.7.0;
pragma experimental ABIEncoderV2;

interface IKToken {
    function underlying() external view returns (address);

    function totalSupply() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function transfer(address recipient, uint256 amount) external returns (bool);

    function allowance(address owner, address spender) external view returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);

    function mint(address recipient, uint256 amount) external returns (bool);

    function burnFrom(address sender, uint256 amount) external;

    function addMinter(address sender) external;

    function renounceMinter() external;
}

interface ILiquidityPoolV2 {
    function depositFeeInBips() external returns (uint256);

    function kToken(address _token) external view returns (IKToken);

    function register(IKToken _kToken) external;

    function renounceOperator() external;

    function deposit(address _token, uint256 _amount) external payable returns (uint256);

    function withdraw(address payable _to, IKToken _kToken, uint256 _kTokenAmount) external;

    function borrowableBalance(address _token) external view returns (uint256);

    function underlyingBalance(address _token, address _owner) external view returns (uint256);
}

interface IDistributeV1 {
    function claim(address _to, uint256 _earningsToDate, uint256 _nonce, bytes memory _signature) external;
}