import os
import sys
root_dir = os.path.dirname(os.path.basename(os.path.realpath(__file__)))
sys.path.append(root_dir)

from ape import project, chain

from utils.config import (
    network_name,
    contracts,
    LDO_HOLDER_ADDRESS_FOR_TESTS,
)

from utils.test.event_validators.node_operators_registry import (
    validate_target_validators_count_changed_event,
    TargetValidatorsCountChanged,
)
from utils.test.event_validators.payout import Payout, validate_token_payout_event
from utils.test.event_validators.easy_track import (
    validate_motions_count_limit_changed_event,
)
from utils.test.event_validators.permission import validate_grant_role_event, validate_revoke_role_event
from utils.test.helpers import almostEqWithDiff

from scripts.vote_2023_05_23 import start_vote

AGENT = "0x3e40D73EB977Dc6a537aF587D48316feE66E9C8c"

#####
# CONSTANTS
#####

STETH_ERROR_MARGIN = 2


def test_main(helpers, accounts):
    vote_ids_from_env = []

    ## parameters
    agent = contracts.agent
    node_operators_registry = contracts.node_operators_registry
    staking_router = contracts.staking_router
    easy_track = contracts.easy_track
    rewards_multisig_address = "0x87D93d9B2C672bf9c9642d853a8682546a5012B5"
    target_NO_id = 12

    # web3.keccak(text="STAKING_MODULE_MANAGE_ROLE")
    STAKING_MODULE_MANAGE_ROLE = "0x3105bcbf19d4417b73ae0e58d508a65ecf75665e46c2622d8521732de6080c48"
    stETH_token = project.ERC20.at("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")

    current_block = chain.blocks[-1]
    print(f"block {current_block}")

    # return
    # 1-3
    assert staking_router.hasRole(STAKING_MODULE_MANAGE_ROLE, agent.address) == False

    NO_summary_before = node_operators_registry.getNodeOperatorSummary(target_NO_id)
    assert NO_summary_before[0] == False
    assert NO_summary_before[1] == 0
    assert NO_summary_before[2] == 0
    assert NO_summary_before[3] == 0
    assert NO_summary_before[4] == 0
    assert NO_summary_before[5] == 0
    assert NO_summary_before[6] == 2300
    assert NO_summary_before[7] == 0

    # 4
    agent_balance_before = stETH_token.balanceOf(agent.address)
    rewards_balance_before = stETH_token.balanceOf(rewards_multisig_address)
    rewards_payout = Payout(
        token_addr=stETH_token.address,
        from_addr=agent.address,
        to_addr=rewards_multisig_address,
        amount=170 * (10 ** 18)
    )

    # 5
    motionsCountLimit_before = 12
    motionsCountLimit_expected = 20
    easy_track.motionsCountLimit() == motionsCountLimit_before, "Incorrect motions count limit before"

    # START VOTE
    if len(vote_ids_from_env) > 0:
        (vote_id,) = vote_ids_from_env
    else:
        tx_params = {"from": LDO_HOLDER_ADDRESS_FOR_TESTS}
        vote_id, _ = start_vote(tx_params, silent=True)

    vote_tx = helpers.execute_vote(accounts, vote_id, contracts.voting, topup=int(10*1e18))

    print(f"voteId = {vote_id}, gasUsed = {vote_tx.gas_used}")

    vote_tx.show_trace()
