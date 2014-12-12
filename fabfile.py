from fabric.api import env

from instrap import config, host, undercloud  # NOQA

env.user = config.USER
