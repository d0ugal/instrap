from __future__ import print_function

USER = 'root'

SOURCERC = "/usr/libexec/openstack-tripleo/devtest_variables.sh"

IMAGES_SHAS = 'http://file.rdu.redhat.com/~jslagle/tripleo-images-juno-source/SHA256SUMS'  # NOQA

IMAGES = [
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

try:
    from instrap.local_config import *
    print("Local config loaded")
except ImportError:
    pass
