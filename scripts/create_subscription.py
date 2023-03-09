from brownie import config, network
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from scripts.fund_subscription import fund_subscription
from pathlib import Path
import yaml


def create_subscription():
    if config["networks"][network.show_active()].get("subscription_id", False) == False:
        account = get_account()
        vrf_coordinator = get_contract("vrf_coordinator")
        print("Creating subscription...")
        tx = vrf_coordinator.createSubscription({"from": account})
        tx.wait(1)
        # subscription_id = tx.return_value # You'd need a strong RPC to use this!
        subscription_id = tx.events[0]["subId"]
        if isinstance(subscription_id, bytes):
            subscription_id = int.from_bytes(subscription_id, 'big')
        config_path = Path("brownie-config.yaml").absolute()
        print(f"Your subscription Id is {subscription_id}")
        if network.show_active() == 'ganache-local' or network.show_active() not in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
            with open(config_path, "r") as file:
                configuration = yaml.safe_load(file)
                configuration["networks"][network.show_active()][
                    "subscription_id"
                ] = int(subscription_id)
            with open(config_path, "w") as file:
                yaml.dump(configuration, file)
            print("Subscription ID Saved!")
    else:
        subscription_id = config["networks"][network.show_active(
        )]["subscription_id"]
        print(f"You already have subscription {subscription_id}")
    return subscription_id


def is_funded(subscription_id):
    print(f"Getting details for sub_id {subscription_id}...")
    vrf_coordinator = get_contract("vrf_coordinator")
    fund_amount = config["networks"][network.show_active()]["fund_amount"]
    try:
        subscription_details = vrf_coordinator.getSubscription(subscription_id)
    except Exception:
        print("You may need to delete the subscription id in brownie-config.yaml and create a new one!")
        exit(1)
    print(f"Subscription details: {subscription_details}")
    if subscription_details[0] >= fund_amount:
        return True
    return False

def main():
    subscription_id = create_subscription()
    if not is_funded(subscription_id):
        fund_subscription(subscription_id)
    else:
        print("Already funded!")
