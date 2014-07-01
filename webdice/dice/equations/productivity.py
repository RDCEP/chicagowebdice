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
        self.params = params

    @property
    def backstop(self):
        """
        Cost of replacing clean energy
        ...
        Returns
        -------
        array
        """
        return self.params.backstop_2005 * (
            (
                self.params.backstop_ratio - 1 + np.exp(
                    -self.params.backstop_decline * self.params.t0
                )) / self.params.backstop_ratio
        ) * (12 / 44)

    @property
    def population_growth_rate(self):
        return (
            (np.exp(self.params.population_growth * self.params.t0) - 1) /
            (np.exp(self.params.population_growth * self.params.t0))
        )

    def population(self, index, data):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            #self.params.population_2005 * (1 - data.population_growth[index]) +
            #data.population_growth[index] * self.params.popasym
            self.params.population_2005 * (1 - self.population_growth_rate[index]) +
            self.population_growth_rate[index] * self.params.popasym
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
        return self.params.productivity_growth * np.exp(
            -self.params.productivity_decline * 10 * self.params.t0
        )

    def intensity_decline(self, index, data):
        return (
            self.params.intensity_growth * np.exp(
                -self.params.intensity_decline_rate * 10 *
                index - self.params.intensity_quadratic * 10 *
                (index ** 2)
            )
        )

    def carbon_intensity(self, index, data):
        intensity_decline = self.intensity_decline(index, data)
        data.intensity_decline[index] = intensity_decline
        return data.carbon_intensity[index - 1] / (
            # 1 - data.intensity_decline[index]
            1 - intensity_decline
        )

    def get_model_values(self, index, data):
        if index > 0:
            carbon_intensity = self.carbon_intensity(index, data)
            productivity = data.productivity[index - 1] / (
                1 - self.productivity_growth[index - 1])
            capital = self.capital(
                data.capital[index - 1], self.params.depreciation,
                data.investment[index - 1]
            )
            data.population[index] = self.population(index, data)
            gross_output = self.gross_output(
                productivity, capital, self.params.output_elasticity,
                data.population[index]
            )
        else:
            data.backstop = self.backstop
            carbon_intensity = self.params.intensity_2005
            productivity = self.params.productivity
            capital = self.params.capital_2005
            gross_output = self.params.output_2005
        backstop_growth = (
            data.backstop[index] * carbon_intensity /
            self.params.abatement_exponent
        ) * (44 / 12)


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
    def intensity_decline(self, index, data):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return data.intensity_decline[index - 1] * (
            1 - (self.params.intensity_decline_rate *
                 np.exp(-self.params.intensity_quadratic * 10 * index)
            )
        ) ** 10

    @property
    def productivity_growth(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array
        """
        return self.params.productivity_growth * np.exp(
            -self.params.productivity_decline * 10 * self.params.t0 *
        np.exp(-.002 * 10 * self.params.t0))

    def carbon_intensity(self, index, data):
        data.intensity_decline[index] = self.intensity_decline(index, data)
        return (
            data.carbon_intensity[index - 1] *
            (1 - data.intensity_decline[index - 1])
        )

    def population(self, index, data):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            data.population[index - 1] * (
                self.params.popasym / data.population[index - 1]
            ) ** self.params.population_growth
        )