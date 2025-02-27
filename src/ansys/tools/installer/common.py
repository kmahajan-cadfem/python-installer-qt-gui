"""Common module for Ansys Python Manager."""

from functools import wraps
import json
import logging
import sys
from threading import Thread
import traceback
from urllib import request

from pkg_resources import parse_version

LOG = logging.getLogger(__name__)
LOG.setLevel("DEBUG")


def threaded(fn):
    """Call a function using a thread."""

    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


def protected(fn):
    """Capture any exceptions from a function and pass it to the GUI.

    Attempts to display the error using ``show_error`` and protects
    the main application from segmentation faulting.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return fn(*args, **kwargs)
        except Exception as exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            LOG.error(exception)
            if hasattr(self, "exceptions"):
                self._exceptions.append(exception)

            # Visual error handing
            if hasattr(self, "parent"):
                if hasattr(self.parent, "show_error"):
                    self.parent.show_error(exception)
                    return wrapper

            if hasattr(self, "_show_error"):
                self._show_error(exception)

    return wrapper


def get_pkg_versions(pkg_name):
    """
    Get the available versions of a package.

    Parameters
    ----------
    pkg_name : str
        Name of the package for which to fetch the available versions.

    Returns
    -------
    list
        A sorted list of available package versions, in descending order.

    Notes
    -----
    This function fetches the package information from the PyPI API
    and filters the package versions based on specific criteria
    for the 'pyansys' package.

    Examples
    --------
    >>> get_pkg_versions("numpy")
    ['1.22.1', '1.22.0', '1.21.2', ...]
    """
    url = f"https://pypi.python.org/pypi/{pkg_name}/json"
    releases = json.loads(request.urlopen(url).read())["releases"]
    all_versions = sorted(releases, key=parse_version, reverse=True)
    if pkg_name == "pyansys":
        all_versions = [x for x in all_versions if int(x.split(".")[0]) > 0]
    return all_versions
