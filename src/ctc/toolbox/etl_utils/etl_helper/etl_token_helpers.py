import pandas as pd

from ctc import directory


def get_token_holdings(token_transfers):
    """convert token_transfers dataframe to token_holdings dataframe

    token_transfers should contain only a single token

    ? TODO
    - volume metrics
        - transfers in
        - transfers out
    - count metrics
        - number of in transfers
        - number of out transfers
        - number of unique transactions
    """

    transfer_from = (
        token_transfers[['from_address', 'value']]
        .set_index('from_address')
        .sum(level='from_address')
    )
    transfer_to = (
        token_transfers[['to_address', 'value']]
        .set_index('to_address')
        .sum(level='to_address')
    )
    token_holdings = transfer_to.sub(transfer_from, fill_value=0)
    token_holdings = token_holdings.rename(columns={'value': 'holdings'})

    return token_holdings


def get_tokens_holdings(tokens_transfers, token_symbols=None):
    """return dataframe of token holdings for each wallet address

    - rows are wallet addresses, columns are token holdings
    """

    token_addresses = set(tokens_transfers['token_address'])

    if token_symbols is None:
        token_symbols = {
            token_address: directory.address_to_symbol[token_address]
            for token_address in token_addresses
        }
    if not set(token_addresses).issubset(token_symbols.keys()):
        raise Exception('not all token names specified')

    tokens_holdings = []
    for token_address in token_addresses:
        symbol = token_symbols[token_address]
        mask = tokens_transfers['token_address'] == token_address
        token_holdings = get_token_holdings(tokens_transfers[mask])
        token_holdings = token_holdings.add_prefix(symbol + '_')
        tokens_holdings.append(token_holdings)

    tokens_holdings = pd.concat(tokens_holdings, axis='columns')
    tokens_holdings = tokens_holdings.fillna(0)

    return tokens_holdings

