# -*- coding: utf-8 -*-

import os
import re
import json
import datetime
import fileinput
import subprocess
import pkg_resources
from os.path import join as j

# Fabric imports
from fabric.api import env
from fabric.api import lcd
from fabric.api import task
from fabric.api import local
from fabric.colors import yellow
from fabric.colors import green
from fabric.tasks import execute

# -----------------------------------------------------------------------------
# CUSTOMER CUSTOM
# -----------------------------------------------------------------------------

REQUIREMENTS = "".split()
ENVIRONMENT = "HOME".split()
VERSION_PACKAGES = "plone.jsonapi.routes".split()


# -----------------------------------------------------------------------------
# FABRIC BOOTSTRAP
# -----------------------------------------------------------------------------

def cmd_exists(cmd):
    """ check if the command exists
    """
    return subprocess.call("type " + cmd,
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE) == 0


# load the package distribution info into the environment
if not os.path.exists("package.json"):
    raise RuntimeError("No package.json file found in %s" % os.getcwd())


# check requirements
for req in REQUIREMENTS:
    if not cmd_exists(req):
        raise RuntimeError("Requirement `%s` not found in PATH" % req)


# check enviornment variables
for req in ENVIRONMENT:
    if req not in os.environ:
        raise RuntimeError("Environment Variable `%s` not set" % req)


# load the json config into the fabric environment
env.package = json.loads(file("package.json", "r").read())


# -----------------------------------------------------------------------------
# HELPER
# -----------------------------------------------------------------------------

def get_section(name="main"):
    """ returns the value of the section or an empty dict
    """
    return env.package.get(name, {})


def get_option(name, section="main", default=None):
    """ returns the value of the option
    """
    return get_section(section).get(name, default)


def get_customer():
    """ returns the customer name
    """
    return get_option("customer")


def get_packages():
    """ returns the packages
    """
    return get_option("packages", default=[])


def get_src_dir():
    """ returns the absolute path to the src directory
    """
    path = get_option("src_dir")
    return j(os.getcwd(), path)


def get_dist_dir():
    """ returns the absolute path to the dist directory
    """
    path = get_option("dist_dir")
    return j(os.getcwd(), path)


def get_docs_dir():
    """ returns the absolute path to the docs directory
    """
    path = get_option("docs_dir")
    return j(os.getcwd(), path)


def get_package_dir(package):
    """ returns the absolute path to the python package
    """
    src = get_src_dir()
    path = j(os.getcwd(), src, package)
    if os.path.exists(path):
        return path
    # different layout -- we are already inside the package
    return src


def get_distribution(package):
    """ get the pkg_resources distribution
    """
    try:
        return pkg_resources.get_distribution(package)
    except pkg_resources.DistributionNotFound:
        # setup pkg_resources to find the distribution
        pkg_resources.working_set.add_entry(get_package_dir(package))
        return pkg_resources.get_distribution(package)


def get_version(package):
    """ return the (stripped) version of the given package
    """
    dist = get_distribution(package)
    return dist.version.strip()


def get_version_file(package):
    """ return the version file of package or None
    """
    package_dir = get_package_dir(package)
    subdir = package.split(".")
    subdir.append("version.py")
    return j(package_dir, *subdir)


def write_version_info(package):
    """ updates the build and date of the version module

    The version.py must contain the version in the following format:
        __date__ = "2015-07-09"
        __build__ = 4711
        __version__ = 42
    """

    f = get_version_file(package)
    if not os.path.exists(f):
        raise RuntimeError("File '%s' does not exist." % f)

    for line in fileinput.input(f, inplace=1):
        if re.findall("__build__.*=", line):
            build = int(line.split("=")[1])
            line = "__build__ = %d" % (build + 1)
        elif re.findall("__date__.*=", line):
            now = datetime.datetime.now().strftime("%Y-%m-%d")
            line = "__date__ = '%s'" % now
        print line.strip("\n")


def get_full_version(package):
    """ returns the verion from the verion file
    """
    vf = get_version_file(package)
    out = {}
    lines = file(vf).readlines()
    for l in lines:
        if "=" in l and l.split("=")[0].strip() in \
           ("__build__", "__date__", "__version__"):
            name, value = l.split("=")
            name = name.strip(" _\n\r")
            value = value.strip(' "\'\n\r')
            # handle version method call gracefully
            out[name] = value.replace("version()", get_version(package))
    return out


# -----------------------------------------------------------------------------
# PUBLIC API
# -----------------------------------------------------------------------------

@task
def reload():
    execute(bump_version)
    local("wget --delete-after http://admin:admin@localhost:8080/@@reload?action=code")
    print green("RELOADED CODE")


@task
def make_docs():
    with lcd("docs"):
        local("make html")


@task
def preview_docs():
    with lcd("docs"):
        local("open _build/html/index.html")


@task
def bump_version():
    """ Bump up the version number
    """
    for package in VERSION_PACKAGES:
        version_file = get_version_file(package)
        print yellow("bumping version ...")
        write_version_info(package)
        print green("adding file '%s' to next commit." % version_file)
        local("git add " + version_file)
        print green(get_full_version(package))


@task
def versions():
    """ print the versions of the listed packages
    """
    for package in get_packages():
        dist = get_distribution(package)
        print green(
            "{} -> {}".format(
                package, dist.version.strip()))


@task
def build():
    """ Build all listed packages
    """
    # build all package
    for package in get_packages():
        print yellow("Building Package '%s'" % package)

        # build the package
        local("python setup.py sdist bdist_egg")
        print green("Finished Package '%s'" % package)
