import docker
import os
import argparse
from subprocess import call

NAME = "forensicarchitecture/mtriage"
CONT_NAME = NAME.replace("/", "_")  # docker doesn't allow slashes in cont names
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ENV_FILE = "{}/.env".format(DIR_PATH)
HOME_PATH = os.path.expanduser("~")
DOCKER = docker.from_env()


def build():
    # TODO: port to docker py CLI.
    print("Building {} image in Docker...".format(NAME))
    print("This may take a few minutes...")
    try:
        call(
            [
                "docker",
                "build",
                "-t",
                "{}:dev".format(NAME),
                "-f",
                "development.Dockerfile",
                ".",
            ]
        )
        print("Build successful, run with: \n\tpython run.py develop")
    except:
        print("Something went wrong. Run command directly to debug:")
        print("\tdocker build -t {}:dev -f development.Dockerfile .".format(NAME))


def develop():
    try:
        DOCKER.containers.get(CONT_NAME)
        print("Develop container already running. Stop it and try again.")
    except docker.errors.NotFound:
        print("Building container from {}:dev...".format(NAME))
        # TODO: remake with docker py CLI.
        call(
            [
                "docker",
                "run",
                "-it",
                "--name",
                CONT_NAME,
                "--env",
                "BASE_DIR=/mtriage",
                "--env-file={}".format(ENV_FILE),
                "--rm",
                "--privileged",
                "-v",
                "{}:/mtriage".format(DIR_PATH),
                "-v",
                "{}/.config/gcloud:/root/.config/gcloud".format(HOME_PATH),
                "{}:dev".format(NAME),
            ]
        )


def __run_cmd(cmd):
    res = DOCKER.containers.run(
        "{}:dev".format(NAME),
        command=cmd,
        remove=True,
        privileged=True,
        volumes={
            DIR_PATH: {"bind": "/mtriage", "mode": "rw"},
            "{}/.config/gcloud".format(HOME_PATH): {
                "bind": "/root/.config/gcloud",
                "mode": "rw",
            },
        },
        environment={"BASE_DIR": "/mtriage"},
    )
    print(res)


def test():
    print("Creating container to run tests...")
    print("----------------------------------")
    __run_cmd("python src/test/all.py")
    print("----------------------------------")
    print("All tests for mtriage done.")


if __name__ == "__main__":
    COMMANDS = {"build": build, "develop": develop, "test": test}
    parser = argparse.ArgumentParser(description="mtriage dev scripts")
    parser.add_argument("command", choices=COMMANDS.keys())

    args = parser.parse_args()

    cmd = COMMANDS[args.command]
    cmd()
