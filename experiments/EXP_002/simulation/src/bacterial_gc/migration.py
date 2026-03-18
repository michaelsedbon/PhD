"""
Migration — robotic DZ ↔ LZ transfers.

Models the pipetting robot transferring bacteria between compartments.
"""

import jax
import jax.numpy as jnp

from .state import BacterialState, DZ, LZ


def transfer_dz_to_lz(
    state: BacterialState,
    fraction: float,
    rng_key: jnp.ndarray,
) -> BacterialState:
    """Transfer a random fraction of DZ bacteria to LZ.

    Models the robot picking up `fraction` of the DZ well
    and pipetting it into the LZ well (selection chamber).
    """
    dz_mask = state.alive & (state.compartment == DZ)
    dz_indices = jnp.where(dz_mask)[0]
    n_dz = dz_indices.shape[0]

    n_transfer = max(1, int(n_dz * fraction))
    n_transfer = min(n_transfer, n_dz)

    # Random sample without replacement
    chosen = jax.random.choice(
        rng_key, dz_indices, shape=(n_transfer,), replace=False,
    )

    # Update compartment
    new_compartment = state.compartment.at[chosen].set(LZ)

    return state._replace(compartment=new_compartment)


def transfer_lz_to_dz(state: BacterialState) -> BacterialState:
    """Transfer all surviving LZ bacteria back to DZ.

    After selection, all survivors return to the DZ well
    for the next growth round.
    """
    lz_alive = state.alive & (state.compartment == LZ)
    new_compartment = jnp.where(lz_alive, DZ, state.compartment)

    return state._replace(compartment=new_compartment)
