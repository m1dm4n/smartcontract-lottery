from scripts.helpful_scripts import (
    get_account,
    listen_for_event,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    BLOCK_CONFIRMATIONS_FOR_VERIFICATION
)
from brownie import network, Lottery
import pytest


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Testnet or mainet only!")
    if len(Lottery) == 0:
        pytest.skip(
            "Please deploy this smart contract manually on %s Testnet first" % (
                network.show_active()
            )
        )

    lottery_contract = Lottery[-1]
    block_wait = BLOCK_CONFIRMATIONS_FOR_VERIFICATION()
    account = get_account()
    fee = lottery_contract.getEntranceFee()

    tx = lottery_contract.startLottery({"from": account})
    tx.wait(block_wait)
    print(tx.events["LotteryStart"])

    tx = lottery_contract.enter(
        {"from": account, "value": fee}
    )
    tx.wait(block_wait)
    print(tx.events["PlayerEnter"])
    tx = lottery_contract.enter(
        {"from": account, "value": fee}
    )
    tx.wait(block_wait)
    print(tx.events["PlayerEnter"])
    
    lottery_contract.endLottery({"from": account}).wait(1)
    event = listen_for_event(
        lottery_contract, "WinnerPicked", timeout=None, poll_interval=2
    )
    print(event)
    assert lottery_contract.recentWinner() == account
    assert lottery_contract.get_lottery_state() == 'Closed'
    assert lottery_contract.balance() == 0
