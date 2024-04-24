# collect
python package to collect nuclear data inputs

## installation

move into the `collect` directory and run

```bash
pip install .
```

to install the package

## RIPL Discrete Levels

to collect the discrete levels in the RIPL database, use the  `collect.ripl.DiscreteLevel` object, with the isotope mass number `A` and either `Z` or the chemical symbol `X`:

```python
import collect

levels = collect.ripl.DiscreteLevels(Z=26,A=56)
```

or 

```python
import collect

levels = collect.ripl.DiscreteLevels(X='Fe',A=56)
```

The `DiscreteLevels` object has some basic information about the isotope:

- `A` - mass number
- `Z` - charge number
- `X` - chemical symbol
- `symbol` - isotope symbol, `AAAXX`
- `num_levels` - number of levels
- `num_gammas` - total number of gammas in the level scheme
- `num_complete` - number of levels in the RIPL complete level scheme
- `Sn` - neutron separation energy in MeV
- `levels` - list of `Level` objects

The `Level` objects have information about each level:

- `index` - Index of the level
- `energy` - Energy of the level in MeV
- `spin` - Spin of the level
- `parity` - Parity of the level (-1 or 1)
- `half_life` - half-live of the level in seconds
- `num_transitions` - number of transitions from this level
- `transitions` -The transitions from this level, a list of `Transition` objects

The `Transition` objects have information about each transition from the level:

- `initial_index` - Index of the initial level
- `final_index` - Index of the final level
- `energy` - Energy of the transition in MeV
- `probability` - Probability that the initial level will decay by this transition
- `gamma_probability` - Probability that the intial level will decay by this transition, and by emission of a gamma (not internal conversion)