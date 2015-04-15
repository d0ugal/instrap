from __future__ import print_function

from time import sleep

from fabric.api import task, sudo
from fabric.context_managers import hide
from fabric.contrib import files
from slugify import slugify

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
    sleep(1)
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

    tmux.kill_all_sessions('u-')
    tmux.kill_all_sessions('o-')


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
    _client_setup(session)

    print("Started tmux session named {}".format(session))


def _client_setup(session):
    tmux.run(session, "sudo yum upgrade -y -q && sudo yum install -y -q vim ack")
    tmux.run(session, "sudo pip install -U virtualenv virtualenvwrapper")
    tmux.run(session, "echo \"\nsource /usr/bin/virtualenvwrapper.sh\" >> \"$(echo /home/stack/.bashrc)\"")  # NOQA
    tmux.run(session, "source /usr/bin/virtualenvwrapper.sh")


@task
def tuskarclient_from_review(changes_ref):

    session = 'u-tuskarclient'
    gerrit = 'https://review.openstack.org/openstack/python-tuskarclient'

    ssh_to_undercloud(session)
    _client_setup(session)

    name = slugify(changes_ref, to_lower=True)
    tmux.run(session, 'rmvirtualenv tuskarclient-review-{}'.format(name))
    tmux.run(session, 'mkvirtualenv tuskarclient-review-{}'.format(name))
    tmux.run(session, 'cd ~ && rm -rf ~/python-tuskarclient')
    tmux.run(session, 'git clone https://git.openstack.org/openstack/python-tuskarclient')  # NOQA
    tmux.run(session, 'cd python-tuskarclient')
    tmux.run(session, 'git fetch {0} {1}'.format(gerrit, changes_ref))
    tmux.run(session, 'git checkout FETCH_HEAD')
    tmux.run(session, 'pip install -I .')


@task
def rdomanager_from_review(changes_ref):

    session = 'u-rdomanager'
    gerrit = 'https://review.gerrithub.io/rdo-management/python-rdomanager-oscplugin'

    ssh_to_undercloud(session)
    _client_setup(session)

    name = slugify(changes_ref, to_lower=True)
    tmux.run(session, 'rmvirtualenv rdomanager-review-{}'.format(name))
    tmux.run(session, 'mkvirtualenv rdomanager-review-{}'.format(name))
    tmux.run(session, 'cd ~ && rm -rf ~/python-rdomanager-oscplugin')
    tmux.run(session, 'git clone https://github.com/rdo-management/python-rdomanager-oscplugin.git')  # NOQA
    tmux.run(session, 'cd python-rdomanager-oscplugin')
    tmux.run(session, 'git fetch {0} {1}'.format(gerrit, changes_ref))
    tmux.run(session, 'git checkout FETCH_HEAD')
    tmux.run(session, 'pip install --editable .')
