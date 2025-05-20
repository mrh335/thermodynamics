# Thermodynamics Package

This package includes various tools for plotting pressure-enthalpy (P-h) diagrams and performing thermodynamic analysis.

## Modules

### `ph_plot_basic`
Basic P-h plot using Matplotlib.

### `ph_plot_v2`
Improved P-h plot version.

### `ph_plot_v3`
Advanced P-h plot with critical and dome adjustments.

### `ph_plot_plotly`
Interactive P-h plot using Plotly.

### `parallel_search`
Parallelized search utility for performance-intensive thermodynamic simulations.

## Installation

```bash
pip install thermodynamics-mrh335
```

## Usage

```python
from thermodynamics import plot_ph_basic
plot_ph_basic()
```

## Testing

```bash
pytest tests/
```
