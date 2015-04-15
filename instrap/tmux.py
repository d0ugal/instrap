from fabric.api import sudo


def kill_session(name):
    sudo("tmux kill-session -t {}".format(name), user="stack", warn_only=True)


def create_session(name, kill=True):
    if kill:
        kill_session(name)
    sudo("tmux new -d -s {}".format(name), user="stack", warn_only=True)


def run(session, command):
    send = "tmux send -t {0}.0 '{1}' ENTER".format(session, command)
    return sudo(send, user="stack")


def get_buffer(session):
    sudo("tmux capture-pane -p -t {0} -S -1000".format(session), user="stack")


def get_session_names():
    r = sudo("tmux ls", user="stack", warn_only=True)

    print r

    for line in r.splitlines():

        if ':' not in line:
            continue

        yield line.split(':', 1)[0]


def kill_all_sessions(starting_with=None):

    for session in get_session_names():

        if starting_with is not None:
            if not session.startswith(starting_with):
                continue

        kill_session(session)
