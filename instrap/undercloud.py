from __future__ import print_function

from time import sleep

from fabric.api import task, sudo, cd
from fabric.context_managers import hide

from instrap import tmux, config


@task
def ip():
    """Output the IP address of the undercloud if it has been created"""

    with hide('running'):
        with cd("~/instack"):
            mac = sudo("source {} && tripleo get-vm-mac instack".format(
                config.SOURCERC), user='stack')

        if not mac:
            print("Undercloud not found.")
            return

        undercloud_ip = sudo(("cat /var/lib/libvirt/dnsmasq/default.leases "
                              "| grep {} | awk '{{print $3;}}'").format(mac),
                             user='stack')

    print("Undercloud IP", repr(undercloud_ip))

    return undercloud_ip


def undercloud_setup():
    # step 6

    undercloud_ip = ip()

    if not undercloud_ip:
        return

    tmux.create_session("undercloud")
    tmux.run('undercloud', "ssh stack@{}".format(undercloud_ip))
    tmux.run('undercloud', "stack")
    tmux.run('undercloud', "sudo curl -o /etc/yum.repos.d/slagle-openstack-m.repo https://copr.fedoraproject.org/coprs/slagle/openstack-m/repo/fedora-20/slagle-openstack-m-fedora-20.repo")  # NOQA
    tmux.run('undercloud', "sudo yum -y install https://repos.fedorapeople.org/repos/openstack/openstack-juno/rdo-release-juno-1.noarch.rpm")  # NOQA
    tmux.run('undercloud', "sudo sed -i 's#repos.fedorapeople.org/repos#rdo-stage.virt.bos.redhat.com#' /etc/yum.repos.d/rdo-release.repo")  # NOQA
    tmux.run('undercloud', "sudo yum -y install instack-undercloud")
    tmux.run('undercloud', "instack-install-undercloud")


def undercloud_copy_images():
    # step 7

    undercloud_ip = ip()

    if not undercloud_ip:
        return

    print("Copying images to the instack VM")

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


@task
def setup():
    """Copy the images to the undercloud and start a SSH session"""

    undercloud_ip = ip()
    while undercloud_ip is None or undercloud_ip == '':
        print("Waiting for undercloud...")
        sleep(30)
        undercloud_ip = ip()

    # TODO: Remove this hack. Currently the stack user is created
    # without a password, we can correct as root and fix this.
    tmux.create_session("undercloud_pw_fix")
    tmux.run('undercloud_pw_fix',
             "ssh -oStrictHostKeyChecking=no root@{}".format(undercloud_ip))
    tmux.run('undercloud_pw_fix', "passwd stack")
    tmux.run('undercloud_pw_fix', "stack")
    tmux.run('undercloud_pw_fix', "stack")

    # step 7
    undercloud_copy_images()
    # step 6 & 8
    undercloud_setup()
