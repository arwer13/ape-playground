from utils.config import contracts
from utils.config import AGENT
from utils.evm_script import (
    encode_call_script,
)
from typing import (
    Tuple,
    Sequence,
)
from hexbytes import HexBytes


def agent_forward(call_script: Sequence[Tuple[str, str]]) -> Tuple[str, str]:
    agent = contracts.agent
    evm_script = encode_call_script(call_script)
    return (AGENT, agent.forward.encode_input(HexBytes(evm_script)))
