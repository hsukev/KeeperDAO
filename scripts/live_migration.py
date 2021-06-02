import urllib.request, json
from brownie import Contract, accounts, web3


def main():
    gov = accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)

    print("\nmigrating StrategyRookUSDC\n")
    yvUSDC = Contract("0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9", owner=gov)
    OldStrategyRookUSDC = Contract("0x4140F350c1B67184fE3AaEa314d8C967F99EE8Cc")
    NewStrategyRookUSDC = Contract("0x2B1a6CB0168aA540ee8D853aB1d10d7A89d6351b")

    print(f'\nOld strategy total: {OldStrategyRookUSDC.estimatedTotalAssets()}\n')

    tx_migrate = yvUSDC.migrateStrategy(OldStrategyRookUSDC, NewStrategyRookUSDC, {"from": gov})
    print(f'\nNew strategy total: {NewStrategyRookUSDC.estimatedTotalAssets()}')



    print("\nmigrating StrategyRookWETH\n")
    yvWETH = Contract("0xa9fE4601811213c340e850ea305481afF02f5b28", owner=gov)
    OldStrategyRookWETH = Contract("0xFc84A04478Ffe0B48e46048f4E933A51F4016289")
    NewStrategyRookWETH = Contract("0xbC0F2FF495eE2eb74A145EDAA457FA4Fa310DAC5")

    print(f'\nOld strategy total: {OldStrategyRookWETH.estimatedTotalAssets()}\n')

    tx_migrate = yvWETH.migrateStrategy(OldStrategyRookWETH, NewStrategyRookWETH, {"from": gov})
    print(f'\nNew strategy total: {NewStrategyRookWETH.estimatedTotalAssets()}')
