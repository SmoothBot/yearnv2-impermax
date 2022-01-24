import pytest
from brownie import config

fixtures = "currency", "whale", "allocConf", "allocChangeConf", "price"
params = [
    pytest.param( # WFTM
        "0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83", 
        "0x5AA53f03197E08C4851CAD8C92c7922DA5857E5d", 
        [
            "0x5dd76071F7b5F4599d4F2B7c08641843B746ace9",  # FTM-TARROT LP
            "0xD05f23002f6d09Cf7b643B69F171cc2A3EAcd0b3",  # FTM-BOO LP
        ],
        [
            "0x93a97db4fEA1d053C31f0B658b0B87f4b38e105d",  # FTM-SPIRIT LP Highest apr
            "0x7A7dd36BCca42952CC1E67BcA1Be44097fF5b644",  # FTM-BTC LP Spooky 2nd highest apr
            "0x5dd76071F7b5F4599d4F2B7c08641843B746ace9",  # FTM-TARROT LP Spooky
            "0x8C97Dcb6a6b08E8bEECE3D75e918FbC076C094ab",
            "0x6e11aaD63d11234024eFB6f7Be345d1d5b8a8f38",  # USDC-FTM Spirit
            "0x5B80b6e16147bc339e22296184F151262657A327",  # FTM-CRV LP Spooky
            "0xD05f23002f6d09Cf7b643B69F171cc2A3EAcd0b3",  # FTM-BOO LP
        ],
        2.2,
        id="FTM LP TarrotLender",
    ),
    pytest.param( # DAI
        "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E",
        "0x27E611FD27b276ACbd5Ffd632E5eAEBEC9761E40",
        [
            "0xC0C9316D611dd939033Aa3F1e3E9d79B2a8bf58d",
            "0x36bAA3dB4d14F062C879fa41af556B6f42Db6B48",
        ],
        [
            '0xC0C9316D611dd939033Aa3F1e3E9d79B2a8bf58d',
            '0x36bAA3dB4d14F062C879fa41af556B6f42Db6B48',
            '0x31c43aB4827C4eC0e5377dB6A22fE83D3C415Da1',
            '0xC8C57213Af8241b3762cA330Cf4F7Cf7d7157BFc',
        ],
        1,
        id="DAI LP TarrotLender",
    ),
    pytest.param( # WBTC
        "0x321162Cd933E2Be498Cd2267a90534A804051b11",
        "0x38aCa5484B8603373Acc6961Ecd57a6a594510A3",
        [
            '0x1a932bBAD60D390Dbdb7596E4FEd9C215830d9D1',
            '0x967A31b5ad8D194cef342397658b1F8A7e40bCAa',
        ],
        [
            '0x1a932bBAD60D390Dbdb7596E4FEd9C215830d9D1',
            '0x967A31b5ad8D194cef342397658b1F8A7e40bCAa',
            '0x9800ac596E345E6a7179B33DeeaE2eFaf7C9B8E7',
        ],
        40000,
        id="WBTC LP TarrotLender",
    ),
    pytest.param( # WETH
        "0x74b23882a30290451A17c44f4F05243b6b58C76d",
        "0x25c130B2624CF12A4Ea30143eF50c5D68cEFA22f",
        [
            '0x9430cfD7cae4182B87fF8b21554cEB813F50dA38',
            '0x84097529a78121549A75e7b4136d7680aA50502A',
        ],
        [
            '0x9430cfD7cae4182B87fF8b21554cEB813F50dA38',
            '0x84097529a78121549A75e7b4136d7680aA50502A',
            '0x6BB913d4b277Ab2b8DADfF079e244F6e61d08d6C',
            '0xcDA31B40671229776a5F9AEdB6BBFc7E7A62eAe6',
        ],
        2500,
        id="WETH LP TarrotLender",
    ),
]


@pytest.fixture
def andre(accounts):
    # Andre, giver of tokens, and maker of yield
    yield accounts[0]


@pytest.fixture
def gov(accounts):
    # yearn multis... I mean YFI governance. I swear!
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    # YFI Whale, probably
    yield accounts[2]


@pytest.fixture
def strategist(accounts):
    # You! Our new Strategist!
    yield accounts[3]


@pytest.fixture
def keeper(accounts):
    # This is our trusty bot!
    yield accounts[4]


@pytest.fixture
def bob(accounts):
    yield accounts[5]


@pytest.fixture
def alice(accounts):
    yield accounts[6]


@pytest.fixture
def rewards(gov):
    yield gov  # TODO: Add rewards contract


@pytest.fixture
def currency(request, interface):
    yield interface.ERC20(request.param)


@pytest.fixture
def whale(request, accounts):
    acc = accounts.at(request.param, force=True)
    yield acc


@pytest.fixture
def allocConf(request):
    yield request.param


@pytest.fixture
def allocChangeConf(request):
    yield request.param


@pytest.fixture
def price(request):
    yield request.param


@pytest.fixture
def decimals(currency):
    yield currency.decimals()


@pytest.fixture
def scale(decimals):
    yield 10 ** decimals


@pytest.fixture
def vault(pm, gov, rewards, guardian, currency):
    Vault = pm(config["dependencies"][0]).Vault
    vault = gov.deploy(Vault)
    vault.initialize(currency, gov, rewards, "", "", guardian)
    vault.setManagementFee(0, {"from": gov})
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    yield vault


@pytest.fixture
def Strategy(TarotLendingStrategy):
    yield TarotLendingStrategy


@pytest.fixture
def strategy(strategist, keeper, vault, Strategy, allocConf):
    strategy = strategist.deploy(Strategy, vault, allocConf)
    strategy.setKeeper(keeper)
    yield strategy
