from fabric.api import sudo


def create_session(name):
    sudo("tmux kill-session -t {}".format(name), user="stack", warn_only=True)
    sudo("tmux new -d -s {}".format(name), user="stack", warn_only=True)


def run_command(session, command):
    send = "tmux send -t {0}.0 '{1}' ENTER".format(session, command)
    return sudo(send, user="stack")


def get_buffer(session):
    sudo("tmux capture-pane -p -t {0}".format(session), user="stack")
