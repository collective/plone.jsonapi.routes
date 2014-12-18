# -*- coding: utf-8 -*-

import os
import json
import time
import glob
import string
import hashlib
import textwrap

# Fabric imports
from fabric.api import env
from fabric.api import lcd
from fabric.api import task
from fabric.api import local
from fabric.colors import red
from fabric.colors import green
from fabric.colors import yellow


if not os.path.exists("fabfile.py"):
    raise RuntimeError("Must be run in the buildout directory")


@task
def make_docs():
    with lcd("docs"):
        local("make html")
        local("open _build/html/index.html")


# vim: set ft=python ts=4 sw=4 expandtab :
