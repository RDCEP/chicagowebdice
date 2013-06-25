from __future__ import division
import numpy as np


class ProductivityModel(object):
    """
    ProductivityModel base class
    ...
    Properties
    ----------
    population_growth: array
        Population growth factor
    population : array
        Labor or population
    productivity_growth : array
        Growth rate of productivity
    intensity_decline : array
        Rate of carbon decline
    ...
    Methods
    -------
    get_model_values()
    capital()
    gross_output()
    """
    def __init__(self, params):
        self._params = params

    @property
    def backstop(self):
        """
        Cost of replacing clean energy
        ...
        Returns
        -------
        array
        """
        return self._params._backstop_2005 * (
            (
                self._params.backstop_ratio - 1 + np.exp(
                    -self._params.backstop_decline * self._params._t0
                )) / self._params.backstop_ratio
        ) * (12 / 44)

    @property
    def population_growth(self):
        """
        L_g, Population growth factor
        ...
        Returns
        -------
        array
        """
        return (
            (np.exp(self._params._population_growth * self._params._t0) - 1) /
            (np.exp(self._params._population_growth * self._params._t0))
        )

    @property
    def population(self):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            self._params._population_2005 * (1 - self.population_growth) +
            self.population_growth * self._params.popasym
        )

    @property
    def productivity_growth(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array
        """
        return self._params._productivity_growth * np.exp(
            -(self._params.productivity_decline / 100.) * 10 * self._params._t0
        )

    @property
    def intensity_decline(self):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return (
            self._params._intensity_growth * np.exp(
                -(self._params.intensity_decline_rate / 100) * 10 *
                self._params._t0 - self._params._intensity_quadratic * 10 *
                (self._params._t0 ** 2)
            )
        )

    def get_model_values(self, index, data):
        if index > 0:
            carbon_intensity = data.carbon_intensity[index - 1] / (
                1 - self.intensity_decline[index]
            )
            productivity = data.productivity[index - 1] / (
                1 - self.productivity_growth[index - 1])
            capital = self.capital(
                data.capital[index - 1], self._params.depreciation,
                data.investment[index - 1]
            )
        else:
            data.backstop = self.backstop
            data.population = self.population
            carbon_intensity = self._params._intensity_2005
            productivity = self._params._productivity
            capital = self._params._capital_2005
        backstop_growth = (
            data.backstop[index] * carbon_intensity /
            self._params.abatement_exponent
        )
        gross_output = self.gross_output(
            productivity, capital, self._params._output_elasticity,
            data.population[index]
        )
        return (
            carbon_intensity,
            productivity,
            capital,
            backstop_growth,
            gross_output,
        )

    def capital(self, capital, depreciation, investment):
        """
        K(t), Capital, trillions $USD
        ...
        Returns
        -------
        Float
        """
        return capital * (1 - depreciation) ** 10 + 10 * investment

    def gross_output(self, productivity, capital, output_elasticity, population):
        """
        Gross output
        ...
        Returns
        -------
        float
        """
        return (
            productivity * capital ** output_elasticity *
            population ** (1 - output_elasticity)
        )

class DiceProductivity(ProductivityModel):
    pass