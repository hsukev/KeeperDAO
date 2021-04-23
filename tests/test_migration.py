import pytest
import conftest as config


@pytest.mark.parametrize(config.fixtures, config.params, indirect=True)
def test_migration(token, vault, strategy, amount, Strategy, strategist, gov):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": gov})
    vault.deposit(amount, {"from": gov})
    strategy.harvest()
    assert strategy.estimatedTotalAssets() > amount * .99

    # migrate to a new strategy
    new_strategy = strategist.deploy(Strategy, vault)
    strategy.migrate(new_strategy.address, {"from": gov})
    assert new_strategy.estimatedTotalAssets() > amount * .99
