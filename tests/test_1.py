import os
import sys
root_dir = os.path.dirname(os.path.basename(os.path.realpath(__file__)))
sys.path.append(root_dir)


from ape import project

from utils.config import (
    network_name,
    contracts,
)

AGENT = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"


def test_main():
    ## parameters
    agent = contracts.agent
    node_operators_registry = contracts.node_operators_registry
    staking_router = contracts.staking_router
    easy_track = contracts.easy_track
    rewards_multisig_address = "0x87D93d9B2C672bf9c9642d853a8682546a5012B5"
    target_NO_id = 12
