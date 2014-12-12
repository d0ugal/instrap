UNDERCLOUD_REPO = "https://github.com/d0ugal/instack-undercloud.git"
TRIPLEO_REPO = "https://git.openstack.org/openstack/tripleo-incubator"
SOURCERC = "instack-undercloud/instack-sourcerc"

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
