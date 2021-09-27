# ansible-test
ansible.test.case is a testing framework and test runner within ansible tasks, it talks to API using openapispec, to Selenium using pageObjects and CLI using pexpect.

## Declarative test cases

```YAML
- name: Create Two Active Users
  ansible.test.case:
    using: myproject.user
    action: create
    with:
      - name: admin
        password: admin
        active: true
      - name: user
        password: user
        active: true
    register: users
    assert:
      - that: status == 200
```

```bash
ansible-playbook my-test-suite.yaml

```
