"""
Core operations on Tucker tensors.
"""

from .base import unfold, tensor_to_vec
from .tenalg import multi_mode_dot
from .tenalg import kronecker
from . import backend as tl

# Author: Jean Kossaifi <jean.kossaifi+tensors@gmail.com>

# License: BSD 3 clause

def _validate_tucker_tensor(tucker_tensor):
    core, factors = tucker_tensor
    
    if len(factors) < 2:
        raise ValueError('A Tucker tensor should be composed of at least two factors and a core.'
                         'However, {} factor was given.'.format(len(factors)))

    if len(factors) != tl.ndim(core):
        raise ValueError('Tucker decompositions should have one factor per more of the core tensor.'
                         'However, core has {} modes but {} factors have been provided'.format(
                         tl.ndim(core), len(factors)))

    shape = []
    rank = []
    for i, factor in enumerate(factors):
        current_shape, current_rank = tl.shape(factor)
        if current_rank != tl.shape(core)[i]:
            raise ValueError('Factor `n` of Tucker decomposition should verify:\n'
                             'factors[n].shape[1] = core.shape[n].'
                             'However, factors[{0}].shape[1]={1} but core.shape[{0}]={2}.'.format(
                                 i, tl.shape(factor)[1], tl.shape(core)[i]))
        shape.append(current_shape)
        rank.append(current_rank)

    return tuple(shape), tuple(rank)

def tucker_to_tensor(core, factors, skip_factor=None, transpose_factors=False):
    """Converts the Tucker tensor into a full tensor

    Parameters
    ----------
    core : ndarray
       core tensor
    factors : ndarray list
       list of matrices of shape ``(s_i, core.shape[i])``
    skip_factor : None or int, optional, default is None
        if not None, index of a matrix to skip
        Note that in any case, `modes`, if provided, should have a lengh of ``tensor.ndim``
    transpose_factors : bool, optional, default is False
        if True, the matrices or vectors in in the list are transposed

    Returns
    -------
    2D-array
       full tensor of shape ``(factors[0].shape[0], ..., factors[-1].shape[0])``
    """
    return multi_mode_dot(core, factors, skip=skip_factor, transpose=transpose_factors)


def tucker_to_unfolded(core, factors, mode=0, skip_factor=None, transpose_factors=False):
    """Converts the Tucker decomposition into an unfolded tensor (i.e. a matrix)

    Parameters
    ----------
    core : ndarray
        core tensor
    factors : ndarray list
        list of matrices
    mode : None or int list, optional, default is None
    skip_factor : None or int, optional, default is None
        if not None, index of a matrix to skip
        Note that in any case, `modes`, if provided, should have a lengh of ``tensor.ndim``
    transpose_factors : bool, optional, default is False
        if True, the matrices or vectors in in the list are transposed

    Returns
    -------
    2D-array
        unfolded tensor
    """
    return unfold(tucker_to_tensor(core, factors, skip_factor=skip_factor, transpose_factors=transpose_factors), mode)


def tucker_to_vec(core, factors, skip_factor=None, transpose_factors=False):
    """Converts a Tucker decomposition into a vectorised tensor

    Parameters
    ----------
    core : ndarray
        core tensor
    factors : ndarray list
        list of factor matrices
    skip_factor : None or int, optional, default is None
        if not None, index of a matrix to skip
        Note that in any case, `modes`, if provided, should have a lengh of ``tensor.ndim``
    transpose_factors : bool, optional, default is False
        if True, the matrices or vectors in in the list are transposed

    Returns
    -------
    1D-array
        vectorised tensor

    Notes
    -----
    Mathematically equivalent but much slower,
    you can obtain the same result using:

    >>> def tucker_to_vec(core, factors):
    ...     return kronecker(factors).dot(tensor_to_vec(core))
    """
    return tensor_to_vec(tucker_to_tensor(core, factors, skip_factor=skip_factor, transpose_factors=transpose_factors))

