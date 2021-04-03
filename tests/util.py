from itertools import count
from brownie import Wei, network
import brownie
import requests


def genericStateOfStrat(strategy, currency, vault):
    decimals = currency.decimals()
    print(f"\n----state of {strategy.name()}----")

    print("Want:", currency.balanceOf(strategy) / (10 ** decimals))
    print("Total assets estimate:", strategy.estimatedTotalAssets() / (10 ** decimals))
    strState = vault.strategies(strategy)
    totalDebt = strState[5] / (10 ** decimals)
    debtLimit = strState[2] / (10 ** decimals)
    totalLosses = strState[7] / (10 ** decimals)
    totalReturns = strState[6] / (10 ** decimals)
    print(f"Total Strategy Debt: {totalDebt:.5f}")
    print(f"Strategy Debt Limit: {debtLimit:.5f}")
    print(f"Total Strategy Gains: {totalReturns}")
    print(f"Total Strategy losses: {totalLosses}")
    print("Harvest Trigger:", strategy.harvestTrigger(1000000 * 30 * 1e9))
    print(
        "Tend Trigger:", strategy.tendTrigger(1000000 * 30 * 1e9)
    )  # 1m gas at 30 gwei
    print("Emergency Exit:", strategy.emergencyExit())


def genericStateOfVault(vault, currency):
    decimals = currency.decimals()
    print(f"\n----state of {vault.name()} vault----")
    balance = vault.totalAssets() / (10 ** decimals)
    print(f"Total Assets: {balance:.5f}")
    balance = vault.totalDebt() / (10 ** decimals)
    print("Loose balance in vault:", currency.balanceOf(vault) / (10 ** decimals))
    print(f"Total Debt: {balance:.5f}")


def strategyBreakdown(strategy, currency, vault):
    decimals = currency.decimals()
    print(f'\n----Strategy breakdown for {vault.name()}')
    print(f'balanceOfStaked = ', strategy.balanceOfStaked() / (10 ** decimals))
    print(f'valueOfStaked = ', strategy.valueOfStaked() / (10 ** decimals))
    print(f'balanceOfUnstaked = ', strategy.balanceOfUnstaked() / (10 ** decimals))
    print(f'balanceOfReward = ', strategy.balanceOfReward() / (10 ** decimals))
    print(f'valueOfReward = ', strategy.valueOfReward() / (10 ** decimals))
    print(f'estimatedTotalAsset = ', strategy.estimatedTotalAssets() / (10 ** decimals))
