from fabric.api import env, task

from instrap import config, host, undercloud, overcloud  # NOQA

env.user = config.USER


@task
def full():
    """All in one. Setup the host and then undercloud."""
    host.setup(block=True)
    undercloud.create()

    print "We didn't do the overcloud, you need to trigger that"
    print "when the undercloud is ready."
