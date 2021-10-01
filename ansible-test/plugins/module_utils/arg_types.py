from .models import (
    ActionList,
    Action,
    ExpectList,
    Expect,
    ExportDict,
    SkipIfList,
    SkipIf,
)
from .validators import validate_boolean, validate_conditionals,validate_export_dict


class ArgType:
    type = lambda value: value  # noqa
    value = None


class UsingArgType(ArgType):
    type = str

    def __call__(self, value) -> str:
        """
        1. Check if value is a string
        2. Check if value is a namespace.collection
        3. Check if namespace.collection is installed
        """
        if not isinstance(value, str):
            raise ValueError(
                f"`using` must be a string, got {type(value).__name__}"
            )
        if len(value.split(".")) != 2:
            raise ValueError(
                f"`using` must be a <namespace>.<collection>, got {value}"
            )
        # TODO: Check if collection is installed
        self.value = self.type(value)
        return value


class ActionsArgType(ArgType):
    type = ActionList

    def __call__(self, actions) -> list:
        """
        1. Check if actions is a list
        2. For each action in actions
            2.1 Check if action is a dict or a str
            2.2 Create the action instance
            2.3 Add Action to return value
        """
        value = []

        if not isinstance(actions, list):
            msg = f"`actions` must be a list, got {type(actions).__name__}"
            if isinstance(actions, dict):
                msg += (
                    f" did you mean `- {list(actions.keys())[0]}:` ?"
                )
            if isinstance(actions, str):
                msg += f" did you mean `[{actions}]` or `- {actions}` ?"
            raise ValueError(msg)

        _valid = ", ".join(Action.Config.valid_ansible_arguments)
        for action in actions:
            if isinstance(action, dict):
                # ensure this is a single key-value pair
                if len(action) != 1:
                    raise ValueError(
                        f"`action` must be single key dictionary,"
                        f" got {action.keys()}"
                    )

                action_key = list(action.keys())[0]
                if "." not in action_key:
                    raise ValueError(
                        f"`action` must be <module>.<action>, got {action_key}"
                    )
                module_name, action_name = action_key.split(".")
                action_value = action[action_key]
                if not isinstance(action_value, dict):
                    raise ValueError(
                        f"`{action_key}:` takes"
                        " {param: value, ...},"
                        f" where `param` is one of {_valid}"
                        f", but got {action_value}"
                    )

                try:
                    action = Action(
                        module_name=module_name,
                        action_name=action_name,
                        **action_value,
                    )
                except TypeError as e:
                    _invalid = set(action_value) - set(
                        Action.Config.valid_ansible_arguments
                    )

                    raise ValueError(
                        f"Unsupported parameters"
                        f" for `{action_key}: {_invalid}`"
                        f". Supported parameters include: {_valid}"
                    ) from e

            elif isinstance(action, str):
                if "." not in action:
                    raise ValueError(
                        f"`action` must be <module>.<action>, got {action}"
                    )
                module, action_name = action.split(".")
                action = Action(module_name=module, action_name=action_name)
            else:
                raise ValueError(
                    f"`actions` must be a list of dicts"
                    f" or strings, got {type(action).__name__}"
                )
            value.append(action)

        self.value = self.type(value)
        return actions


class SkipifArgType(ArgType):
    type = SkipIfList

    def __call__(self, value) -> str:
        self.value = validate_conditionals(value, "skipif", SkipIf, self.type)
        return value


class ExpectArgType(ArgType):
    type = ExpectList

    def __call__(self, value) -> list:
        self.value = validate_conditionals(value, "expect", Expect, self.type)
        return value


class ExportArgType(ArgType):
    type = ExportDict

    def __call__(self, value) -> dict:
        self.value = self.type(validate_export_dict(value))
        return value


class RequiredArgType(ArgType):

    def __call__(self, value) -> bool:
        self.value = validate_boolean(value)
        return value
