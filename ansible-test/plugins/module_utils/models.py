import enum
from typing import List, Optional, Union, Any, Dict
from dataclasses import dataclass

from ansible.module_utils.basic import AnsibleModule
from .validators import (
    DataclassValidationMixin,
    validate_conditionals,
    validate_export_dict,
    validate_boolean
)


ActionInputDict = Dict[str, Any]
ActionInputList = List[ActionInputDict]
ActionInputs = Union[ActionInputDict, ActionInputList]


class Status(str, enum.Enum):
    OK = "ok"
    FAIL = "fail"
    SKIP = "skip"

    def __str__(self) -> str:
        return self.value


class ActionList(list):
    ...


class ExpectList(list):
    ...


class SkipIfList(list):
    ...


class ExportDict(dict):
    ...


@dataclass
class Expect:
    condition: str


@dataclass
class SkipIf:
    condition: str


@dataclass
class Action(DataclassValidationMixin):
    module_name: str
    action_name: str
    title: Optional[str] = None
    skipif: Optional[SkipIfList] = None
    inputs: Optional[ActionInputs] = None
    export: Optional[ExportDict] = None
    expect: Optional[ExpectList] = None
    required: bool = True

    class Config:
        valid_ansible_arguments = [
            "title",
            "skipif",
            "inputs",
            "export",
            "expect",
            "required",
        ]

    def validate_title(self, value, **_) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(
                f"`{self.module_name}.{self.action_name}:`"
                f" title must be a string, got {type(value).__name__}={value}"
            )

    def validate_skipif(self, value, **_) -> Optional[SkipIfList]:
        if value is None:
            return None
        return validate_conditionals(value, "skipif", SkipIf, SkipIfList)

    def validate_expect(self, value, **_) -> Optional[ExpectList]:
        if value is None:
            return None
        return validate_conditionals(value, "expect", Expect, ExpectList)

    def validate_export(self, value, **_) -> Optional[ExportDict]:
        if value is None:
            return None
        return ExportDict(validate_export_dict(value))

    def validate_inputs(self, value, **_) -> Optional[ActionInputs]:
        if value is None:
            return None
        if not isinstance(value, (dict, list)):
            raise ValueError(
                f"`{self.module_name}.{self.action_name}:`"
                " inputs must be a dict or list[dict]"
                f" got: {type(value).__name__}={value}"
            )
        if isinstance(value, dict):
            for k in value:
                if k[0].isdigit():
                    raise ValueError(
                        f"`{self.module_name}.{self.action_name}:`"
                        f" inputs must not have numeric starting keys: got {k}"
                    )
        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    raise ValueError(
                        f"`{self.module_name}.{self.action_name}:`"
                        f" inputs {value}"
                        " should be a list or Dict[str, Any],"
                        f" got {type(item).__name__}={item}"
                    )
        return value

    def validate_required(self, value, **_) -> bool:
        return validate_boolean(value)


@dataclass(frozen=True)
class ActionResult:
    action: Action
    status: Status
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


@dataclass(frozen=True)
class TestCase:
    using: str
    actions: ActionList
    skipif: Optional[SkipIfList] = None
    expect: Optional[ExpectList] = None
    export: Optional[Dict[str, Any]] = None
    required: bool = True

    @classmethod
    def from_module(cls, module: AnsibleModule):
        """Return an instance of TestCase from an AnsibleModule."""
        data = {
            field: module.argument_spec[field]["type"].value
            for field in TestCase.__dataclass_fields__
        }
        return cls(**data)


@dataclass(frozen=True)
class TestCaseResult:
    test_case: TestCase
    action_results: List[ActionResult]
    status: Status
