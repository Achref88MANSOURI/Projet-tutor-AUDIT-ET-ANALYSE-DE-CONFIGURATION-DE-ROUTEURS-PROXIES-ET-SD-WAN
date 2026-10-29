"""Validation of the single business contract for Python consumers."""
from jsonschema import Draft202012Validator, FormatChecker
from schemas.router_contract_v1 import RouterContractV1, router_contract_v1_schema


def boolean(value):
    """Accept a captured boolean, never infer one from a nonempty string."""
    if type(value) is not bool:
        raise ValueError('Configured flag must be a boolean')
    return value


def validate(document):
    model = RouterContractV1.model_validate(document)
    Draft202012Validator(router_contract_v1_schema(), format_checker=FormatChecker()).validate(
        model.model_dump(mode='json'))
    return model
