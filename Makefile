.PHONY: setup clean build test format lint release govenv all

PYTHON := python
VENV := venv
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

govenv: setup
	@echo Activating virtual environment...
	@powershell -NoExit -Command "& '$(BIN)\Activate.ps1'"

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
		--icon assets/logo.ico \
		--add-data "assets;assets" \
		--add-data "MotionCal.exe;." \
		--add-data "gatt.json;." \
		main.py
	if not exist dist mkdir dist
	copy /Y MotionCal.exe "dist\"
	copy /Y gatt.json "dist\"
	if not exist "dist\assets" mkdir "dist\assets"
	xcopy /Y /E /I assets "dist\assets"

.DEFAULT_GOAL := all