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

    def population(self, i, df):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            self.params._population_2005 *
            (1 - self.population_growth_rate[i]) +
            self.population_growth_rate[i] * self.params.popasym
        )

    def intensity_decline(self, i, df):
        return (
            self.params.intensity_growth * np.exp(
                -self.params.intensity_decline_rate * 10 *
                i - self.params.intensity_quadratic * 10 *
                (i ** 2)
            )
        )

    def carbon_intensity(self, i, df):
        intensity_decline = self.intensity_decline(i, df)
        df.intensity_decline[i] = intensity_decline
        return df.carbon_intensity[i - 1] / (
            1 - intensity_decline
        ), intensity_decline

    def get_model_values(self, i, df):
        if i > 0:
            carbon_intensity, intensity_decline = self.carbon_intensity(i, df)
            productivity = df.productivity[i - 1] / (
                1 - self.productivity_growth[i - 1])
            capital = self.capital(
                df.capital[i - 1], self.params.depreciation,
                df.investment[i - 1]
            )
            population = self.population(i, df)
            gross_output = self.gross_output(
                productivity, capital, self.params.output_elasticity,
                population
            )
        else:
            df.backstop = self.backstop
            carbon_intensity = self.params.intensity_2005
            productivity = self.params.productivity
            capital = self.params.capital_2005
            gross_output = self.params.output_2005
            intensity_decline = self.params.intensity_growth
            population = self.params._population_2005

        backstop_growth = (
            df.backstop[i] * carbon_intensity /
            self.params.abatement_exponent
        ) * (44 / 12)

        return (
            carbon_intensity,
            productivity,
            capital,
            backstop_growth,
            gross_output,
            intensity_decline,
            population,
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
    def intensity_decline(self, i, df):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return df.intensity_decline[i - 1] * (
            1 - (self.params.intensity_decline_rate *
                 np.exp(-self.params.intensity_quadratic * 10 * i)
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

    def carbon_intensity(self, i, df):
        intensity_decline = self.intensity_decline(i, df)
        return intensity_decline, (
            df.carbon_intensity[i - 1] *
            (1 - df.intensity_decline[i - 1])
        )

    def population(self, i, df):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return (
            df.population[i - 1] * (
                self.params.popasym / df.population[i - 1]
            ) ** self.params.population_growth
        )