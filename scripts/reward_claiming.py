import urllib.request, json
from brownie import Contract, accounts, web3
import click


def main():
    StrategyRookDAI = Contract("0xB361a3E75Bc2Ae6c8A045b3A43E2B0c9aD890d48")
    StrategyRookUSDC = Contract("0x2B1a6CB0168aA540ee8D853aB1d10d7A89d6351b")
    StrategyRookWETH = Contract("0xbC0F2FF495eE2eb74A145EDAA457FA4Fa310DAC5")

    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{StrategyRookDAI.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    before = StrategyRookDAI.balanceOfReward()

    StrategyRookDAI.claimRewards(amount, nonce, signature, {'from': dev})
    print(f'\n{(StrategyRookDAI.balanceOfReward() - before)/1e18} rooks claimed\n')

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{StrategyRookUSDC.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    before = StrategyRookUSDC.balanceOfReward()
    StrategyRookUSDC.claimRewards(amount, nonce, signature, {'from': dev})
    print(f'\n{(StrategyRookUSDC.balanceOfReward() - before)/1e18} rooks claimed\n')

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{StrategyRookWETH.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    before = StrategyRookWETH.balanceOfReward()

    StrategyRookWETH.claimRewards(amount, nonce, signature, {'from': dev})
    print(f'\n{(StrategyRookWETH.balanceOfReward() - before)/1e18} rooks claimed\n')

