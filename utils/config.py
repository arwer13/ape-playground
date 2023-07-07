import os
import sys
from typing import Any, Union, Optional, Dict

from ape import project


MAINNET_VOTE_DURATION = 3 * 24 * 60 * 60
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def color(x):
    return ""


def network_name():
    return "mainnet"

# def network_name() -> Optional[str]:
    # if network.show_active() is not None:
    #     return network.show_active()
    # cli_args = sys.argv[1:]
    # net_ind = next((cli_args.index(arg) for arg in cli_args if arg == "--network"), len(cli_args))

    # net_name = None
    # if net_ind != len(cli_args):
    #     net_name = cli_args[net_ind + 1]

    # return net_name


if network_name() in ("goerli", "goerli-fork"):
    print(f'Using {color("cyan")}config_goerli.py{color} addresses')
    from configs.config_goerli import *
else:
    print(f'Using {color("magenta")}config_mainnet.py{color} addresses')
    from configs.config_mainnet import *


def get_is_live() -> bool:
    return False
    # dev_networks = ["development", "hardhat", "hardhat-fork", "goerli-fork", "local-fork", "mainnet-fork"]
    # return network.show_active() not in dev_networks


def get_priority_fee() -> str:
    if "OMNIBUS_PRIORITY_FEE" in os.environ:
        return os.environ["OMNIBUS_PRIORITY_FEE"]
    else:
        return "2 gwei"


def get_max_fee() -> str:
    if "OMNIBUS_MAX_FEE" in os.environ:
        return os.environ["OMNIBUS_MAX_FEE"]
    else:
        return "300 gwei"


# def get_deployer_account() -> Union[LocalAccount, Account]:
#     is_live = get_is_live()
#     if is_live and "DEPLOYER" not in os.environ:
#         raise EnvironmentError("Please set DEPLOYER env variable to the deployer account name")

#     return accounts.load(os.environ["DEPLOYER"]) if (is_live or "DEPLOYER" in os.environ) else accounts[4]


def prompt_bool() -> Optional[bool]:
    choice = input().lower()
    if choice in {"yes", "y"}:
        return True
    elif choice in {"no", "n"}:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def get_config_params() -> Dict[str, str]:
    if network_name() in ("goerli", "goerli-fork"):
        import configs.config_goerli

        ret = {x: globals()[x] for x in dir(configs.config_goerli) if not x.startswith("__")}
    else:
        import configs.config_mainnet

        ret = {x: globals()[x] for x in dir(configs.config_mainnet) if not x.startswith("__")}
    return ret


class ContractsLazyLoader:
    @property
    def lido_v1(self):
        return project.LidoV1.at(LIDO)

    @property
    def lido(self):
        return project.Lido.at(LIDO)

    @property
    def ldo_token(self):
        return project.MiniMeToken.at(LDO_TOKEN)

    @property
    def voting(self):
        return project.Voting.at(VOTING)

    @property
    def token_manager(self):
        return project.TokenManager.at(TOKEN_MANAGER)

    @property
    def finance(self):
        return project.Finance.at(FINANCE)

    @property
    def acl(self):
        return project.ACL.at(ACL)

    @property
    def agent(self):
        return project.Agent.at(AGENT)

    @property
    def node_operators_registry(self):
        return project.NodeOperatorsRegistry.at(NODE_OPERATORS_REGISTRY)

    @property
    def legacy_oracle(self):
        return project.LegacyOracle.at(LEGACY_ORACLE)

    @property
    def deposit_security_module_v1(self):
        return project.DepositSecurityModuleV1.at(DEPOSIT_SECURITY_MODULE_V1)

    @property
    def deposit_security_module(self):
        return project.DepositSecurityModule.at(DEPOSIT_SECURITY_MODULE)

    @property
    def burner(self):
        return project.Burner.at(BURNER)

    @property
    def execution_layer_rewards_vault(self):
        return project.LidoExecutionLayerRewardsVault.at(EXECUTION_LAYER_REWARDS_VAULT)

    @property
    def hash_consensus_for_accounting_oracle(self):
        return project.HashConsensus.at(HASH_CONSENSUS_FOR_AO)

    @property
    def accounting_oracle(self):
        return project.AccountingOracle.at(ACCOUNTING_ORACLE)

    @property
    def hash_consensus_for_validators_exit_bus_oracle(self):
        return project.HashConsensus.at(HASH_CONSENSUS_FOR_VEBO)

    @property
    def validators_exit_bus_oracle(self):
        return project.ValidatorsExitBusOracle.at(VALIDATORS_EXIT_BUS_ORACLE)

    @property
    def oracle_report_sanity_checker(self):
        return project.OracleReportSanityChecker.at(ORACLE_REPORT_SANITY_CHECKER)

    @property
    def withdrawal_queue(self):
        return project.WithdrawalQueueERC721.at(WITHDRAWAL_QUEUE)

    @property
    def lido_locator(self):
        return project.LidoLocator.at(LIDO_LOCATOR)

    @property
    def eip712_steth(self):
        return project.EIP712StETH.at(EIP712_STETH)

    @property
    def withdrawal_vault(self):
        return project.WithdrawalVault.at(WITHDRAWAL_VAULT)

    @property
    def staking_router(self):
        return project.StakingRouter.at(STAKING_ROUTER)

    @property
    def kernel(self):
        return project.Kernel.at(ARAGON_KERNEL)

    @property
    def lido_app_repo(self):
        return project.Repo.at(LIDO_REPO)

    @property
    def nor_app_repo(self):
        return project.Repo.at(NODE_OPERATORS_REGISTRY_REPO)

    @property
    def voting_app_repo(self):
        return project.Repo.at(VOTING_REPO)

    @property
    def oracle_app_repo(self):
        return project.Repo.at(LEGACY_ORACLE_REPO)

    @property
    def easy_track(self):
        return project.EasyTrack.at(EASYTRACK)

    @property
    def relay_allowed_list(self):
        return project.MEVBoostRelayAllowedList.at(RELAY_ALLOWED_LIST)

    @property
    def weth_token(self):
        return project.WethToken.at(WETH_TOKEN)

    @property
    def oracle_daemon_config(self):
        return project.OracleDaemonConfig.at(ORACLE_DAEMON_CONFIG)

    @property
    def wsteth(self):
        return project.WstETH.at(WSTETH_TOKEN)

    @property
    def gate_seal(self):
        return project.GateSeal.at(GATE_SEAL)

    @property
    def evm_script_registry(self):
        return project.EVMScriptRegistry.at(ARAGON_EVMSCRIPT_REGISTRY)

    @property
    def insurance_fund(self):
        return project.InsuranceFund.at(INSURANCE_FUND)


def __getattr__(name: str) -> Any:
    if name == "contracts":
        return ContractsLazyLoader()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
