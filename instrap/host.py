from fabric.api import task, sudo, settings


from instrap import tmux, config


def yum():
    # Step 0
    sudo('yum upgrade -q -y')
    sudo('yum install -q -y git tmux sshpass')


def download_images():
    # step 7 prep (Start early)
    sudo("mkdir -p ~/images", user='stack')
    tmux.create_session("image-dl")
    tmux.run('image-dl', 'cd ~/images')
    for f in config.IMAGES:
        tmux.run('image-dl', "wget {}".format(f))


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

    sudo("mkdir -p ~/instack", user='stack')
    tmux.create_session("tripleo")
    tmux.run('tripleo', 'cd ~/instack')
    tmux.run('tripleo', "git clone {}".format(config.UNDERCLOUD_REPO))
    tmux.run('tripleo', "git clone {}".format(config.TRIPLEO_REPO))
    tmux.run('tripleo', "source {}".format(config.SOURCERC))
    tmux.run('tripleo', "tripleo install-dependencies")
    tmux.run('tripleo', "tripleo set-usergroup-membership")


@task
def setup():
    """Setup the host. Create user, download images, tripleo setup"""
    # Step 0
    yum()

    # Step 1
    create_user()

    # step 7 prep (Start early)
    download_images()

    # Step 2 & 3
    tripleo_setup()


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
