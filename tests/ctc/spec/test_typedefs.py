from ctc.spec import typedata
from ctc.spec.typedefs import config_types
from ctc.spec.typedefs import transaction_types


def test_config_specs_match():
    assert set(config_types.Config.__annotations__.keys()) == set(
        config_types.PartialConfig.__annotations__.keys()
    )
    assert set(config_types.Config.__annotations__.keys()) == set(
        config_types.JsonConfig.__annotations__.keys()
    )

    for key, value in config_types.Config.__annotations__.items():
        assert value == config_types.PartialConfig.__annotations__[key]
        if key not in typedata.config_int_subkeys:
            assert value == config_types.JsonConfig.__annotations__[key]


def test_transaction_spec_match():
    assert set(transaction_types.DBTransaction.__annotations__.keys()) == set(
        transaction_types.DBTransactionText.__annotations__.keys()
    )

