from __future__ import print_function

from fabric.api import task, sudo, settings
from fabric.context_managers import hide

from instrap import tmux


def yum():
    sudo('yum install -q -y deltarpm')
    sudo('yum upgrade -q -y')
    sudo('yum install -q -y tmux sshpass ack')


def create_user():
    result = sudo('useradd stack', warn_only=True)

    if result.return_code != 0:
        print("User already exists.")
        return

    sudo('echo "stack:stack" | chpasswd')
    sudo('echo "stack ALL=(root) NOPASSWD:ALL" '
         '| sudo tee -a /etc/sudoers.d/stack')
    sudo('chmod 0440 /etc/sudoers.d/stack')

    with settings(sudo_user='stack'):
        sudo("echo 'export LIBVIRT_DEFAULT_URI=\"qemu:///system\"' "
             ">> ~/.bashrc")


@task
def setup(block=False):
    """Setup the host. Create user, download images, tripleo setup"""

    yum()
    create_user()

    session = "h-prep"
    tmux.create_session(session)
    tmux.run(session,
        "curl https://raw.githubusercontent.com/rdo-management/instack-undercloud/master/scripts/instack-setup-host | bash -x")

    tmux.run(session, "sudo yum install -y instack-undercloud")

    while block:

        with hide('running'):
            pkg = "instack-undercloud"
            installed = sudo("yum list installed {0}".format(pkg), user='stack')

            if pkg in installed:
                break

            print("Waiting for {0} to be installed".format(pkg))


@task
def virsh_list():
    """Display the status of the VM's used for the undercloud virst setup"""
    return sudo("virsh list --all", user="stack")
