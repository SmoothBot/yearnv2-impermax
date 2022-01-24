import pytest
from brownie import Wei, accounts, chain

import conftest as config


@pytest.mark.parametrize(config.fixtures, config.params, indirect=True)
def test_shutdown(gov, whale, currency, vault, strategy, allocChangeConf, price, scale):
    currency.approve(vault, 2 ** 256 - 1, {"from": gov})

    currency.approve(whale, 2 ** 256 - 1, {"from": whale})
    currency.transferFrom(whale, gov, int(40000 * scale / price), {"from": whale})

    vault.setDepositLimit(int(40000 * scale / price), {"from": gov})
    # Start with 100% of the debt
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 0, {"from": gov})
    # Depositing 80k
    vault.deposit(int(40000 * scale / price), {"from": gov})
    strategy.harvest()

    vault.revokeStrategy(strategy, {"from": gov})
    strategy.harvest()
    assert vault.strategies(strategy).dict()["totalDebt"] == 0
