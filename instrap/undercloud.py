from __future__ import print_function

from time import sleep

from fabric.api import task, sudo, cd
from fabric.context_managers import hide
from slugify import slugify

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

        if not undercloud_ip:
            print("Undercloud mac found, but no IP yet.")
            return

    print("Undercloud IP", repr(undercloud_ip))

    return undercloud_ip


def _ssh_to_undercloud(session):
    undercloud_ip = ip()

    if not undercloud_ip:
        return

    tmux.create_session(session)
    tmux.run(session, "ssh stack@{}".format(undercloud_ip))
    tmux.run(session, "stack")


def _load_env(session):

    tmux.run(session, 'sudo cp /root/tripleo-undercloud-passwords ~/')
    tmux.run(session, 'sudo cp /root/stackrc ~/')

    tmux.run(session, 'source ~/deploy-overcloudrc')
    tmux.run(session, 'source ~/tripleo-undercloud-passwords')
    tmux.run(session, 'source ~/stackrc')
    tmux.run(session, 'source /usr/share/instack-undercloud/deploy-virt-overcloudrc')  # NOQA


def undercloud_setup():
    # step 6

    session = 'undercloud'

    _ssh_to_undercloud(session)
    tmux.run(session, "sudo curl -o /etc/yum.repos.d/slagle-openstack-m.repo https://copr.fedoraproject.org/coprs/slagle/openstack-m/repo/fedora-20/slagle-openstack-m-fedora-20.repo")  # NOQA
    tmux.run(session, "sudo yum -y install https://repos.fedorapeople.org/repos/openstack/openstack-juno/rdo-release-juno-1.noarch.rpm")  # NOQA
    tmux.run(session, "sudo sed -i 's#repos.fedorapeople.org/repos#rdo-stage.virt.bos.redhat.com#' /etc/yum.repos.d/rdo-release.repo")  # NOQA
    tmux.run(session, "sudo yum -y install instack-undercloud")

    # TODO: REMOVE THIS HACK WHEN THIS IS PAKAGED:
    # https://github.com/agroup/instack-undercloud/pull/112
    print("#" * 50)
    print("Patching instack. This is horrible.")
    tmux.run(session, "sudo sed -i -e 's/--public//g' /usr/bin/instack-prepare-for-overcloud")  # NOQA
    print("#" * 50)

    tmux.run(session, "instack-install-undercloud")


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

    session = "u-instack-virt"

    tmux.create_session(session)
    tmux.run(session, 'sudo su - stack')
    tmux.run(session, "source {}".format(config.SOURCERC))
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


@task
def recreate():
    """A simple helper which calls undercloud.destroy and undercloud.create"""
    destroy()
    create()


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

    tmux.kill_session('undercloud_pw_fix')


@task
def _client_setup(session):
    tmux.run(session, "sudo yum upgrade -y -q && sudo yum install -y -q vim ack")
    tmux.run(session, "sudo pip install -U virtualenv virtualenvwrapper")
    tmux.run(session, "echo \"\nsource /usr/bin/virtualenvwrapper.sh\" >> \"$(echo /home/stack/.bashrc)\"")  # NOQA
    tmux.run(session, "source /usr/bin/virtualenvwrapper.sh")


@task
def install_tuskarclient_from_review(changes_ref):

    session = 'u-tuskarclient'
    gerrit = 'https://review.openstack.org/openstack/python-tuskarclient'

    _ssh_to_undercloud(session)
    _client_setup(session)

    name = slugify(changes_ref, to_lower=True)
    tmux.run(session, 'mkvirtualenv tuskarclient-review-{}'.format(name))
    tmux.run(session, 'cd ~ && sudo rm -rf ~/python-tuskarclient')
    tmux.run(session, 'git clone https://git.openstack.org/openstack/python-tuskarclient')  # NOQA
    tmux.run(session, 'cd python-tuskarclient')
    tmux.run(session, 'git fetch {0} {1}'.format(gerrit, changes_ref))
    tmux.run(session, 'git checkout FETCH_HEAD')
    tmux.run(session, 'sudo pip install -I .')


@task
def install_tuskarclient_from_git(repo=None, branch=None):

    session = 'u-tuskarclient'

    if repo is None:
        repo = "https://git.openstack.org/openstack/python-tuskarclient"

    if branch is None:
        branch = "master"

    _ssh_to_undercloud(session)
    _client_setup(session)
    tmux.run(session, 'mkvirtualenv tuskarclient-git')
    tmux.run(session, 'cd ~ && sudo rm -rf ~/python-tuskarclient')
    tmux.run(session, 'git clone {0} -b {1}'.format(repo, branch))
    tmux.run(session, 'cd python-tuskarclient')
    tmux.run(session, 'sudo pip install -I .')


@task
def install_tuskarclient_from_pypi(repo=None, branch=None):

    session = 'u-tuskarclient'

    _ssh_to_undercloud(session)
    _client_setup(session)
    tmux.run(session, 'mkvirtualenv tuskarclient-pypi')
    tmux.run(session, 'sudo pip install -IU tuskar')


@task
def start_ssh_session(name):
    session = "u-{0}".format(name)
    _ssh_to_undercloud(session)
    _client_setup(session)
    _load_env(session)

    print("Started tmux session named {}".format(session))
