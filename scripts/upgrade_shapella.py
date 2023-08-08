"""
Voting 12/05/2023.

Lido V2 (Shapella-ready) protocol upgrade

1. Update `WithdrawalVault` proxy implementation
2. Call `ShapellaUpgradeTemplate.startUpgrade()`
3. Publish new `Lido` implementation in Lido app APM repo
4. Update `Lido` implementation
5. Publish new `NodeOperatorsRegistry` implementation in NodeOperatorsRegistry app APM repo
6. Update `NodeOperatorsRegistry` implementation
7. Publish new `LidoOracle` implementation in LidoOracle app APM repo
8. Update `LidoOracle` implementation to `LegacyOracle`
9. Create new role `STAKING_ROLE_ROLE` and assign to `StakingRouter`
10. Call `ShapellaUpgradeTemplate.finishUpgrade()`
11. Revoke `MANAGE_FEE` role from `Voting`
12. Revoke `MANAGE_WITHDRAWAL_KEY` role from `Voting`
13. Revoke `MANAGE_PROTOCOL_CONTRACTS_ROLE` role from `Voting`
14. Revoke `SET_EL_REWARDS_VAULT_ROLE` role from `Voting`
15. Revoke `SET_EL_REWARDS_WITHDRAWAL_LIMIT_ROLE` role from `Voting`
16. Revoke `DEPOSIT_ROLE` role from old `DepositSecurityModule`
17. Revoke `BURN_ROLE` role from `SelfOwnedStETHBurner`
18. Revoke `ADD_NODE_OPERATOR_ROLE` role from `Voting`
19. Revoke `SET_NODE_OPERATOR_ACTIVE_ROLE` role from `Voting`
20. Revoke `SET_NODE_OPERATOR_NAME_ROLE` role from `Voting`
21. Revoke `SET_NODE_OPERATOR_ADDRESS_ROLE` role from `Voting`
22. Revoke `REPORT_STOPPED_VALIDATORS_ROLE` role from `Voting`
23. Revoke `MANAGE_MEMBERS` role from `Voting`
24. Revoke `MANAGE_QUORUM` role from `Voting`
25. Revoke `SET_BEACON_SPEC` role from `Voting`
26. Revoke `SET_REPORT_BOUNDARIES` role from `Voting`
27. Revoke `SET_BEACON_REPORT_RECEIVER` role from `Voting`
28. Grant `MANAGE_TOKEN_URI_ROLE` role to `Voting`
29. Set `WithdrawalQueueERC721` baseUri to `https://wq-api.lido.fi/v1/nft`
30. Revoke `MANAGE_TOKEN_URI_ROLE` role from `Voting`
31. Fund Gas Funder multisig 0x5181d5D56Af4f823b96FE05f062D7a09761a5a53 for deposits with 50 stETH
"""

import time

from typing import Dict, Tuple, Optional

from ape import project
from utils.agent import agent_forward
from utils.finance import make_steth_payout

from utils.voting import bake_vote_items, confirm_vote_script, create_vote
from utils.repo import (
    add_implementation_to_lido_app_repo,
    add_implementation_to_nor_app_repo,
    add_implementation_to_oracle_app_repo,
)
from utils.kernel import update_app_implementation
from utils.config import (
    contracts,
    STAKING_ROUTER,
    WITHDRAWAL_VAULT,
    WITHDRAWAL_VAULT_IMPL,
    SELF_OWNED_STETH_BURNER,
)
from utils.permissions import (
    encode_oz_grant_role,
    encode_oz_revoke_role,
    encode_permission_create,
    encode_permission_revoke,
)

# Content URI: https://github.com/lidofinance/lido-dao/blob/b70881f026096790308d7ac9e277ad7f609c7117/apps/lido/README.md
update_lido_app = {
    "new_address": "0x17144556fd3424EDC8Fc8A4C940B2D04936d17eb",
    "content_uri": "0x697066733a516d525358415a724632785235726762556445724456364c47746a7151315434415a677336796f586f734d516333",
    "id": "0x3ca7c3e38968823ccb4c78ea688df41356f182ae1d159e4ee608d30d68cef320",
    "version": [4, 0, 0],  # must be list, not tuple
}

# Content URI: https://github.com/lidofinance/lido-dao/blob/b70881f026096790308d7ac9e277ad7f609c7117/apps/node-operators-registry/README.md
update_nor_app = {
    "new_address": "0x8538930c385C0438A357d2c25CB3eAD95Ab6D8ed",
    "content_uri": "0x697066733a516d54346a64693146684d454b5576575351316877786e33365748394b6a656743755a7441684a6b6368526b7a70",
    "id": "0x7071f283424072341f856ac9e947e7ec0eb68719f757a7e785979b6b8717579d",
    "version": [4, 0, 0],
}

