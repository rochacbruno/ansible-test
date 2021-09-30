import enum
from typing import List, Optional, Union, Any, Dict
from dataclasses import dataclass

from ansible.module_utils.basic import AnsibleModule
from .validators import DataclassValidationMixin

ActionInputDict = Dict[str, Any]
ActionInputList = List[ActionInputDict]
ActionInputs = Union[ActionInputDict, ActionInputList]

ActionOutputDict = Dict[str, Any]
ActionOutputStr = str
ActionOutputs = Union[ActionOutputStr, ActionOutputDict]


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


@dataclass
class Expect:
    condition: str


@dataclass
class Action(DataclassValidationMixin):
    module_name: str
    action_name: str
    title: Optional[str] = None
    skipif: Optional[str] = None
    inputs: Optional[ActionInputs] = None
    outputs: Optional[ActionOutputs] = None
    expect: Optional[ExpectList] = None
    required: bool = True

    class Config:
        valid_ansible_arguments = [
            "title",
            "skipif",
            "inputs",
            "outputs",
            "expect",
            "required",
        ]

    def validate_inputs(self, value, **_) -> Optional[ActionInputs]:
        if not value:
            return None
        if isinstance(value, dict):
            return value
        elif isinstance(value, list):
            return value
        raise ValueError(
            f"`action` inputs must be a list or dict got: {type(value)}"
        )


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
    skipif: Optional[str] = None
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
