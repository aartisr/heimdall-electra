# Hyperbolic TDOA Kinematic Multilateration

**Canonical Production Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)  
**Principal Investigator & Author:** Aarti S. Ravikumar ([@aartisr](https://github.com/aartisr))  
**Repository:** [https://github.com/aartisr/heimdall-electra](https://github.com/aartisr/heimdall-electra)  

---

## 1. Multi-Station Time-Difference-of-Arrival (TDOA) Architecture

To determine the 3D position $\mathbf{x} = [x, y, z]^T$ and orbital velocity of a non-cooperative orbital body without transmitting active radar pulses, HEIMDALL ELECTRA utilizes a distributed terrestrial receiver network:

Let $\mathbf{s}_i = [x_i, y_i, z_i]^T$ denote the known spatial coordinates of ground station $i \in \{1, 2, \dots, N\}$.

The slant range from station $i$ to the object is:

$$R_i(\mathbf{x}) = \|\mathbf{x} - \mathbf{s}_i\|_2 = \sqrt{(x - x_i)^2 + (y - y_i)^2 + (z - z_i)^2}$$

---

## 2. Hyperbolic Range Difference Equations

Using Station 1 as the reference receiver, the Time Difference of Arrival $\tau_{i1} = t_i - t_1$ establishes a hyperboloid of revolution:

$$\Delta R_{i1}(\mathbf{x}) = R_i(\mathbf{x}) - R_1(\mathbf{x}) = c \cdot \tau_{i1} + \epsilon_i$$

where $c = 2.99792458 \times 10^8\text{ m/s}$ and $\epsilon_i$ represents synthetic clock jitter noise ($\sigma_t < 1\text{ ns}$ with rubidium synchronization).

---

## 3. Gauss-Newton Non-Linear Least Squares (NLLS) Solver

The position $\mathbf{x}$ is resolved by minimizing the weighted sum of squared residuals:

$$\mathcal{L}(\mathbf{x}) = \sum_{i=2}^N \frac{1}{\sigma_i^2} \left[ \|\mathbf{x} - \mathbf{s}_i\|_2 - \|\mathbf{x} - \mathbf{s}_1\|_2 - c \tau_{i1} \right]^2$$

The Gauss-Newton iterative update step is given by:

$$\mathbf{x}^{(k+1)} = \mathbf{x}^{(k)} + \left(\mathbf{J}^T \mathbf{W} \mathbf{J}\right)^{-1} \mathbf{J}^T \mathbf{W} \mathbf{r}\left(\mathbf{x}^{(k)}\right)$$

where:
- $\mathbf{J}$ is the Jacobian matrix of partial derivatives $\frac{\partial (R_i - R_1)}{\partial \mathbf{x}}$:
  $$J_{i, j} = \frac{x_j - s_{i, j}}{R_i} - \frac{x_j - s_{1, j}}{R_1}$$
- $\mathbf{W} = \text{diag}(\sigma_2^{-2}, \dots, \sigma_N^{-2})$ is the inverse noise covariance matrix.
- $\mathbf{r}(\mathbf{x}) = \left[ c\tau_{21} - \Delta R_{21}(\mathbf{x}), \dots, c\tau_{N1} - \Delta R_{N1}(\mathbf{x}) \right]^T$ is the residual vector.

---

## 4. Geometric Dilution of Precision (GDOP)

The geometric arrangement of ground stations determines solution precision:

$$\text{GDOP} = \sqrt{\text{Trace}\left((\mathbf{J}^T \mathbf{J})^{-1}\right)}$$

For the reference European/Arctic baseline array (Boulmer, Kiruna, Svalbard, Woomera), the achieved GDOP is **$1.48$**, ensuring sub-meter kinematic position convergence within 5 iterations.

---

## Backlinks & Exploration
* **Interactive Live Suite:** [https://nasa.ai-aarti.com](https://nasa.ai-aarti.com)
* **Wiki Home:** [Home.md](Home.md)
* **Plasma Wake Physics:** [Wiki_Plasma_Wake_Physics.md](Wiki_Plasma_Wake_Physics.md)
* **Conjunction Assessment:** [Wiki_Conjunction_Risk.md](Wiki_Conjunction_Risk.md)
