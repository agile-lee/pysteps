"""
The methods in the extrapolation module implement the following interface:

    extrapolate(precip, velocity, num_timesteps, outval=np.nan, **keywords )

where precip is a (m,n) array with input precipitation field to be advected and
velocity is a (2,m,n) array containing  the x- and y-components of
the m x n advection field.
num_timesteps is an integer specifying the number of time steps to extrapolate.
The optional argument outval specifies the value for pixels advected
from outside the domain.
Optional keyword arguments that are specific to a given extrapolation
method are passed as a dictionary.

The output of each method is an array R_e that includes the time series of
extrapolated fields of shape (num_timesteps, m, n)."""

import numpy as np

from pysteps.extrapolation import semilagrangian


def eulerian_persistence(precip, velocity, num_timesteps, **kwargs):
    """ Eulerian persistence extrapolator """
    del velocity  # Unused by _eulerian_persistence
    return_displacement = kwargs.get("return_displacement", False)

    extrapolated_precip = np.repeat(precip[np.newaxis, :, :, ],
                                    num_timesteps,
                                    axis=0)

    if not return_displacement:
        return extrapolated_precip
    else:
        return extrapolated_precip, np.zeros((2,) + extrapolated_precip.shape)


def _do_nothing(precip, velocity, num_timesteps, **kwargs):
    del precip, velocity, num_timesteps, kwargs  # Unused by _do_nothing
    return None


_extrapolation_methods = dict()
_extrapolation_methods['eulerian'] = eulerian_persistence
_extrapolation_methods['semilagrangian'] = semilagrangian.extrapolate
_extrapolation_methods[None] = _do_nothing


def get_method(name):
    """Return a callable function for the extrapolation method corresponding to
    the given name. The available options are:\n

    +-----------------+--------------------------------------------------------+
    |     Name        |              Description                               |
    +=================+========================================================+
    |  None           | returns None                                           |
    +-----------------+--------------------------------------------------------+
    |  eulerian       | this methods does not apply any advection to the input |
    |                 | precipitation field (Eulerian persistence)             |
    +-------------------+------------------------------------------------------+
    | semilagrangian  | implementation of the semi-Lagrangian method of        |
    |                 | Germann et al. (2002)                                  |
    +-----------------+--------------------------------------------------------+

    """
    if isinstance(name, str):
        name = name.lower()

    try:
        return _extrapolation_methods[name]
    except KeyError:
        raise ValueError("Unknown method {}\n".format(name)
                         + "The available methods are:"
                         + str(list(_extrapolation_methods.keys()))) from None