# Content URI: https://github.com/lidofinance/lido-dao/blob/b70881f026096790308d7ac9e277ad7f609c7117/apps/lidooracle/README.md
update_oracle_app = {
    "new_address": "0xa29b819654cE6224A222bb5f586920105E2D7E0E",
    "content_uri": "0x697066733a516d575461635041557251614376414d5663716e5458766e7239544c666a57736861736334786a536865717a3269",
    "id": "0x8b47ba2a8454ec799cd91646e7ec47168e91fd139b23f017455f3e5898aaba93",
    "version": [4, 0, 0],
}

WITHDRAWAL_QUEUE_ERC721_BASE_URI = "https://wq-api.lido.fi/v1/nft"


def encode_template_start_upgrade(template_address: str) -> Tuple[str, str]:
    template = project.ShapellaUpgradeTemplate.at(template_address)
    return template.address, template.startUpgrade.encode_input()


def encode_template_finish_upgrade(template_address: str) -> Tuple[str, str]:
    template = project.ShapellaUpgradeTemplate.at(template_address)
    return template.address, template.finishUpgrade.encode_input()


def encode_withdrawal_vault_proxy_update(vault_proxy_address: str, implementation: str) -> Tuple[str, str]:
    proxy = project.WithdrawalVaultManager.at(vault_proxy_address)
    return proxy.address, proxy.proxy_upgradeTo.encode_input(implementation, b"")


def encode_withdrawal_queue_base_uri_update(withdrawal_queue_address: str, base_uri: str) -> Tuple[str, str]:
    withdrawal_queue = project.WithdrawalQueueERC721.at(withdrawal_queue_address)
    return withdrawal_queue.address, withdrawal_queue.setBaseURI.encode_input(base_uri)


