import brownie

from live_usdc.util import genericStateOfStrat, strategyBreakdown, genericStateOfVault
import urllib.request, json


def test_operation(chain, usdc, live_vault, strategy_live, strategist, amount, usdc_whale, gov_live):
    # Deposit to the live_usdc_vault
    usdc.approve(live_vault.address, amount, {"from": usdc_whale})
    live_vault.deposit(amount, {"from": usdc_whale})
    whale_before = usdc.balanceOf(usdc_whale)

    # harvest
    strategy_live.harvest({"from": gov_live})
    genericStateOfStrat(strategy_live, usdc, live_vault)
    assert strategy_live.estimatedTotalAssets() > 0
    genericStateOfStrat(strategy_live, usdc, live_vault)

    # tend()
    strategy_live.tend({"from": gov_live})

    chain.sleep(21600)
    strategyBreakdown(strategy_live, usdc, live_vault)
    live_vault.withdraw(2 ** 256 - 1, usdc_whale, 70, {"from": usdc_whale})

    assert usdc.balanceOf(usdc_whale) >= whale_before


def test_profitable_harvest(chain, gov_live, usdc, live_vault, strategy_live, strategist, amount, rook_whale, rook,
                            usdc_whale):
    # Deposit to the live_usdc_vault
    usdc.approve(live_vault.address, amount, {"from": usdc_whale})
    live_vault.deposit(amount, {"from": usdc_whale})
    # harvest
    strategy_live.harvest({"from": gov_live})

    assets_before = live_vault.totalAssets()

    # There isn't a way to simulate rewards from the distributor as it requires data from an offchain heroku app
    # The heroku app is updated from mainnet data and is not open sourced

    # arbitrary reward amount from a whale
    rook.transfer(strategy_live.address, 100 * 10 ** 18, {"from": rook_whale})
    print(f'\n---- before harvest')
    strategyBreakdown(strategy_live, usdc, live_vault)
    genericStateOfVault(live_vault, usdc)
    strategy_live.harvest({"from": gov_live})
    chain.sleep(21600)  # 6 hrs
    print(f'\n---- after harvest')
    strategyBreakdown(strategy_live, usdc, live_vault)
    genericStateOfVault(live_vault, usdc)

    assert live_vault.totalAssets() > assets_before


def test_sweep(gov_live, live_vault, strategy_live, usdc, amount, crv, crv_amount, crv_whale, rook):
    # Strategy want usdc doesn't work
    usdc.transfer(strategy_live, amount, {"from": gov_live})
    assert usdc.address == strategy_live.want()
    assert usdc.balanceOf(strategy_live) > 0
    with brownie.reverts("!want"):
        strategy_live.sweep(usdc, {"from": gov_live})

    # live_usdc_vault share usdc doesn't work
    with brownie.reverts("!shares"):
        strategy_live.sweep(live_vault.address, {"from": gov_live})

    # Protected usdc doesn't work
    with brownie.reverts("!protected"):
        strategy_live.sweep(rook, {"from": gov_live})
        strategy_live.sweep(strategy_live.kToken, {"from": gov_live})

    crv.transfer(strategy_live, crv_amount, {"from": crv_whale})
    assert crv.address != strategy_live.want()
    assert crv.balanceOf(strategy_live) == crv_amount
    strategy_live.sweep(crv, {"from": gov_live})
    assert crv.balanceOf(strategy_live) == 0


def test_triggers(gov_live, live_vault, strategy_live, usdc, amount, rook, rook_whale, usdc_whale):
    # Deposit to the live_usdc_vault and harvest
    usdc.approve(live_vault.address, amount, {"from": usdc_whale})
    live_vault.deposit(amount, {"from": usdc_whale})
    strategy_live.harvest({"from": gov_live})
    # harvestTrigger in this strategy is gated by amount of rewards, no reward = no harvest
    assert strategy_live.harvestTrigger(0, {"from": gov_live}) == False
    strategy_live.tendTrigger(0, {"from": gov_live})

    # give it enough reward to trigger harvest
    rook.transfer(strategy_live.address, 100 * 10 ** 18, {"from": rook_whale})
    strategyBreakdown(strategy_live, usdc, live_vault)
    assert strategy_live.harvestTrigger(0, {"from": gov_live}) == True


