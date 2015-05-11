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
def deploy_prep():
    session = 'o-deploy-prep'
    undercloud.ssh_to_undercloud(session)
    tmux.run(session, "openstack baremetal import ~/instackenv.json --json --debug")
    tmux.run(session, "openstack baremetal configure boot --debug")
    tmux.run(session, ("openstack baremetal introspection all start "
                       "--discoverd-url http://localhost:5050 --debug"))
    tmux.run(session, "instack-ironic-deployment --setup-flavors")


@task
def deploy():
    session = 'o-deploy'
    undercloud.ssh_to_undercloud(session)
    tmux.run(session, "openstack overcloud deploy --debug")
