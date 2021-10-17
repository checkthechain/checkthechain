from ctc import evm


sushi_pools = {
    'DAI_ETH': '0xc3d03e4f041fd4cd388c549ee2a29a9e5075882f',
    'WBTC_ETH': '0xceff51756c56ceffca006cd410b03ffc46dd3a58',
    'SUSHI_ETH': '0x795065dcc9f64b5614c407a6efdc400da6221fb0',
    'USDC_ETH': '0x397ff1542f962076d0bfe58ea045ffa2d347aca0',
    'USDT_ETH': '0x06da0fd433c1a5d7a4faa01111c044910a184553',
    'ETH_ALCX': '0xc3f279090a47e80990fe3a9c30d24cb117ef91a8',
    'YFI_ETH': '0x088ee5007c98a9677165d78dd2109ae4a3d04d0c',
    'AAVE_ETH': '0xd75ea151a61d06868e31f8988d28dfe5e9df57b4',
    'ILV_ETH': '0x6a091a3406e0073c3cd6340122143009adac0eda',
    'LINK_ETH': '0xc40d16476380e4037e6b1a2594caf6a6cc8da967',
}

sushi_bentobox_v1_address = '0xf5bce5077908a1b7370b9ae04adc565ebd643966'

sushi_address_to_names = evm.create_reverse_address_map(sushi_pools)

