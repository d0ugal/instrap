from __future__ import print_function

from fabric.api import cd, env, settings, sudo

UNDERCLOUD_REPO = "https://github.com/agroup/instack-undercloud.git"
TRIPLEO_REPO = "https://git.openstack.org/openstack/tripleo-incubator"
SOURCERC = "instack-undercloud/instack-sourcerc"

env.user = 'root'

IMAGES = [
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/SHA256SUMS',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/deploy-ramdisk-ironic.initramfs',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/deploy-ramdisk-ironic.kernel',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/discovery-ramdisk.initramfs',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/discovery-ramdisk.kernel',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/fedora-user.qcow2',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.initrd',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.qcow2',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.vmlinuz',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.initrd',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.qcow2',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.vmlinuz',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.initrd',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.qcow2',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.vmlinuz',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.initrd',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.qcow2',  # NOQA
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.vmlinuz ',  # NOQA
]


def _tmux_create(name):
    sudo("tmux kill-session -t {}".format(name), user="stack", warn_only=True)
    sudo("tmux new -d -s {}".format(name), user="stack", warn_only=True)


def _tmux(session, command):
    send = "tmux send -t {0}.0 '{1}' ENTER".format(session, command)
    return sudo(send, user="stack")


def _tmux_buffer(session):
    sudo("tmux capture-pane -p -t {0}".format(session), user="stack")


def _host_setup():
    # Step 0
    sudo('yum upgrade -q -y')
    sudo('yum install -q -y git tmux sshpass')


def _host_download_images():
    # step 7 prep (Start early)
    sudo("mkdir -p ~/images", user='stack')
    _tmux_create("image-dl")
    _tmux('image-dl', 'cd ~/images')
    for f in IMAGES:
        _tmux('image-dl', "wget {}".format(f))


def _host_create_user():
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


def _host_initial_setup():
    # Step 2 & 3

    sudo("mkdir -p ~/instack", user='stack')
    _tmux_create("tripleo")
    _tmux('tripleo', 'cd ~/instack')
    _tmux('tripleo', "git clone {}".format(UNDERCLOUD_REPO))
    _tmux('tripleo', "git clone {}".format(TRIPLEO_REPO))

    _tmux('tripleo', "source {}".format(SOURCERC))
    _tmux('tripleo', "tripleo install-dependencies")
    _tmux('tripleo', "tripleo set-usergroup-membership")


def undercloud_ip():
    """Output the IP address of the undercloud if it has been created"""

    with cd("~/instack"):
        mac = sudo("source {} && tripleo get-vm-mac instack".format(
            SOURCERC), user='stack')

    if not mac:
        print("Undercloud not found.")
        return

    ip = sudo(("cat /var/lib/libvirt/dnsmasq/default.leases "
               "| grep {} | awk '{{print $3;}}'").format(mac), user='stack')

    print("Undercloud IP", ip)

    return ip


def host():
    """Setup the host. Create user, download images, tripleo setup"""
    # Step 0
    _host_setup()

    # Step 1
    _host_create_user()

    # step 7 prep (Start early)
    _host_download_images()

    # Step 2 & 3
    _host_initial_setup()


def host_virsh_list():
    """Display the status of the VM's used for the undercloud virst setup"""
    return sudo("virsh list --all", user="stack")


def host_tmux_list():
    """Display the active tmux sessions"""
    sudo("tmux ls", user="stack")


def host_tmux_buffer(session):
    """Display the current buffer for a given tmux session"""
    _tmux_buffer(session)


def host_list_images():
    """Display the active tmux sessions"""
    sudo("ls -la ~/images", user="stack")


def undercloud_create():
    """Create and start virtual environment for instack"""
    # step 4 & 5

    _tmux_create("instack")
    _tmux('instack', 'sudo su - stack')
    _tmux('instack', 'cd ~/instack')
    _tmux('instack', "source {}".format(SOURCERC))
    _tmux('instack', "instack-virt-setup")


def undercloud_destroy():
    """Destroy the virt machines for the undercloud """

    vms = host_virsh_list()

    names = ['baremetal_{}'.format(i) for i in range(4)]
    names.append('instack')

    sudo("virsh list --all", user="stack")

    for name in names:
        if name not in vms:
            continue
        sudo("virsh destroy {}".format(name), user="stack", warn_only=True)
        sudo("virsh undefine {}".format(name), user="stack")


def _undercloud_ssh():
    # step 6

    ip = undercloud_ip()

    if not ip:
        return

    _tmux_create("undercloud")
    _tmux('undercloud', "ssh stack@{}".format(ip))
    _tmux('undercloud', "stack")
    _tmux('undercloud', "git clone {}".format(UNDERCLOUD_REPO))
    _tmux('undercloud', "source instack-undercloud/instack-sourcerc")
    _tmux('undercloud', "export PACKAGES=0")
    _tmux('undercloud', "instack-install-undercloud-source")
    _tmux('undercloud', "sudo cp /root/tripleo-undercloud-passwords ~/")
    _tmux('undercloud', "sudo cp /root/stackrc ~/")


def _undercloud_copy_images():
    # step 7

    ip = undercloud_ip()

    if not ip:
        return

    sudo(("sshpass -p 'stack' "
          "scp -oStrictHostKeyChecking=no ~/images/* stack@{}:").format(ip),
         user='stack')


def undercloud_setup():
    """Copy the images to the undercloud and start a SSH session"""
    # step 7
    _undercloud_copy_images()
    # step 6 & 8
    _undercloud_ssh()
