# ansible-test
ansible.test.case is a testing framework and test runner within ansible tasks, it talks to API using openapispec, to Selenium using pageObjects and CLI using pexpect.

## Declarative test cases

```YAML
# This is a standard ansible-playbook named test-case.yaml
---
- name: Test Create User
  ansible.test.case:
    using: namespace.project
    actions:

      - user.read:
          via: api
          inputs:
            name: admin
          export:
            admin_user: result.data
            user_exists: result.status_code != 404
        
      - user.create:
          skipif: user_exists
          via: api
          inputs:
            name: admin
            password: "{{ generate_password('str', 8, 'strong') }}"
          expect:
            - result.status == ok
          export: admin_user
    
      - user.read:
          via: [api, cli, ui]
          inputs:
            name: admin_user.name
          expect:
            - result.status == ok
            - result.data.name == admin_user.name
            - result.api.status_code == 200
            - result.cli.rc == 0
            - result.ui.has_element('#username')
            - result.ui.element_value('#username') == admin_user.name
```

```bash
$ ansible-playbook --connection=local test-case.yaml
# or
$ ansible-playbook -i my.ci.host, test-case.yaml
```

Outputs:

```plain
PLAY [Functional tests for project] *********************

TASK [Gathering Facts] **********************************
ok: [localhost]

TASK [Test Create User] *********************************
ok: [localhost] => 
    user.read: status=ok, api.status_code=404 [PASSED]
    user.create: status=ok, api.status_code=200 [PASSED]
    user.read: status=ok, api.status_code=200, cli.rc=0, ui.state=loaded [PASSED]

TASK [Junit Report] *************************************
ok: [localhost] => (file=junit/test-case-result.xml)

TASK [Uploading junit report] ***************************
ok: [localhost] => (to=metrics.host, status=ok)

TASK [Saving Selenium Screenshots] ***********************
ok: [localhost] => (to=/screenshots/build-1234, status=ok)

```

Use https://docs.ansible.com/ansible/latest/collections/ansible/builtin/junit_callback.html in the ansible.cfg to get a results-junit.xml file
