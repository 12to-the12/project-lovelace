#!make
include .env


default: all
all: start-server install run

format:
	ruff format

check:
	ruff check

install: format
	setup 3.12 uv
	.venv/bin/python src/main.py


run:
	.venv/bin/python src/main.py

clean:
	-rm -rf ./.venv
	-rm -rf ./venv/
	-rm -rf ./build/
	-rm -rf ./dist/
	-rm ./main.spec


stop-server:
	-ssh services "tmux kill-session -t 'server'"
	
push-server: stop-server
	rsync -avzch ./src/server/ services:~/server/

start-server: push-server
	ssh services "tmux new-session -d -s 'server' ./server/server.py"
	ssh services "tmux ls"
environment-install:
	wine ${wPython}/python.exe ${wPython}/Scripts/pip.exe install -r requirements.txt

build-exe: clean environment-install
	# pyinstaller --windowed ./src/main.py
	/home/logan/.wine/drive_c/users/logan/AppData/Local/Programs/Python/Python313/Scripts/pyinstaller.exe --onefile --windowed --add-data "rootCA.pem;rootCA.pem" ./src/main.py


test-exe: build-exe
	wine ./dist/main/main.exe