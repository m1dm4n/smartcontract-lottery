#!/usr/bin/python3
from brownie import Lottery
from scripts.helpful_scripts import get_account, BLOCK_CONFIRMATIONS_FOR_VERIFICATION


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    try:
        starting_tx = lottery.startLottery({"from": account})
        starting_tx.wait(BLOCK_CONFIRMATIONS_FOR_VERIFICATION())
        print("The lottery is started!")
    except Exception as E:
        print("An error had occurred: " + str(E))

def main():
    start_lottery()
