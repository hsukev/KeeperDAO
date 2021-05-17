from pathlib import Path

from brownie import accounts, config, network, project, web3, Contract
from eth_utils import is_checksum_address
import click

def main():
    ms = "0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7"
    sharerv4 = Contract("0xc491599b9A20c3A2F0A85697Ee6D9434EFa9f503")
    strategyRookDAI = "0xb374387a340e6aA7d78385C4a4aaC6b425A685B0"
    strategyRookUSDC = "0x4140F350c1B67184fE3AaEa314d8C967F99EE8Cc"
    strategyRookWETH = "0xFc84A04478Ffe0B48e46048f4E933A51F4016289"
    kev = "0x1F93b58fb2cF33CfB68E73E94aD6dD7829b1586D"
    wavey = "0x6AFB7c9a6E8F34a3E0eC6b734942a5589A84F44C"
    matt = "0xd9c68eb096db712FFE15ede78B3D020903F8aa30"
    sharerv4.setContributors(
        strategyRookDAI,
        [kev, ms, wavey, matt],
        [800, 100, 90, 10],
        {"from": ms}
    )
    sharerv4.setContributors(
        strategyRookUSDC,
        [kev, ms, wavey, matt],
        [800, 100, 90, 10],
        {"from": ms}
    )
    sharerv4.setContributors(
        strategyRookWETH,
        [kev, ms, wavey, matt],
        [800, 100, 90, 10],
        {"from": ms}
    )
