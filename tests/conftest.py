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
    pytest.param("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "0xeadb3840596cabf312f2bc88a4bb0b93a4e1ff5f", id="weth"),
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
    amount = 100000 * 10 ** token.decimals()
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
    vault.initialize(token, gov, rewards, "", "", guardian, {"from": gov})
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def dai_vault(pm, gov, rewards, guardian, management, dai):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(dai, gov, rewards, "", "", guardian, {"from": gov})
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, gov, weth, rewards, pool, rook_distributor, zero_address):
    strategy = strategist.deploy(Strategy, vault, strategist, rewards, keeper, pool, gov, rook_distributor, zero_address)
    strategy.setKeeper(keeper, {"from": gov})
    vault.addStrategy(strategy, 10_000, 0, 1000, {"from": gov})
    yield strategy


@pytest.fixture
def marketplace():
    token_address = "0xAab367F214340d94482984521C30b639525D8182"
    yield Contract(token_address)

@pytest.fixture
def rook_whale(accounts):
    yield accounts.at("0xb81f5b9bd373b9d0df2e3191a01b8fa9b4d2832a", force=True)


@pytest.fixture
def uniswap_v2_router(accounts):
    yield accounts.at("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", force=True)


@pytest.fixture
def rook_distributor(accounts):
    yield accounts.at("0x59FF8975c813C1E70Bdf2bCB8C02886928e4eA2D", force=True)


@pytest.fixture
def pool():
    token_address = "0xAaE0633E15200bc9C50d45cD762477D268E126BD"
    yield Contract(token_address)

@pytest.fixture
def zero_address(accounts):
    token_address = "0x0000000000000000000000000000000000000000"
    yield accounts.at(token_address, force=True)
