import pytest
import brownie
from brownie import Wei, accounts, Contract, config


def test_clone(strategy, strategist, rewards, keeper, vault, Strategy, gov):
    with brownie.reverts():
        strategy.initialize(vault, strategist, rewards, keeper, {"from": gov})

    tx = strategy.cloneStrategy(vault, strategist, rewards, keeper, {"from": gov})
    assert Strategy.at(tx.return_value).name == "sdf"
