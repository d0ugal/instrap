from __future__ import print_function

from time import sleep

from fabric.api import task, sudo
from fabric.context_managers import hide
from fabric.contrib import files

from instrap import tmux


@task
def ip():
    """Output the IP address of the undercloud if it has been created"""

    with hide('running'):
        mac = sudo("tripleo get-vm-mac instack", user='stack')

        if not mac:
            print("Undercloud not found.")
            return

        undercloud_ip = sudo(("cat /var/lib/libvirt/dnsmasq/default.leases "
                              "| grep {} | awk '{{print $3;}}'").format(mac),
                             user='stack')

        if not undercloud_ip:
            print("Undercloud mac found, but no IP yet.")
            return

    ips = set(undercloud_ip.splitlines())

    if len(ips) > 1:
        print(undercloud_ip)
        print(ips)
        raise Exception("Multiple IPs found: {0}".format(ips))

    undercloud_ip = ips.pop()

    print("Undercloud IP", repr(undercloud_ip))

    return undercloud_ip


def ssh_to_undercloud(session):
    undercloud_ip = ip()

    if not undercloud_ip:
        return

    tmux.create_session(session)
    tmux.run(session, "ssh -oStrictHostKeyChecking=no root@{}".format(
        undercloud_ip))
    tmux.run(session, "su stack")
    tmux.run(session, "cd ~")
    tmux.run(session, "source ~/tripleo-undercloud-passwords")
    tmux.run(session, "source ~/stackrc")


@task
def create():
    """Create the virt machines for the undercloud """

    session = "u-instack-virt"

    tmux.create_session(session)
    tmux.run(session, "cd ~")
    tmux.run(session, "export NODE_DIST=centos7")
    tmux.run(session, "export NODE_COUNT=4")
    files.append('/etc/hosts', "127.0.0.1 localhost.localhost")
    tmux.run(session, "instack-virt-setup")
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


def setup():
    undercloud_ip = ip()
    while undercloud_ip is None:
        print("Waiting for undercloud...")
        sleep(15)
        undercloud_ip = ip()

    session = "u-setup"
    ssh_to_undercloud(session)
    tmux.run(session,
        "curl https://raw.githubusercontent.com/rdo-management/instack-undercloud/master/scripts/instack-setup-host | bash -x")
    tmux.run(session, "sudo yum install -y instack-undercloud python-rdomanager-oscplugin")
    tmux.run(session, "openstack undercloud install")


@task
def ssh(name):
    """Create an ssh session to the undercloud with the given name."""
    session = "u-{0}".format(name)
    ssh_to_undercloud(session)

    print("Started tmux session named {}".format(session))
