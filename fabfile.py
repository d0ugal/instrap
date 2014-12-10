from __future__ import print_function

from fabric.api import cd, env, settings, sudo

UNDERCLOUD_REPO = "https://github.com/d0ugal/instack-undercloud.git"

TRIPLEO_REPO = "https://git.openstack.org/openstack/tripleo-incubator"
SOURCERC = "instack-undercloud/instack-sourcerc"

env.user = 'root'

IMAGES = [
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/SHA256SUMS',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/deploy-ramdisk-ironic.initramfs',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/deploy-ramdisk-ironic.kernel',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/discovery-ramdisk.initramfs',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/discovery-ramdisk.kernel',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/fedora-user.qcow2',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.initrd',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.qcow2',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-cinder-volume.vmlinuz',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.initrd',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.qcow2',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-compute.vmlinuz',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.initrd',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.qcow2',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-control.vmlinuz',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.initrd',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.qcow2',
    'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/overcloud-swift-storage.vmlinuz ',
]


def _tmux_create(name, kill=True):
    if kill:
        sudo("tmux kill-session -t {}".format(name),
             user="stack", warn_only=True)
    sudo("tmux new -d -s {}".format(name), user="stack", )


def _tmux(session, command):
    send = "tmux send -t {0}.0 '{1}' ENTER".format(session, command)
    return sudo(send, user="stack")


def _host_setup():
    # Step 0
    sudo('yum upgrade -qy')
    sudo('yum install -qy git tmux')


def _host_download_images():
    # step 7 prep (Start early)
    sudo("mkdir -p ~/images", user='stack')
    _tmux_create("image-download")
    _tmux('image-download', 'cd ~/images')
    for f in IMAGES:
        _tmux('image-download', "wget {}".format(f))


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
    _tmux_create("tripleo-setup")
    _tmux('tripleo-setup', 'cd ~/instack')
    _tmux('tripleo-setup', "git clone {}".format(UNDERCLOUD_REPO))
    _tmux('tripleo-setup', "git clone {}".format(TRIPLEO_REPO))

    _tmux('tripleo-setup', "source {}".format(SOURCERC))
    _tmux('tripleo-setup', "tripleo install-dependencies")
    _tmux('tripleo-setup', "tripleo set-usergroup-membership")


def _undercloud_ip():

    with cd("~/instack"):
        mac = sudo("source {} && tripleo get-vm-mac instack".format(SOURCERC), user='stack')

    ip = sudo("cat /var/lib/libvirt/dnsmasq/default.leases | grep {} | awk '{{print $3;}}'".format(mac), user='stack')
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
    sudo("virsh list --all", user="stack")


def host_tmux_list():
    """Display the active tmux sessions"""
    sudo("tmux ls", user="stack")


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

    names = ['baremetal_{}'.format(i) for i in range(4)]
    names.append('instack')

    sudo("virsh list --all", user="stack")

    for name in names:
        sudo("virsh destroy {}".format(name), user="stack", warn_only=True)
        sudo("virsh undefine {}".format(name), user="stack")


def _undercloud_ssh():
    # step 6

    ip = _undercloud_ip()

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

    ip = _undercloud_ip()

    sudo("scp ~/images/* stack@{}:".format(ip), user='stack')


def undercloud_setup():
    """Copy the images to the undercloud and start a SSH session"""
    # step 7
    _undercloud_copy_images()
    # step 6 & 8
    _undercloud_ssh()
