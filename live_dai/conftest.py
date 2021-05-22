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
def dai():
    token_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    yield Contract(token_address)


@pytest.fixture
def dai_whale(accounts):
    yield accounts.at("0x5d3a536e4d6dbd6114cc1ead35777bab948e3643", force=True)


@pytest.fixture
def amount(accounts, dai, gov_live, dai_whale):
    amount = 100000 * 10 ** dai.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.

    dai.transfer(gov_live, amount, {"from": dai_whale})
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
def dai_vault(pm, gov, rewards, guardian, management, dai):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(dai, gov, rewards, "", "", guardian)
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
    strategy = Strategy.at("0xb374387a340e6aA7d78385C4a4aaC6b425A685B0")
    ms = accounts.at(web3.ens.resolve("brain.ychad.eth"), force=True)

    yvDAI = live_vault
    StrategyAH2EarncyDAI = "0x7D960F3313f3cB1BBB6BF67419d303597F3E2Fa8"  # Current Ratio: 26.5%
    # StrategyKeeperDAODAI = "0xb374387a340e6aA7d78385C4a4aaC6b425A685B0"  # Current Ratio: 0%
    StrategyKeeperDAODAI = strategy
    params = yvDAI.strategies(StrategyAH2EarncyDAI)
    currentDetbRatio = params.dict()['debtRatio']
    newDebtRatio = currentDetbRatio - 100  # Give up 1%
    yvDAI.updateStrategyDebtRatio(StrategyAH2EarncyDAI, newDebtRatio, {"from": ms})
    yvDAI.updateStrategyDebtRatio(StrategyKeeperDAODAI, 100, {"from": ms})

    yield strategy


@pytest.fixture
def live_vault(pm):
    yield Contract("0x19D3364A399d251E894aC732651be8B0E4e85001")


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
