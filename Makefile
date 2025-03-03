#!make
include .env


default: all
all: start-server install run

# local:
# 	./.venv/bin/python/ ./src/server/server.py
# 	./.venv/bin/python ./src/main.py
format:
	ruff format

check:
	ruff check
	mypy

install: format
	setup 3.13 uv
	# .venv/bin/python src/main.py


run:
	.venv/bin/python src/main.py

clean:
	-rm -rf ./.venv
	-rm -rf ./venv/
	-rm -rf ./build/
	-rm -rf ./dist/
	-rm ./main.spec


stop-server:
	-ssh lovelace "tmux kill-session -t 'server'"
	
push-server: stop-server
	cp ./src/config.py ./server-src/config.py
	rsync -avzh ./server-src/ lovelace:~/server/ --delete

start-server: push-server
	ssh lovelace "tmux new-session -d -s 'server' ./server/main.py"
	ssh lovelace "tmux ls"

start-server-attached: push-server
	ssh lovelace "~/server/main.py"


environment-install:
	wine ${wPython}/python.exe ${wPython}/Scripts/pip.exe install -r requirements.txt

build-exe: clean environment-install
	# pyinstaller --windowed ./src/main.py
	/home/logan/.wine/drive_c/users/logan/AppData/Local/Programs/Python/Python313/Scripts/pyinstaller.exe --onefile --windowed --add-data "rootCA.pem;rootCA.pem" ./src/main.py


test-exe: build-exe
	wine ./dist/main.exe