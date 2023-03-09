from brownie import Lottery, config, network
from scripts.helpful_scripts import get_account, get_contract, LOCAL_BLOCKCHAIN_ENVIRONMENTS, BLOCK_CONFIRMATIONS_FOR_VERIFICATION


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    # then end the lottery
    try:
        ending_transaction = lottery.endLottery({"from": account})
        ending_transaction.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION())
        if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            request_id = ending_transaction.events[0]["requestId"]
            get_contract("vrf_coordinator").fulfillRandomWords(
                request_id, lottery.address, {"from": account}
            )
        print(f"{lottery.recentWinner()} is the new winner!")

    except Exception as E:
        print(
            "An error had occurred: " +
            str(E) + "\nRemember to fund your subscription! \n You can do it with the scripts here, or at https://vrf.chain.link/"
        )
def main():
    end_lottery()
