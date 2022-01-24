**WARNING** This is a Work in Progress

# ansible-test
ansible.test.case is a testing framework and test runner within ansible tasks, it **WILL** taslk to API using openapispec, to Selenium using pageObjects and CLI using pexpect.

## Declarative test cases

```YAML
# This is a standard ansible-playbook named test-case.yaml
---
- name: Test Case for Users
  ansible.test.case:
    using: namespace.project
    actions:
      - user.read:
          title: Start initial objects
          via: api
          inputs:
            name: admin
          export:
            admin_user: result.data
            user_exists: result.status_code != 404   
      - user.create:
          skipif: user_exists
          title: Ensure user can be created via API
          via: api
          inputs:
            name: admin
            password: "{{ generate_password('str', 8, 'strong') }}"
          expect:
            - result.status == ok
          export: admin_user
      - user.read:
          title: Ensure the created user can is available via api, cli and ui
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
Execute the test suite.

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

---

<details>
<summary>Click here to compare the same test scenario written in Python</summary>


> Considering the same level of abstractions.

```py
"""Test Case for Users"""
import pytest
from namespace.project import api
from namespace.project import cli
from namespace.project import ui
from namespace.project.generators import generate_password


def pytest_configure():
    """Start initial objects"""
    result = api.user.read(name="admin")
    pytest.my_global_context = {
      "user_exists": result.status_code != 404,
      "admin_user": result.data
    }


@pytest.mark.skipif(pytest.my_global_context["user_exists"])
def test_create_user_via_api():
    """Ensure user can be created via API"""
    response = api.user.create(
        name="admin", 
        password=generate_password('str', 8, 'strong')
    )
    assert response.status_code == 200
    pytest.my_global_context["admin_user"] = response.data
    
    
@pytest.mark.parameterize("via", [api, cli, ui])
def test_user_read(via):
    """Ensure the created user can is available via api, cli and ui"""
    admin_user = pytest.my_global_context["admin_user"]
    response = via.user.read(name=admin_user.name)
    assert response.status == "ok"
    assert response.data.name == admin_user.name
    if via == api:
        assert response.status_code == 200
    if via == cli:
        assert response.rc == 0
    if via == ui:
        assert response.ui.has_element("#username")
        assert response.ui.element_value("#username") == admin_user.name
```


[Python](https://gist.github.com/rochacbruno/47f7b50df3345e570986941516b9bc77)

</details>
