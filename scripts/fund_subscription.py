from brownie import config, network, convert
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


def fund_subscription(subscription_id, amount=None):
    print("Funding subscription...")
    account = get_account()
    fund_amount = amount if amount is not None else config["networks"][network.show_active()]["fund_amount"]
    if network.show_active() not in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        link_token = get_contract("link_token")
        vrf_coordinator = get_contract("vrf_coordinator")
        tx = link_token.transferAndCall(
            vrf_coordinator.address,
            fund_amount,
            convert.to_bytes(subscription_id),
            {"from": account},
        )
        tx.wait(1)
    else:
        vrf_coordinator = get_contract("vrf_coordinator")
        tx = vrf_coordinator.fundSubscription(
            subscription_id, fund_amount, {"from": account}
        )
        tx.wait(1)
    print("Subscription Funded!")

def main():
    try:
        subscription_id = int(input("What is your subscription id: ").strip())
        amount = int(input("How many amount you want to fund: ").strip())
        fund_subscription(subscription_id, amount)
    except Exception as E:
        print(str(E))
        exit(1)
    