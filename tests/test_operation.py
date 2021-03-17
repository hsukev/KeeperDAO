import brownie
from brownie import Contract
import requests

from util import genericStateOfStrat, genericStateOfVault, strategyBreakdown


# def test_operation(accounts, token, vault, strategy, strategist, amount):
#     # Deposit to the vault
#     token.approve(vault.address, amount, {"from": accounts[0]})
#     vault.deposit(amount, {"from": accounts[0]})
#     assert token.balanceOf(vault.address) == amount
#
#     # harvest
#     strategy.harvest()
#     genericStateOfStrat(strategy, token, vault)
#
#     # tend()
#     strategy.tend()
#
#     # withdrawal
#
#     strategyBreakdown(strategy)
#     vault.withdraw(2 ** 256 - 1, accounts[0], 70, {"from": accounts[0]})
#
#     assert token.balanceOf(accounts[0]) != 0


# def test_emergency_exit(accounts, token, vault, strategy, strategist, amount):
#     # Deposit to the vault
#     token.approve(vault.address, amount, {"from": accounts[0]})
#     vault.deposit(amount, {"from": accounts[0]})
#     strategy.harvest()
#     assert token.balanceOf(strategy.address) == amount
#
#     # set emergency and exit
#     strategy.setEmergencyExit()
#     strategy.harvest()
#     assert token.balanceOf(strategy.address) < amount
#
#

def test_profitable_harvest(accounts, token, vault, strategy, strategist, amount, rook_whale, rook):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    assert token.balanceOf(vault.address) == amount
    #
    # harvest
    strategy.harvest()
    assert abs(strategy.estimatedTotalAssets() - amount * 0.9936) < 10000

    # There isn't a way to simulate rewards from the distributor as it requires data from an offchain heroku app
    # The heroku app is updated from mainnet data and is not open sourced

    # arbitrary reward amount from a whale
    rook.transfer(strategy.address, 100 * 10 ** 18, {"from": rook_whale})
    print(f'---- before harvest')
    strategyBreakdown(strategy)
    strategy.harvest()

    print(f'---- after harvest')
    strategyBreakdown(strategy)
    assert strategy.estimatedTotalAssets() > amount

#
# def test_change_debt(gov, token, vault, strategy, strategist, amount):
#     # Deposit to the vault and harvest
#     token.approve(vault.address, amount, {"from": gov})
#     vault.deposit(amount, {"from": gov})
#     vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
#     strategy.harvest()
#
#     assert token.balanceOf(strategy.address) == amount / 2
#
#     vault.updateStrategyDebtRatio(strategy.address, 10_000, {"from": gov})
#     strategy.harvest()
#     assert token.balanceOf(strategy.address) == amount
#
#     # In order to pass this tests, you will need to implement prepareReturn.
#     # TODO: uncomment the following lines.
#     # vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
#     # assert token.balanceOf(strategy.address) == amount / 2
#
#
# def test_sweep(gov, vault, strategy, token, amount, weth, weth_amout):
#     # Strategy want token doesn't work
#     token.transfer(strategy, amount, {"from": gov})
#     assert token.address == strategy.want()
#     assert token.balanceOf(strategy) > 0
#     with brownie.reverts("!want"):
#         strategy.sweep(token, {"from": gov})
#
#     # Vault share token doesn't work
#     with brownie.reverts("!shares"):
#         strategy.sweep(vault.address, {"from": gov})
#
#     # TODO: If you add protected tokens to the strategy.
#     # Protected token doesn't work
#     # with brownie.reverts("!protected"):
#     #     strategy.sweep(strategy.protectedToken(), {"from": gov})
#
#     weth.transfer(strategy, weth_amout, {"from": gov})
#     assert weth.address != strategy.want()
#     assert weth.balanceOf(gov) == 0
#     strategy.sweep(weth, {"from": gov})
#     assert weth.balanceOf(gov) == weth_amout
#
#
# def test_triggers(gov, vault, strategy, token, amount, weth, weth_amout):
#     # Deposit to the vault and harvest
#     token.approve(vault.address, amount, {"from": gov})
#     vault.deposit(amount, {"from": gov})
#     vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
#     strategy.harvest()
#
#     strategy.harvestTrigger(0)
#     strategy.tendTrigger(0)
