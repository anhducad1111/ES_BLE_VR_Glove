.PHONY: setup clean build test format lint release all

PYTHON := python
VENV := ES_BLE_UI_venv
BIN := $(VENV)\Scripts
SRC := src
TESTS := tests

all: setup lint test

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(BIN)\python -m pip install --upgrade pip
	$(BIN)\pip install -r requirements.txt
	$(BIN)\pip install -r requirements-dev.txt

setup: $(VENV)

clean:
	if exist $(VENV) rmdir /S /Q $(VENV)
	if exist __pycache__ rmdir /S /Q __pycache__
	if exist .pytest_cache rmdir /S /Q .pytest_cache
	if exist .coverage del /F /Q .coverage
	if exist htmlcov rmdir /S /Q htmlcov
	if exist .mypy_cache rmdir /S /Q .mypy_cache
	if exist build rmdir /S /Q build
	if exist dist rmdir /S /Q dist
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /S /Q "%%d"
	del /S /Q *.pyc *.pyo *.pyd 2>nul

build: setup
	$(BIN)\python setup.py build

test: setup
	$(BIN)\pytest $(TESTS) \
		--cov=$(SRC) \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-fail-under=80 \
		-v

format: setup
	$(BIN)\isort $(SRC) --skip-glob="**/env/*" --skip-glob="*_env/*" --skip-glob="**/*_venv/*"
	$(BIN)\black $(SRC) --exclude="(.*/|)*(env|venv)"

lint: setup
	$(BIN)\flake8 $(SRC) --exclude=".env,venv,*_env,*_venv"
	$(BIN)\mypy $(SRC) --exclude="(.*/)?(env|venv)/"

release: setup
	$(BIN)\pyinstaller --onefile --noconsole \
		--name ES_BLE_VR_Glove \
		--add-data "assets;assets" \
		main.py
	copy MotionCal.exe dist\
	copy gatt.json dist\
	xcopy /E /I assets dist\assets

.DEFAULT_GOAL := all