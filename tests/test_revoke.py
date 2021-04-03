from util import genericStateOfStrat, genericStateOfVault, strategyBreakdown


def test_revoke_strategy_from_vault(token, vault, strategy, amount, gov):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    strategy.harvest()
    assert strategy.estimatedTotalAssets() > amount * .99

    # In order to pass this tests, you will need to implement prepareReturn.
    vault.revokeStrategy(strategy.address, {"from": gov})
    strategy.harvest()
    genericStateOfVault(vault, token)
    strategyBreakdown(strategy, token, vault)
    assert token.balanceOf(vault.address) > amount * .99


def test_emergency_exit(accounts, token, vault, strategy, strategist, amount):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": accounts[0]})
    vault.deposit(amount, {"from": accounts[0]})
    strategy.harvest()
    assert strategy.estimatedTotalAssets() > amount * .99

    # set emergency and exit
    strategy.setEmergencyExit()
    strategy.harvest()
    assert strategy.estimatedTotalAssets() == 0

    genericStateOfVault(vault, token)
