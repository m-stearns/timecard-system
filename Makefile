# For speeding up builds. You can find more info at:
# https://www.docker.com/blog/faster-builds-in-compose-thanks-to-buildkit-support/
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down --remove-orphans

test:
	docker-compose run --rm --no-deps --entrypoint=pytest timecardservice /tests/

linter:
	python -m flake8 ./src/