# ansible-test
ansible.test.case is a testing framework and test runner within ansible tasks, it talks to API using openapispec, to Selenium using pageObjects and CLI using pexpect.

## Declarative test cases

```YAML
# This is a standard ansible-playbook-task.yaml 
---
- name: Create Two Active Users          # The name of the test case        
  ansible.test.case:                     # Declare the test.case module
    using: namespace.project.user        # Project specific actions module
    action: create                       # The action to perform
    inputs:                              # The inputs to the action
      - name: admin
        password: admin
        active: true
      - name: user
        password: user
        active: true
    register: users                      # The result of the action is registered as users
    assert:                              # The assertions to perform
      - that: status == ok               # Assert that the status code is success, possible statuses are ok, error, skipped
```

```bash
ansible-playbook my-test-suite.yaml

```

Use https://docs.ansible.com/ansible/latest/collections/ansible/builtin/junit_callback.html in the ansible.cfg to get a results-junit.xml file
