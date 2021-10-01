from typing import Any, Union, List, Dict


class DataclassValidationMixin:
    def __post_init__(self):
        """Run validation methods if declared.

        The validation method can be a simple check
        that raises ValueError or a transformation to
        the field value.

        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`
        """
        for name, field in self.__dataclass_fields__.items():
            if method := getattr(self, f"validate_{name}", None):
                setattr(self, name, method(getattr(self, name), field=field))


def validate_conditionals(
    value: Union[List, str],
    field_name: str,
    conditional_type: Any,
    list_type: Any = list
):
    """
    1. Check if value is a list or str
        1.1 Each item in the list must be a str
    2. for each value create an conditional_type instance
    3. Add the conditional_type instance to the return value
    """
    ret = []

    if not isinstance(value, (list, str)):
        raise ValueError(
            f"`{field_name}` must be a list or str, got {type(value).__name__}"
        )

    if isinstance(value, str):
        value = [value]

    for item in value:
        if not isinstance(item, str):
            raise ValueError(
                f"`{field_name}` conditional must be str,"
                f" got {type(item).__name__}"
            )
        ret.append(conditional_type(condition=item))

    return list_type(ret)


def validate_export_dict(value, default_expression="result") -> Dict[str, str]:
    """
    Ensure export is a Dict[str, str]
    """
    if isinstance(value, str):
        value = {value: default_expression}

    if not isinstance(value, dict):
        raise ValueError(
            f"`export` must be a dictionary, got {type(value).__name__}"
        )

    for k, v in value.items():
        if not isinstance(k, str):
            raise ValueError(
                f"`export` keys must be strings, got {type(k).__name__}"
            )
        if not isinstance(v, str):
            raise ValueError(
                f"`export` values must be strings, got {type(v).__name__}"
            )
    return value


def validate_boolean(value) -> bool:
    """
    Ensure it is a boolean from values
    on, off, yes, no, true, false, 1, 0, True, False
    """
    truthy = [True, "on", "yes", "true", "1"]
    falsy = [False, "off", "no", "false", "0"]
    valid_options = truthy + falsy

    if isinstance(value, str):
        value = value.lower()

    if value not in valid_options:
        raise ValueError(
            f"`required:` cannot convert {value} to boolean"
            f" options are {valid_options}"
        )

    return value in truthy
