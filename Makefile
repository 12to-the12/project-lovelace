#!make
include .env


default: all
all: install run

install:
	setup 3.12 uv

run:
	.venv/bin/python src/main.py

clean:
	rm -rf ./.venv
	rm -rf ./venv/
	rm -rf ./build/
	rm -rf ./dist/
	rm ./main.spec

environment-install:
	wine ${wPython}/python.exe ${wPython}/Scripts/pip.exe install -r requirements.txt

build-exe: clean environment-install
	# pyinstaller --windowed ./src/main.py
	/home/logan/.wine/drive_c/users/logan/AppData/Local/Programs/Python/Python313/Scripts/pyinstaller.exe ./src/main.py


test-exe: build-exe
	wine ./dist/main/main.exe