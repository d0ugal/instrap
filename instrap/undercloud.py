from __future__ import print_function

from time import sleep

from fabric.api import task, sudo, cd
from fabric.context_managers import hide

from instrap import tmux, config


@task
def ip():
    """Output the IP address of the undercloud if it has been created"""

    with hide('running', 'stdout'):
        with cd("~/instack"):
            mac = sudo("source {} && tripleo get-vm-mac instack".format(
                config.SOURCERC), user='stack')

        if not mac:
            print("Undercloud not found.")
            return

        undercloud_ip = sudo(("cat /var/lib/libvirt/dnsmasq/default.leases "
                              "| grep {} | awk '{{print $3;}}'").format(mac),
                             user='stack')

    print("Undercloud IP", undercloud_ip)

    return undercloud_ip


def _undercloud_ssh():
    # step 6

    undercloud_ip = ip()

    if not undercloud_ip:
        return

    tmux.create_session("undercloud")
    tmux.run('undercloud', "ssh stack@{}".format(undercloud_ip))
    tmux.run('undercloud', "stack")
    tmux.run('undercloud', "git clone {} --branch={}".format(
        config.UNDERCLOUD_REPO, config.UNDERCLOUD_BRANCH))
    tmux.run('undercloud', "source instack-undercloud/instack-sourcerc")
    tmux.run('undercloud', "instack-install-undercloud-source")


def _undercloud_copy_images():
    # step 7

    undercloud_ip = ip()

    if not undercloud_ip:
        return

    sudo(("sshpass -p 'stack' "
          "scp -oStrictHostKeyChecking=no ~/images/* "
          "stack@{}:").format(undercloud_ip),
         user='stack')


@task
def create():
    """Create and start virtual environment for instack"""
    # step 4 & 5

    tmux.create_session("instack")
    tmux.run('instack', 'sudo su - stack')
    tmux.run('instack', 'cd ~/instack')
    tmux.run('instack', "source {}".format(config.SOURCERC))
    tmux.run('instack', "instack-virt-setup")
    setup()


@task
def destroy():
    """Destroy the virt machines for the undercloud """

    from instrap import host

    vms = host.virsh_list()

    names = ['baremetal_{}'.format(i) for i in range(4)]
    names.append('instack')

    for name in names:
        if name not in vms:
            continue
        sudo("virsh destroy {}".format(name), user="stack", warn_only=True)
        sudo("virsh undefine {}".format(name), user="stack")


@task
def recreate():
    """A simple helper which calls undercloud.destroy and undercloud.create"""
    destroy()
    create()


def setup():
    """Copy the images to the undercloud and start a SSH session"""

    undercloud_ip = None
    while undercloud_ip is None:
        print("Waiting for undercloud...")
        undercloud_ip = ip()
        sleep(30)

    # step 7
    _undercloud_copy_images()
    # step 6 & 8
    _undercloud_ssh()
