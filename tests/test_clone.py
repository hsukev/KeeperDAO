import pytest
import brownie
from brownie import Wei, accounts, Contract, config


@pytest.mark.require_network("mainnet-fork")
def test_clone(strategy, strategist, rewards, keeper, vault, Strategy, gov, dai_vault):
    with brownie.reverts():
        strategy.initialize(vault, strategist, rewards, keeper, {"from": gov})

    tx = strategy.cloneStrategy(dai_vault, strategist, rewards, keeper, {"from": gov})
    assert Strategy.at(tx.return_value).name == "sdf"
