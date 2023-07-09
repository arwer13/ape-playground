# Setup
```
poetry install
poetry shell
ape plugins install .
```

# Usage
## Vote 2023_05_23
In `ape-config.yaml` set `ganache->...->block_number` to `17306000`
then
```shell
ape test tests/test_2023_05_23.py -s --network :mainnet-fork:ganache
```

## Vote V2 upgrade
In `ape-config.yaml` set `ganache->...->block_number` to `17240000`
then
```shell
ape test tests/test_upgrade_shapella.py -s --network :mainnet-fork:ganache
```
