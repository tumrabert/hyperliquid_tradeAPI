import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from .config import load_config
def setup(base_url=None, skip_ws=False):
    config = load_config()
    account: LocalAccount = eth_account.Account.from_key(config["secret_key"])
    address = config["account_address"] or account.address
    print("Running with account address:", address)

    if address != account.address:
        print("Running with agent address:", account.address)

    info = Info(base_url, skip_ws)
    user_state = info.user_state(address)
    spot_user_state = info.spot_user_state(address)
    margin_summary = user_state["marginSummary"]

    if float(margin_summary["accountValue"]) == 0 and len(spot_user_state["balances"]) == 0:
        url = info.base_url.split(".", 1)[1]
        raise Exception(f"No accountValue:\nEnsure {address} has a balance on {url}.")

    exchange = Exchange(account, base_url, account_address=address)
    return address, info, exchange

def setup_multi_sig_wallets():
    config = load_config()
    authorized_user_wallets = []

    for wallet_config in config["multi_sig"]["authorized_users"]:
        account: LocalAccount = eth_account.Account.from_key(wallet_config["secret_key"])
        address = wallet_config["account_address"]
        if account.address != address:
            raise Exception(f"Provided authorized user address {address} does not match private key")
        print("Loaded authorized user for multi-sig", address)
        authorized_user_wallets.append(account)

    return authorized_user_wallets
