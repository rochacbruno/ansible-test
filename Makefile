build:
	@echo "Building..."
	@ansible-galaxy collection build ansible-test --force

install:
	@echo "Installing..."
	@ansible-galaxy collection install ansible-test-0.1.0.tar.gz --force

run:
	@echo "Running..."
	@ansible-playbook --connection=local test-playbook.yaml

adhoc:
	@echo "Running adhoc..."
	2ansible localhost, -m ansible.test.case -a "bar=baz"