def test_revoke_strategy_from_vault(usdc, live_vault, strategy_live, amount, gov_live, usdc_whale):
    # Deposit to the vault and harvest
    usdc.approve(live_vault.address, amount, {"from": usdc_whale})
    live_vault.deposit(amount, {"from": usdc_whale})
    live_vault.revokeStrategy(strategy_live.address, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    genericStateOfVault(live_vault, usdc)
    strategyBreakdown(strategy_live, usdc, live_vault)
    assert usdc.balanceOf(live_vault.address) > amount * .99


def test_emergency_exit(usdc, live_vault, strategy_live, strategist, amount, gov_live, usdc_whale):
    # Deposit to the vault
    usdc.approve(live_vault.address, amount, {"from": usdc_whale})
    live_vault.deposit(amount, {"from": usdc_whale})

    # harvest
    strategy_live.harvest({"from": gov_live})
    genericStateOfStrat(strategy_live, usdc, live_vault)
    assert strategy_live.estimatedTotalAssets() > amount * .99

    # set emergency and exit
    strategy_live.setEmergencyExit({"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    assert strategy_live.estimatedTotalAssets() == 0

    genericStateOfVault(live_vault, usdc)


def test_migration(usdc, live_vault, strategy_live, amount, Strategy, gov_live, strategist, gov, new_pool,
                   rook_distributor, rook,
                   weth, rewards, keeper):
    # Deposit to the vault and harvest
    usdc.approve(live_vault.address, amount, {"from": gov_live})
    live_vault.deposit(amount, {"from": gov_live})
    strategy_live.harvest({"from": gov_live})
    assert strategy_live.estimatedTotalAssets() > amount * .99

    # migrate to a new strategy
    new_strategy = gov_live.deploy(Strategy, live_vault, strategist, rewards, keeper, new_pool, gov, rook_distributor,
                                   strategy_live)
    strategy_live.migrate(new_strategy.address, {"from": gov_live})
    assert new_strategy.estimatedTotalAssets() > amount * .99


def test_migration_with_reward(usdc, live_vault, strategy_live, amount, Strategy, gov_live, strategist, gov, new_pool,
                               rook_distributor, rook,
                               weth, rewards, keeper, chain, accounts, web3):
    with urllib.request.urlopen(
            f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{strategy_live.address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)
        nonce = int(data["nonce"], 16)
        signature = data["signature"]

    print(f'\n{amount / 1e18} rooks to claim\n')
    # Deposit to the vault and harvest
    strategy_live.claimRewards(amount, nonce, signature, {'from': gov_live})
    old = strategy_live.estimatedTotalAssets()

    print('old strat')
    strategyBreakdown(strategy_live, usdc, live_vault)

    # migrate to a new strategy
    new_strategy = gov_live.deploy(Strategy, live_vault, strategist, rewards, keeper, new_pool, gov, rook_distributor,
                                   strategy_live)
    live_vault.migrateStrategy(strategy_live, new_strategy.address, {"from": gov_live})
    assert strategy_live.incurredLosses() == new_strategy.incurredLosses()
    assert new_strategy.estimatedTotalAssets() == old

    before = live_vault.totalAssets()
    print('before harvest')
    strategyBreakdown(new_strategy, usdc, live_vault)

    new_strategy.harvest({"from": gov_live})
    chain.sleep(3600 * 12)  # 6 hrs needed for profits to unlock
    chain.mine(1)
    print('after harvest')
    strategyBreakdown(new_strategy, usdc, live_vault)

    assert live_vault.totalAssets() >= before

    print(f'params {live_vault.strategies(new_strategy.address)}')

    ms = accounts.at(web3.ens.resolve("brain.ychad.eth"), force=True)
    live_vault.updateStrategyDebtRatio(new_strategy.address, 0, {"from": ms})
    new_strategy.harvest()

    print('debt 0')
    strategyBreakdown(new_strategy, usdc, live_vault)
    print(f'params {live_vault.strategies(new_strategy.address)}')
    assert new_strategy.estimatedTotalAssets() != 0

    new_strategy.setSunset(True, {"from": gov_live})
    new_strategy.harvest()
    assert new_strategy.estimatedTotalAssets() == 0
