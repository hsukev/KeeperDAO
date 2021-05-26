import pytest
from brownie import config
from brownie import Contract


# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture
def gov(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def usdc():
    token_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    yield Contract(token_address)

@pytest.fixture
def dai():
    token_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    yield Contract(token_address)


@pytest.fixture
def usdc_whale(accounts):
    yield accounts.at("0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503", force=True)


@pytest.fixture
def amount(accounts, usdc, gov_live):
    amount = 100000 * 10 ** usdc.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.

    reserve = accounts.at("0xd551234ae421e3bcba99a0da6d736074f22192ff", force=True)
    usdc.transfer(gov_live, amount, {"from": reserve})
    yield amount


@pytest.fixture
def weth():
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    yield Contract(token_address)


@pytest.fixture
def rook():
    token_address = "0xfA5047c9c78B8877af97BDcb85Db743fD7313d4a"
    yield Contract(token_address)


@pytest.fixture
def crv_amount(crv, crv_whale):
    yield 100 * 10 ** crv.decimals()


@pytest.fixture
def crv():
    token_address = "0xD533a949740bb3306d119CC777fa900bA034cd52"
    yield Contract(token_address)


@pytest.fixture
def token():
    yield Contract("0x6B175474E89094C44Da98b954EedeAC495271d0F")


@pytest.fixture
def crv_whale(accounts):
    yield accounts.at("0xd2d43555134dc575bf7279f4ba18809645db0f1d", force=True)


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def dai_vault(pm, gov, rewards, guardian, management, usdc):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(usdc, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, gov, live_vault, strategy_live, rewards):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 1000, {"from": gov})
    yield strategy


@pytest.fixture
def strategy_live(Strategy, live_vault, accounts, web3):
    strategy = Strategy.at("0x4140F350c1B67184fE3AaEa314d8C967F99EE8Cc")
    # ms = accounts.at(web3.ens.resolve("brain.ychad.eth"), force=True)
    # # Allocate 1.5% USDC to KeeperDAO
    # yvUSDC = live_vault
    # StrategyAH2EarncyUSDC = "0x86Aa49bf28d03B1A4aBEb83872cFC13c89eB4beD"  # Current Ratio: 32%
    # StrategyKeeperDAOUSDC = strategy
    # params = yvUSDC.strategies(StrategyAH2EarncyUSDC)
    # currentDetbRatio = params.dict()['debtRatio']
    # newDebtRatio = currentDetbRatio - 150  # Give up 1.5%
    # yvUSDC.updateStrategyDebtRatio(StrategyAH2EarncyUSDC, newDebtRatio, {"from": ms})
    # yvUSDC.updateStrategyDebtRatio(StrategyKeeperDAOUSDC, 150, {"from": ms})

    yield strategy


@pytest.fixture
def live_vault(pm):
    yield Contract("0x5f18C75AbDAe578b483E5F43f12a39cF75b973a9")


@pytest.fixture
def gov_live(accounts):
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)


@pytest.fixture
def rook_whale(accounts):
    yield accounts.at("0xb81f5b9bd373b9d0df2e3191a01b8fa9b4d2832a", force=True)


@pytest.fixture
def rook_distributor(accounts):
    yield accounts.at("0x59FF8975c813C1E70Bdf2bCB8C02886928e4eA2D", force=True)


@pytest.fixture
def pool():
    token_address = "0xAaE0633E15200bc9C50d45cD762477D268E126BD"
    yield Contract(token_address)
