import urllib.request, json
from brownie import Contract, accounts, web3
import click


def main():
    OldStrategyRookUSDC = Contract("0x4140F350c1B67184fE3AaEa314d8C967F99EE8Cc")
    OldStrategyRookWETH = Contract("0xFc84A04478Ffe0B48e46048f4E933A51F4016289")

    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{OldStrategyRookUSDC.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    print(f'OldStrategyRookUSDC has \n{amount / 1e18} rooks to claim\n')
    print(f'\nOld strategy total: {OldStrategyRookUSDC.estimatedTotalAssets()}\n')

    OldStrategyRookUSDC.claimRewards(amount, nonce, signature, {'from': dev})
    print(f'\nOld strategy total after: {OldStrategyRookUSDC.estimatedTotalAssets()}\n')

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{OldStrategyRookWETH.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    print(f'OldStrategyRookWETH has \n{amount / 1e18} rooks to claim\n')
    print(f'\nOld strategy total: {OldStrategyRookWETH.estimatedTotalAssets()}\n')

    OldStrategyRookWETH.claimRewards(amount, nonce, signature, {'from': dev})
    print(f'\nOld strategy total after: {OldStrategyRookWETH.estimatedTotalAssets()}\n')

