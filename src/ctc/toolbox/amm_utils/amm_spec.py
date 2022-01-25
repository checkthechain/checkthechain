
contenttypes = {
    'AMMPool': {
        'x_reserves': 'Number',
        'y_reserves': 'Number',
        'lp_total_supply': 'Number',
    },
    'AMMTrade': {
        'x_bought': 'Number',
        'x_sold': 'Number',
        'y_bought': 'Number',
        'y_sold': 'Number',
        'fee_rate': 'Number',
        'new_pool': 'AMMPool',
    },
    'AMMMint': {
        'x_deposited': 'Number',
        'y_deposited': 'Number',
        'lp_minted': 'Number',
        'new_pool': 'AMMPool',
    },
    'AMMBurn': {
        'x_withdrawn': 'Number',
        'y_withdrawn': 'Number',
        'lp_burned': 'Number',
        'new_pool': 'AMMPool',
    },
    'AMMPoolSummary': {
        'x_per_y': 'Number',
        'y_per_x': 'Number',
        'x_per_y_depth': {'Number': 'Number'},
        'y_per_x_depth': {'Number': 'Number'},
    },
    'AMMTradeSummary': {
        'slippage': 'Number',
        'mean_x_per_y': 'Number',
        'mean_y_per_x': 'Number',
        'x_fees': 'Number',
        'y_fees': 'Number',
    },
}

