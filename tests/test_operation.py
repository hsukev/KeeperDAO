import brownie
from brownie import Contract
import requests

from util import genericStateOfStrat, genericStateOfVault, strategyBreakdown


def test_operation(accounts, token, vault, strategy, strategist, amount):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount

    # harvest
    strategy.harvest()
    genericStateOfStrat(strategy, token, vault)

    # tend()
    strategy.tend()

    # withdrawal

    strategyBreakdown(strategy, token, vault)
    vault.withdraw(2 ** 256 - 1, accounts[0], 70, {"from": accounts[0]})

    assert token.balanceOf(accounts[0]) != 0


def test_profitable_harvest(accounts, token, vault, strategy, strategist, amount, rook_whale, rook):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount
    #
    # harvest
    strategy.harvest()
    assert abs(strategy.estimatedTotalAssets() - amount * 0.9936) < 10000

    assets_before = vault.totalAssets()

    # There isn't a way to simulate rewards from the distributor as it requires data from an offchain heroku app
    # The heroku app is updated from mainnet data and is not open sourced

    # arbitrary reward amount from a whale
    rook.transfer(strategy.address, 100 * 10 ** 18, {"from": rook_whale})
    print(f'\n---- before harvest')
    strategyBreakdown(strategy, token, vault)
    genericStateOfVault(vault, token)
    strategy.harvest()

    print(f'\n---- after harvest')
    strategyBreakdown(strategy, token, vault)
    genericStateOfVault(vault, token)

    assert vault.totalAssets() > assets_before


def test_change_debt(gov, token, vault, strategy, strategist, amount):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})

    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()
    # since there's a deposit fee, we just want to check within a reasonable margin like 1%
    assert (amount / 2) * 1.01 > strategy.estimatedTotalAssets() > (amount / 2) * .99

    vault.updateStrategyDebtRatio(strategy.address, 10_000, {"from": gov})
    strategy.harvest()
    # since there's a deposit fee, we just want to check within a reasonable margin like 1%
    assert (amount) * 1.01 > strategy.estimatedTotalAssets() > (amount) * .99

    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()
    # Larger margin bc deposit was never recovered before debtRatio was lowered
    assert amount / 2 * 1.02 > strategy.estimatedTotalAssets() > amount / 2 * .98


def test_sweep(gov, vault, strategy, token, amount, crv, crv_amount, crv_whale, rook):
    # Strategy want token doesn't work
    token.transfer(strategy, amount, {"from": gov})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

    # Protected token doesn't work
    with brownie.reverts("!protected"):
        strategy.sweep(rook, {"from": gov})
        strategy.sweep(strategy.kToken, {"from": gov})

    crv.transfer(strategy, crv_amount, {"from": crv_whale})
    assert crv.address != strategy.want()
    assert crv.balanceOf(strategy) == crv_amount
    strategy.sweep(crv, {"from": gov})
    assert crv.balanceOf(strategy) == 0


def test_triggers(gov, vault, strategy, token, amount, rook, rook_whale):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    strategy.harvest()

    # harvestTrigger in this strategy is gated by amount of rewards, no reward = no harvest
    assert strategy.harvestTrigger(0) == False
    strategy.tendTrigger(0)

    # give it a tiny bit of reward, but not enough to trigger harvest
    rook.transfer(strategy.address, 1 * 10 ** 4, {"from": rook_whale})
    assert strategy.harvestTrigger(0) == False

    # give it enough reward to trigger harvest
    rook.transfer(strategy.address, 1 * 10 ** 18, {"from": rook_whale})
    assert strategy.harvestTrigger(0) == True
