from fabric.api import env, task

from instrap import host, undercloud, overcloud  # NOQA

env.user = 'root'


@task
def full_under():
    """All in one. Setup the host and then undercloud."""
    undercloud.destroy()
    host.setup(block=True)
    undercloud.create()

    print "We didn't do the overcloud, you need to trigger that"
    print "when the undercloud is ready."


@task
def full():
    """All in one. Setup the host, undercloud and deploy the overcloud"""
    undercloud.destroy()
    host.setup(block=True)
    undercloud.create()
    overcloud.full()
