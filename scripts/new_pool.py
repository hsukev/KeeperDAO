import urllib.request, json
from brownie import Contract, accounts, web3


def main():
    gov = accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)
    new_pool = Contract("0x4F868C1aa37fCf307ab38D215382e88FCA6275E2")

    StrategyRookUSDC = Contract("0x2B1a6CB0168aA540ee8D853aB1d10d7A89d6351b")
    print(f"\nStrategyRookUSDC ETA before {StrategyRookUSDC.estimatedTotalAssets()}\n")
    print("\nset new pool StrategyRookUSDC\n")
    StrategyRookUSDC.setLiquidityPool(new_pool, {'from': gov})
    print(f"\nStrategyRookUSDC ETA after {StrategyRookUSDC.estimatedTotalAssets()}\n")

    StrategyRookDAI = Contract("0xB361a3E75Bc2Ae6c8A045b3A43E2B0c9aD890d48")
    print(f"\nStrategyRookDAI ETA before {StrategyRookDAI.estimatedTotalAssets()}\n")
    print("\nset new pool StrategyRookDAI\n")
    StrategyRookDAI.setLiquidityPool(new_pool, {'from': gov})
    print(f"\nStrategyRookDAI ETA after {StrategyRookDAI.estimatedTotalAssets()}\n")

    StrategyRookWETH = Contract("0xbC0F2FF495eE2eb74A145EDAA457FA4Fa310DAC5")
    print(f"\nStrategyRookWETH ETA before {StrategyRookWETH.estimatedTotalAssets()}\n")
    print("\nset new pool StrategyRookWETH\n")
    StrategyRookWETH.setLiquidityPool(new_pool, {'from': gov})
    print(f"\nStrategyRookWETH ETA after {StrategyRookWETH.estimatedTotalAssets()}\n")