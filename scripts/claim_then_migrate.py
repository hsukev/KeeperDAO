import urllib.request, json
from brownie import Contract, accounts, web3


def main():
    gov = accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)
    yvDAI = Contract("0x19D3364A399d251E894aC732651be8B0E4e85001", owner=gov)
    OldStrategyRookDAI = Contract("0xb374387a340e6aA7d78385C4a4aaC6b425A685B0")
    NewStrategyRookDAI = Contract("0xB361a3E75Bc2Ae6c8A045b3A43E2B0c9aD890d48")

    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{OldStrategyRookDAI.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    print(f'\n{amount / 1e18} rooks to claim\n')
    print(f'\nOld strategy total before claim: {OldStrategyRookDAI.estimatedTotalAssets()}\n')

    OldStrategyRookDAI.claimRewards(amount, nonce, signature, {'from': gov})
    print(f'\nOld strategy total: {OldStrategyRookDAI.estimatedTotalAssets()}\n')

    tx_migrate = yvDAI.migrateStrategy(OldStrategyRookDAI, NewStrategyRookDAI, {"from": gov})
    print(f'\nNew strategy total: {NewStrategyRookDAI.estimatedTotalAssets()}')
