from .models import (
    Action,
    ActionList,
    ExpectList,
    Expect,
)


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
            raise ValueError(f"`using` must be a string, got {type(value)}")
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
            raise ValueError(f"`actions` must be a list, got {type(actions)}")

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

                try:
                    action = Action(
                        module_name=module_name,
                        action_name=action_name,
                        **action_value,
                    )
                except TypeError as e:
                    _valid = ", ".join(Action.Config.valid_ansible_arguments)
                    _invalid = set(action_value) - set(
                        Action.Config.valid_ansible_arguments
                    )

                    raise ValueError(
                        f"'Unsupported parameters for `actions`: {_invalid}"
                        f". Supported parameters include: {_valid}"
                    ) from e

            elif isinstance(action, str):
                module, action_name = action.split(".")
                action = Action(module_name=module, action_name=action_name)
            else:
                raise ValueError(
                    f"`actions` must be a list of dicts"
                    f" or strings, got {type(action)}"
                )
            value.append(action)

        self.value = self.type(value)
        return actions


class SkipifArgType(ArgType):
    type = str

    def __call__(self, value) -> str:
        if not isinstance(value, str):
            raise ValueError(f"`skipif` must be a string, got {type(value)}")
        self.value = self.type(value)
        return value


class ExpectArgType(ArgType):
    type = ExpectList

    def __call__(self, expect) -> list:
        """
        1. Check if value is a list or str
            1.1 Each item in the list must be a str
        2. for each value create an Expect instance
        3. Add the Expect instance to the return value
        """
        value = []

        if not isinstance(expect, (list, str)):
            raise ValueError(
                f"`expect` must be a list or str, got {type(value)}"
            )

        if isinstance(expect, str):
            expect = [expect]

        for item in expect:
            if not isinstance(item, str):
                raise ValueError(f"each `expect` must a str, got {type(item)}")
            value.append(Expect(condition=item))

        self.value = self.type(value)
        return expect


class ExportArgType(ArgType):
    type = dict

    def __call__(self, value) -> dict:
        """
        1. Ensure value is a dictionary
        2. ensure every value in the dictionary is a str
        """
        if not isinstance(value, dict):
            raise ValueError(
                f"`export` must be a dictionary, got {type(value)}"
            )
        for k, v in value.items():
            if not isinstance(k, str):
                raise ValueError(
                    f"`export` keys must be strings, got {type(k)}"
                )
            if not isinstance(v, str):
                raise ValueError(
                    f"`export` values must be strings, got {type(v)}"
                )
        self.value = self.type(value)
        return value


class RequiredArgType(ArgType):
    type = bool

    def __call__(self, value) -> bool:
        """
        Ensure it is a boolean from values
        on, off, yes, no, true, false, 1, 0, True, False
        """
        truthy = [True, "on", "yes", "true", "1"]
        falsy = [False, "off", "no", "false", "0"]
        if isinstance(value, str):
            value = value.lower()
        if value not in falsy + truthy:
            raise ValueError(f"`required` must be a boolean, got {value}")
        value = True if value in truthy else False
        self.value = self.type(value)
        return value
