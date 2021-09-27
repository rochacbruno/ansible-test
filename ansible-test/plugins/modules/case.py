from ansible.module_utils.basic import AnsibleModule
from ansible_act import ModuleFactory


if __name__ == '__main__':
    module = AnsibleModule(argument_spec={})
    module_factory = ModuleFactory(module)
    module_factory.run()
    module.exit_json()
