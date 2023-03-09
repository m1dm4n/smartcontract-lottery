from scripts.helpful_scripts import (
    get_account,
    fund_with_link,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from scripts.Lottery_script.deploy_lottery import deploy_lottery
from scripts.Lottery_script.end_lottery import end_lottery
from scripts.create_subscription import create_subscription, is_funded, fund_subscription
from brownie import exceptions, network, Lottery
import pytest


def init():
    name = network.show_active()
    if name == 'ganache-local' or name not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Local test for development only")
    subscription_id = create_subscription()
    if not is_funded(subscription_id):
        fund_subscription(subscription_id)
    deploy_lottery(subscription_id)


def test_cant_enter_unless_started():
    # Arrange
    init()
    lottery_contract = Lottery[-1]
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery_contract.enter(
            {"from": get_account(), "value": lottery_contract.getEntranceFee() + 10000}
        )


def test_can_start_and_enter_lottery():
    # Arrange
    init()
    lottery_contract = Lottery[-1]

    account = get_account()
    lottery_contract.startLottery({"from": account})
    # Act
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    # Assert
    assert lottery_contract.get_ith_player(0) == account


def test_can_end_lottery():
    # Arrange
    init()
    lottery_contract = Lottery[-1]

    account = get_account()
    lottery_contract.startLottery({"from": account})
    lottery_contract.enter(
        {"from": account, "value": lottery_contract.getEntranceFee()}
    )
    fund_with_link(lottery_contract)
    end_lottery()
    assert lottery_contract.get_lottery_state() == 'Closed'


def test_can_pick_winner_correctly():
    # Arrange
    init()
    lottery_contract = Lottery[-1]

    account = get_account()
    lottery_contract.startLottery({"from": account})
    lottery_contract.enter(
        {"from": get_account(index=1),
         "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=2),
         "value": lottery_contract.getEntranceFee()}
    )
    lottery_contract.enter(
        {"from": get_account(index=3),
         "value": lottery_contract.getEntranceFee()}
    )
    fund_with_link(lottery_contract)
    STATIC_RNG = 777
    winner = get_account(index=1)
    starting_balance_of_account = winner.balance()
    balance_of_lottery = lottery_contract.balance()
    transaction = lottery_contract.endLottery({"from": account})
    request_id = transaction.events[0]["requestId"]
    lottery_contract.rawFulfillRandomWords(
        request_id, [STATIC_RNG], {
            "from": get_contract("vrf_coordinator").address
        }
    )
    # 777 % 3 = 0
    assert lottery_contract.recentWinner() == winner
    assert lottery_contract.balance() == 0
    assert winner.balance() == starting_balance_of_account + balance_of_lottery