def start_vote(tx_params: Dict[str, str], silent: bool):
    """Prepare and run voting."""
    voting = contracts.voting
    node_operators_registry = contracts.node_operators_registry
    lido = contracts.lido
    legacy_oracle = contracts.legacy_oracle
    withdrawal_queue = contracts.withdrawal_queue

    call_script_items = [
        # 1)
        encode_withdrawal_vault_proxy_update(WITHDRAWAL_VAULT, WITHDRAWAL_VAULT_IMPL),
        # 2)
        encode_template_start_upgrade(contracts.shapella_upgrade_template),
        # 3)
        add_implementation_to_lido_app_repo(
            update_lido_app["version"], update_lido_app["new_address"], update_lido_app["content_uri"]
        ),
        # 4)
        update_app_implementation(update_lido_app["id"], update_lido_app["new_address"]),
        # 5)
        add_implementation_to_nor_app_repo(
            update_nor_app["version"], update_nor_app["new_address"], update_nor_app["content_uri"]
        ),
        # 6)
        update_app_implementation(update_nor_app["id"], update_nor_app["new_address"]),
        # 7)
        add_implementation_to_oracle_app_repo(
            update_oracle_app["version"], update_oracle_app["new_address"], update_oracle_app["content_uri"]
        ),
        # 8)
        update_app_implementation(update_oracle_app["id"], update_oracle_app["new_address"]),
        # 9)
        encode_permission_create(STAKING_ROUTER, node_operators_registry, "STAKING_ROUTER_ROLE", manager=voting),
        # 10)
        encode_template_finish_upgrade(contracts.shapella_upgrade_template),
        # 11)
        encode_permission_revoke(lido, "MANAGE_FEE", revoke_from=voting),
        # 12)
        encode_permission_revoke(lido, "MANAGE_WITHDRAWAL_KEY", revoke_from=voting),
        # 13)
        encode_permission_revoke(lido, "MANAGE_PROTOCOL_CONTRACTS_ROLE", revoke_from=voting),
        # 14)
        encode_permission_revoke(lido, "SET_EL_REWARDS_VAULT_ROLE", revoke_from=voting),
        # 15)
        encode_permission_revoke(lido, "SET_EL_REWARDS_WITHDRAWAL_LIMIT_ROLE", revoke_from=voting),
        # 16)
        encode_permission_revoke(lido, "DEPOSIT_ROLE", revoke_from=contracts.deposit_security_module_v1),
        # 17)
        encode_permission_revoke(lido, "BURN_ROLE", revoke_from=SELF_OWNED_STETH_BURNER),
        # 18)
        encode_permission_revoke(node_operators_registry, "ADD_NODE_OPERATOR_ROLE", revoke_from=voting),
        # 19)
        encode_permission_revoke(node_operators_registry, "SET_NODE_OPERATOR_ACTIVE_ROLE", revoke_from=voting),
        # 20)
        encode_permission_revoke(node_operators_registry, "SET_NODE_OPERATOR_NAME_ROLE", revoke_from=voting),
        # 21)
        encode_permission_revoke(node_operators_registry, "SET_NODE_OPERATOR_ADDRESS_ROLE", revoke_from=voting),
        # 22)
        encode_permission_revoke(node_operators_registry, "REPORT_STOPPED_VALIDATORS_ROLE", revoke_from=voting),
        # 23)
        encode_permission_revoke(legacy_oracle, "MANAGE_MEMBERS", revoke_from=voting),
        # 24)
        encode_permission_revoke(legacy_oracle, "MANAGE_QUORUM", revoke_from=voting),
        # 25)
        encode_permission_revoke(legacy_oracle, "SET_BEACON_SPEC", revoke_from=voting),
        # 26)
        encode_permission_revoke(legacy_oracle, "SET_REPORT_BOUNDARIES", revoke_from=voting),
        # 27)
        encode_permission_revoke(legacy_oracle, "SET_BEACON_REPORT_RECEIVER", revoke_from=voting),
        # 28)
        agent_forward([encode_oz_grant_role(withdrawal_queue, "MANAGE_TOKEN_URI_ROLE", grant_to=voting)]),
        # 29)
        encode_withdrawal_queue_base_uri_update(withdrawal_queue, base_uri=WITHDRAWAL_QUEUE_ERC721_BASE_URI),
        # 30)
        agent_forward([encode_oz_revoke_role(withdrawal_queue, "MANAGE_TOKEN_URI_ROLE", revoke_from=voting)]),
        # 31)
        make_steth_payout(
            target_address="0x5181d5D56Af4f823b96FE05f062D7a09761a5a53",
            steth_in_wei=50 * (10**18),
            reference="Fund Gas Funder multisig"
        )
    ]

    vote_desc_items = [
        "1) Update `WithdrawalVault` proxy implementation",
        "2) Call `ShapellaUpgradeTemplate.startUpgrade()",
        "3) Publish new implementation in Lido app APM repo",
        "4) Updating implementation of Lido app",
        "5) Publishing new implementation in Node Operators Registry app APM repo",
        "6) Updating implementation of Node Operators Registry app",
        "7) Publishing new implementation in Oracle app APM repo",
        "8) Updating implementation of Oracle app",
        "9) Create permission for STAKING_ROUTER_ROLE of NodeOperatorsRegistry assigning it to StakingRouter",
        "10) Finish upgrade by calling `ShapellaUpgradeTemplate.finishUpgrade()`",
        "11) Revoke `MANAGE_FEE` role from `Voting`",
        "12) Revoke `MANAGE_WITHDRAWAL_KEY` role from `Voting`",
        "13) Revoke `MANAGE_PROTOCOL_CONTRACTS_ROLE` role from `Voting`",
        "14) Revoke `SET_EL_REWARDS_VAULT_ROLE` role from `Voting`",
        "15) Revoke `SET_EL_REWARDS_WITHDRAWAL_LIMIT_ROLE` role from `Voting`",
        "16) Revoke `DEPOSIT_ROLE` role from old `DepositSecurityModule`",
        "17) Revoke `BURN_ROLE` role from `SelfOwnedStETHBurner`",
        "18) Revoke `ADD_NODE_OPERATOR_ROLE` role from `Voting`",
        "19) Revoke `SET_NODE_OPERATOR_ACTIVE_ROLE` role from `Voting",
        "20) Revoke `SET_NODE_OPERATOR_NAME_ROLE` role from `Voting`",
        "21) Revoke `SET_NODE_OPERATOR_ADDRESS_ROLE` role from `Voting`",
        "22) Revoke `REPORT_STOPPED_VALIDATORS_ROLE` role from `Voting`",
        "23) Revoke `MANAGE_MEMBERS` role from `Voting`",
        "24) Revoke `MANAGE_QUORUM` role from `Voting`",
        "25) Revoke `SET_BEACON_SPEC` role from `Voting`",
        "26) Revoke `SET_REPORT_BOUNDARIES` role from `Voting`",
        "27) Revoke `SET_BEACON_REPORT_RECEIVER` role from `Voting`",
        "28) Grant `MANAGE_TOKEN_URI_ROLE` role to `Voting`",
        "29) Set `WithdrawalQueueERC721` baseUri to `https://wq-api.lido.fi/v1/nft`",
        "30) Revoke `MANAGE_TOKEN_URI_ROLE` role from `Voting`",
        "31) Fund Gas Funder multisig 0x5181d5D56Af4f823b96FE05f062D7a09761a5a53 for deposits with 50 stETH"
    ]

    vote_items = bake_vote_items(vote_desc_items, call_script_items)

    return confirm_vote_script(vote_items, silent) and list(create_vote(vote_items, tx_params))

