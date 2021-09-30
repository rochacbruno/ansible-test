from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.test.plugins.module_utils.arg_types import (
    UsingArgType,
    ActionsArgType,
    SkipifArgType,
    ExpectArgType,
    ExportArgType,
    RequiredArgType,
)
from ansible_collections.ansible.test.plugins.module_utils.models import (
    TestCase,
)


def run_module():

    module_args = {
        "using": {"type": UsingArgType(), "required": True},
        "actions": {"type": ActionsArgType(), "required": True},
        "skipif": {
            "type": SkipifArgType(),
            "required": False,
            "default": None,
        },
        "expect": {
            "type": ExpectArgType(),
            "required": False,
            "default": None,
        },
        "export": {
            "type": ExportArgType(),
            "required": False,
            "default": None,
        },
        "required": {
            "type": RequiredArgType(),
            "required": False,
            "default": True,
        },
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # __import__("sdb").set_trace()

    test_case: TestCase = TestCase.from_module(module)

    result = {"changed": False, "test_case": str(test_case)}

    if module.check_mode:
        module.exit_json(**result)

    result["changed"] = True
    result["status"] = "ok"  # enum?

    # action_result = [{"name": "admin"}]
    # result["ansible_facts"] = {}
    # if (fact := module.params["outputs"]):
    #     result["ansible_facts"][fact] = action_result

    # result['original_message'] = module.params['name']
    # result['message'] = 'goodbye'

    # if module.params['new']:
    #     result['changed'] = True

    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
