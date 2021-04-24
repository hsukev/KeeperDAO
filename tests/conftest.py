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

fixtures = "token, amount"
params = [
    pytest.param("0x6b175474e89094c44da98b954eedeac495271d0f", "0xd551234ae421e3bcba99a0da6d736074f22192ff", id="dai"),
    pytest.param("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8", id="usdc"),
    pytest.param("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0x2f0b23f53734252bda2277357e97e1517d6b042a", id="weth"),
    pytest.param("0xEB4C2781e4ebA804CE9a9803C67d0893436bB27D", "0x93054188d876f558f4a66b2ef1d97d16edf0895b", id="renBTC")
]

@pytest.fixture
def token(request):
    yield Contract(request.param)


@pytest.fixture
def dai():
    token_address = "0x6b175474e89094c44da98b954eedeac495271d0f"
    yield Contract(token_address)


@pytest.fixture
def amount(accounts, token, request):
    amount = 1 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.

    reserve = accounts.at(request.param, force=True)
    token.transfer(accounts[0], amount, {"from": reserve})
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
def strategy(strategist, keeper, vault, Strategy, gov):
    strategy = strategist.deploy(Strategy, vault)
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 1000, {"from": gov})
    yield strategy


@pytest.fixture
def rook_whale(accounts):
    yield accounts.at("0xb81f5b9bd373b9d0df2e3191a01b8fa9b4d2832a", force=True)
