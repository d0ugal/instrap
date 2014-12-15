from fabric.api import env, task

from instrap import config, host, undercloud  # NOQA

env.user = config.USER


@task
def full():
    host.setup(block=True)
    undercloud.create()
