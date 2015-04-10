from fabric.api import env, task

from instrap import host, undercloud  # NOQA

env.user = 'root'


@task
def full():
    """All in one. Setup the host and then undercloud."""
    host.setup(block=True)
    undercloud.create()

    print "We didn't do the overcloud, you need to trigger that"
    print "when the undercloud is ready."
