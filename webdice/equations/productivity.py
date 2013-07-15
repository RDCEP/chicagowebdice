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

    def population(self, data, index):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            self._params._population_2005 * (1 - data.population_growth[index]) +
            data.population_growth[index] * self._params.popasym
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
            -self._params.productivity_decline * 10 * self._params._t0
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
                -self._params.intensity_decline_rate * 10 *
                self._params._t0 - self._params._intensity_quadratic * 10 *
                (self._params._t0 ** 2)
            )
        )

    def carbon_intensity(self, index, data):
        return data.carbon_intensity[index - 1] / (
            1 - self.intensity_decline[index]
        )

    def get_model_values(self, index, data):
        if index > 0:
            carbon_intensity = self.carbon_intensity(index, data)
            productivity = data.productivity[index - 1] / (
                1 - self.productivity_growth[index - 1])
            capital = self.capital(
                data.capital[index - 1], self._params.depreciation,
                data.investment[index - 1]
            )
            data.population[index] = self.population(data, index)
        else:
            data.backstop = self.backstop
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

    def gross_output(self, productivity, capital, output_elasticity,
                     population):
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


class Dice2007(ProductivityModel):
    pass


class Dice2010(ProductivityModel):
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
                -self._params.intensity_decline_rate * 10 *
                self._params._t0 - self._params._intensity_quadratic * 10 *
                (self._params._t0 ** 2)
            )
        )

    def carbon_intensity(self, index, data):
        intensity_decline = (
            data.intensity_decline[index - 1] * (1 - (
                self._params.intensity_decline_rate * np.exp(
                    -self._params._intensity_quadratic * 10 * index
                )
            )) ** 10
        )
        data.intensity_decline[index] = intensity_decline
        return data.carbon_intensity[index - 1] * (1 - intensity_decline)

    def population(self, data, index):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            data.population[index - 1] *
            (self._params.popasym / data.population[index - 1]) ** .485
        )