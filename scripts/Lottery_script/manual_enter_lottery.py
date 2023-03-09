#!/usr/bin/python3
from brownie import Lottery, network, accounts
from scripts.helpful_scripts import fund_with_link, get_account, get_contract, LOCAL_BLOCKCHAIN_ENVIRONMENTS, BLOCK_CONFIRMATIONS_FOR_VERIFICATION


def local_enter():
    idx = input("Type the index of account you want to enter: ").strip()
    try:
        account = get_account(index=int(idx))
    except Exception as E:
        print(str(E))
        exit(1)
    return account


def normal_enter():
    priv_key = input(
        "Type the private key of account you want to enter: ").strip()
    try:
        account = accounts.add(priv_key)
    except Exception as E:
        print(str(E))
        exit(1)
    return account


def main():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = local_enter()
    else:
        account = normal_enter()
    try:
        lottery = Lottery[-1]
        value = lottery.getEntranceFee()
        if account.balance() < value:
            raise Exception("You don't have enoungh fee to enter the Lottery!")
        tx = lottery.enter({"from": account, "value": value + 10000000})
        tx.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION())
        print("You entered the lottery!")
    except IndexError:
        print("We couldn't find that contract. You may need to deploy it first!")
    except Exception as E:
        print(str(E))
