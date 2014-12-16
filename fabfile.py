from fabric.api import env, task

from instrap import config, host, undercloud  # NOQA

env.user = config.USER


@task
def full():
    """All in one. Setup the host and then undercloud."""
    host.setup(block=True)
    undercloud.create()
