import brownie

from live_tests.util import genericStateOfStrat, strategyBreakdown, genericStateOfVault


def test_operation(dai, live_dai_vault, strategy_live, strategist, amount, dai_whale, gov_live):
    # Deposit to the live_dai_vault
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})
    assert dai.balanceOf(live_dai_vault.address) == amount

    # harvest
    strategy_live.harvest({"from": gov_live})
    genericStateOfStrat(strategy_live, dai, live_dai_vault)

    # tend()
    strategy_live.tend({"from": gov_live})

    # withdrawal

    strategyBreakdown(strategy_live, dai, live_dai_vault)
    live_dai_vault.withdraw(2 ** 256 - 1, gov_live, 70, {"from": gov_live})

    assert dai.balanceOf(gov_live) != 0


def test_profitable_harvest(gov_live, dai, live_dai_vault, strategy_live, strategist, amount, rook_whale, rook):
    # Deposit to the live_dai_vault
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})
    assert dai.balanceOf(live_dai_vault.address) == amount
    #
    # harvest
    strategy_live.harvest({"from": gov_live})
    assert abs(strategy_live.estimatedTotalAssets() - amount * 0.9936) < 10000

    assets_before = live_dai_vault.totalAssets()

    # There isn't a way to simulate rewards from the distributor as it requires data from an offchain heroku app
    # The heroku app is updated from mainnet data and is not open sourced

    # arbitrary reward amount from a whale
    rook.transfer(strategy_live.address, 100 * 10 ** 18, {"from": rook_whale})
    print(f'\n---- before harvest')
    strategyBreakdown(strategy_live, dai, live_dai_vault)
    genericStateOfVault(live_dai_vault, dai)
    strategy_live.harvest({"from": gov_live})

    print(f'\n---- after harvest')
    strategyBreakdown(strategy_live, dai, live_dai_vault)
    genericStateOfVault(live_dai_vault, dai)

    assert live_dai_vault.totalAssets() > assets_before


def test_change_debt(gov_live, dai, live_dai_vault, strategy_live, strategist, amount):
    # Deposit to the live_dai_vault and harvest
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})

    live_dai_vault.updateStrategyDebtRatio(strategy_live.address, 5_000, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    # since there's a deposit fee, we just want to check within a reasonable margin like 1%
    assert (amount / 2) * 1.01 > strategy_live.estimatedTotalAssets() > (amount / 2) * .99

    live_dai_vault.updateStrategyDebtRatio(strategy_live.address, 10_000, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    # since there's a deposit fee, we just want to check within a reasonable margin like 1%
    assert (amount) * 1.01 > strategy_live.estimatedTotalAssets() > (amount) * .99

    live_dai_vault.updateStrategyDebtRatio(strategy_live.address, 5_000, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    # Larger margin bc deposit was never recovered before debtRatio was lowered
    assert amount / 2 * 1.02 > strategy_live.estimatedTotalAssets() > amount / 2 * .98


def test_sweep(gov_live, live_dai_vault, strategy_live, dai, amount, crv, crv_amount, crv_whale, rook):
    # Strategy want dai doesn't work
    dai.transfer(strategy_live, amount, {"from": gov_live})
    assert dai.address == strategy_live.want()
    assert dai.balanceOf(strategy_live) > 0
    with brownie.reverts("!want"):
        strategy_live.sweep(dai, {"from": gov_live})

    # live_dai_vault share dai doesn't work
    with brownie.reverts("!shares"):
        strategy_live.sweep(live_dai_vault.address, {"from": gov_live})

    # Protected dai doesn't work
    with brownie.reverts("!protected"):
        strategy_live.sweep(rook, {"from": gov_live})
        strategy_live.sweep(strategy_live.kToken, {"from": gov_live})

    crv.transfer(strategy_live, crv_amount, {"from": crv_whale})
    assert crv.address != strategy_live.want()
    assert crv.balanceOf(strategy_live) == crv_amount
    strategy_live.sweep(crv, {"from": gov_live})
    assert crv.balanceOf(strategy_live) == 0


def test_triggers(gov_live, live_dai_vault, strategy_live, dai, amount, rook, rook_whale):
    # Deposit to the live_dai_vault and harvest
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    # harvestTrigger in this strategy is gated by amount of rewards, no reward = no harvest
    assert strategy_live.harvestTrigger(0, {"from": gov_live}) == False
    strategy_live.tendTrigger(0, {"from": gov_live})

    # give it a tiny bit of reward, but not enough to trigger harvest
    rook.transfer(strategy_live.address, 1 * 10 ** 4, {"from": rook_whale})
    assert strategy_live.harvestTrigger(0, {"from": gov_live}) == False

    # give it enough reward to trigger harvest
    rook.transfer(strategy_live.address, 1 * 10 ** 18, {"from": rook_whale})
    strategyBreakdown(strategy_live, dai, live_dai_vault)
    assert strategy_live.harvestTrigger(0, {"from": gov_live}) == True


def test_revoke_strategy_from_vault(dai, live_dai_vault, strategy_live, amount, gov_live, dai_whale):
    # Deposit to the vault and harvest
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})
    live_dai_vault.revokeStrategy(strategy_live.address, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    genericStateOfVault(live_dai_vault, dai)
    strategyBreakdown(strategy_live, dai, live_dai_vault)
    assert dai.balanceOf(live_dai_vault.address) > amount * .99


def test_emergency_exit(dai, live_dai_vault, strategy_live, strategist, amount, gov_live):
    # Deposit to the vault
    dai.approve(live_dai_vault.address, amount,  {"from": gov_live})
    live_dai_vault.deposit(amount,{"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    assert strategy_live.estimatedTotalAssets() > amount * .99

    # set emergency and exit
    strategy_live.setEmergencyExit({"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    assert strategy_live.estimatedTotalAssets() == 0

    genericStateOfVault(live_dai_vault, dai)


def test_migration(dai, live_dai_vault, strategy_live, amount, Strategy, gov_live):
    # Deposit to the vault and harvest
    dai.approve(live_dai_vault.address, amount, {"from": gov_live})
    live_dai_vault.deposit(amount, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    assert strategy_live.estimatedTotalAssets() > amount * .99

    # migrate to a new strategy
    new_strategy = gov_live.deploy(Strategy, live_dai_vault)
    strategy_live.migrate(new_strategy.address, {"from": gov_live})
    assert new_strategy.estimatedTotalAssets() > amount * .99
