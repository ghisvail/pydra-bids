POETRY ?= poetry
PACKAGES = pydra

all: install test

.PHONY: install
install:
	@$(POETRY) install

.PHONY: install-docs
install-docs:
	@$(POETRY) install --only docs

.PHONY: format
format: format-black format-isort

.PHONY: format-black
format-black:
	$(info Formatting code with black)
	@$(POETRY) run black --quiet $(PACKAGES)

.PHONY: format-isort
format-isort:
	$(info Formatting code with isort)
	@$(POETRY) run isort --quiet $(PACKAGES)

.PHONY: lint
lint: lint-black lint-isort

.PHONY: lint-black
lint-black:
	$(info Linting code with black)
	@$(POETRY) run black --check --diff $(PACKAGES)

.PHONY: lint-isort
lint-isort:
	$(info Linting code with isort)
	@$(POETRY) run isort --check --diff $(PACKAGES)

.PHONY: clean-docs
clean-docs:
	@$(POETRY) run make -C docs clean

.PHONY: docs
docs: clean-docs
	@$(POETRY) run make -C docs html

.PHONY: test
test:
	@$(POETRY) run python -m pytest

.PHONY: update
update:
	@$(POETRY) update
