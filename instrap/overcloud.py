from fabric.api import task

from instrap import undercloud
from instrap import tmux


@task
def build_images():

    session = 'o-build-images'
    undercloud.ssh_to_undercloud(session)
    tmux.run(session, "export NODE_DIST=centos7")
    tmux.run(session, "instack-build-images")
    tmux.run(session, "instack-prepare-for-overcloud")


@task
def register_nodes():
    session = 'o-register-nodes'
    undercloud.ssh_to_undercloud(session)
    tmux.run(session, "jq '.nodes' instackenv.json > instacknodes.json")
    tmux.run(session, "openstack baremetal import ~/instacknodes.json --json")
    tmux.run(session, ("openstack baremetal introspection all start "
                       "--discoverd-url http://localhost:5050"))


@task
def all():

    build_images()
    register_nodes()
