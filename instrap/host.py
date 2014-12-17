from __future__ import print_function

from time import sleep
from urllib2 import urlopen

from fabric.api import task, sudo, settings
from fabric.context_managers import hide

from instrap import tmux, config


def yum():
    # Step 0
    sudo('yum upgrade -q -y')
    sudo('yum install -q -y git tmux sshpass')


def download_images():

    try:
        if are_images_downloaded():
            return True
    except Exception:
        pass

    # step 7 prep (Start early)
    tmux.create_session("image-dl")
    sudo("rm -rf ~/images", user='stack')
    sudo("mkdir -p ~/images", user='stack')
    tmux.run('image-dl', 'cd ~/images')
    tmux.run('image-dl', "wget {}".format(config.IMAGES_SHAS))
    for f in config.IMAGES:
        tmux.run('image-dl', "wget {}".format(f))


def are_images_downloaded():

    print("Checking for images...")
    response = urlopen(config.IMAGES_SHAS)
    text = [l.strip() for l in response.readlines()]

    d = {p.split('  ')[1]: p.split('  ')[0] for p in text}

    for image in config.IMAGES:
        name = image.rsplit('/', 1)[-1].strip()
        with hide('running', 'stdout'):
            sha = sudo("openssl dgst -sha256 ~/images/{}".format(name),
                       user='stack')[-64:]
            if name not in d:
                print("Missing image: %r" % name)
                return False
            if d[name] != sha:
                print("SHA mismatch: {}. (probably still downloading)"
                      .format(name))
                return False

    print("Images downloaded")
    return True


def create_user():
    # Step 1
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


def tripleo_setup():
    # Step 2 & 3

    if user_membership():
        return True

    sudo("mkdir -p ~/instack", user='stack')
    tmux.create_session("tripleo")
    tmux.run('tripleo', 'cd ~/instack')
    tmux.run('tripleo', "git clone {} --branch={}".format(
        config.UNDERCLOUD_REPO, config.UNDERCLOUD_BRANCH))
    tmux.run('tripleo', "git clone {}".format(config.TRIPLEO_REPO))
    tmux.run('tripleo', "source {}".format(config.SOURCERC))
    tmux.run('tripleo', "tripleo install-dependencies")
    tmux.run('tripleo', "tripleo set-usergroup-membership")


def user_membership():
    with hide('running', 'stdout'):
        membership = 'libvirtd' in sudo('id', user='stack')
        print("Stack user in libvirtd", membership)
        return membership


@task
def setup(block=False):
    """Setup the host. Create user, download images, tripleo setup"""
    # Step 0
    yum()

    # Step 1
    create_user()

    # step 7 prep (Start early)
    images_downloaded = download_images()

    # Step 2 & 3
    user_in_libvirtd = tripleo_setup()

    if block:
        print("Waiting for tripleo setup and images to download.")
        while not user_in_libvirtd or not images_downloaded:
            sleep(60)
            if not user_in_libvirtd:
                user_in_libvirtd = user_membership()
            if not images_downloaded:
                images_downloaded = are_images_downloaded()


@task
def virsh_list():
    """Display the status of the VM's used for the undercloud virst setup"""
    return sudo("virsh list --all", user="stack")


@task
def tmux_list():
    """Display the active tmux sessions"""
    sudo("tmux ls", user="stack")


@task
def tmux_buffer(session):
    """Display the current buffer for a given tmux session"""
    tmux.get_buffer(session)


@task
def list_images():
    """Display the active tmux sessions"""
    sudo("ls -la ~/images", user="stack")
