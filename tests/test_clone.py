import pytest
import brownie
import test_operation
from brownie import Wei, accounts, Contract, config
from util import genericStateOfStrat, genericStateOfVault, strategyBreakdown
import pytest
import conftest as config


@pytest.mark.parametrize("token, amount", [
    pytest.param("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
                 id="usdc")], indirect=True)
def test_clone(accounts, strategy, strategist, rewards, keeper, vault, Strategy, gov, dai, dai_vault, rook, rook_whale,
               amount, marketplace, pool, rook_distributor, weth):
    with brownie.reverts():
        strategy.init(dai_vault, strategist, rewards, keeper, pool, gov, rook_distributor, {"from": gov})

    transaction = strategy.clone(dai_vault, strategist, rewards, keeper, pool, gov, rook_distributor, {"from": gov})
    cloned_strategy = Strategy.at(transaction.return_value)
    assert cloned_strategy.name() == "StrategyRook Dai Stablecoin"

    with brownie.reverts():
        cloned_strategy.init(dai_vault, strategist, rewards, keeper, pool, gov, rook_distributor, {"from": gov})

    # test harvest for cloned strategy
    # dai whale
    amount = 1 * 10 ** dai.decimals()
    reserve = accounts.at("0xd551234ae421e3bcba99a0da6d736074f22192ff", force=True)
    dai.transfer(accounts[0], amount, {"from": reserve})

    token = dai
    vault = dai_vault
    strategy = cloned_strategy

    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1000, {"from": gov})
    assert token.balanceOf(vault.address) == amount
    #
    # harvest
    strategy.harvest({"from": gov})

    # assert eta is there, accouting for deposit fee

    assert pytest.approx(strategy.estimatedTotalAssets(), rel=amount * 0.0064) == amount

    assets_before = vault.totalAssets()

    # There isn't a way to simulate rewards from the distributor as it requires data from an offchain heroku app
    # The heroku app is updated from mainnet data and is not open sourced

    # arbitrary reward amount from a whale
    rook.transfer(strategy.address, 100 * 10 ** 18, {"from": rook_whale})
    print(f'\n---- before harvest')
    strategyBreakdown(strategy, token, vault)
    genericStateOfVault(vault, token)
    strategy.harvest({"from": gov})

    print(f'\n---- after harvest')
    strategyBreakdown(strategy, token, vault)
    genericStateOfVault(vault, token)

    assert vault.totalAssets() > assets_before
