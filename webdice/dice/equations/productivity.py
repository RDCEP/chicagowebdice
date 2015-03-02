# -*- coding: utf-8 -*-
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
        """BC, Cost of replacing with clean energy

        Note: 12/44 converts from $/C to $/CO2

        Eq: $BC(0) * [ratio - 1 + exp(-BC_{g}(0) * t] / ratio)$

        Returns:
            :returns: Array of backstop prices
             :rtype: np.ndarray
        """
        return self.params.backstop_init * (
            (
                self.params.backstop_ratio - 1 + np.exp(
                    -self.params.backstop_decline * self.params.t0
                )) / self.params.backstop_ratio
        ) * (12 / 44)

    @property
    def population_growth_rate(self):
        """L_{g}, Growth rate of population.

        Eq: $[exp(L_{g} * t] - 1] / exp(L_{g} * t)$

        Returns:
            :return: Array of population growth rates
             :rtype: np.ndarray
        """
        return (
            (np.exp(self.params.population_growth * self.params.t0) - 1) /
            (np.exp(self.params.population_growth * self.params.t0))
        )

    @property
    def productivity_growth(self):
        """A_{g}, Growth rate of total factor productivity.

        Eq: $A_{g}(0) * exp(-Δ_{a} * t)$

        Returns:
            :return: Array of productivity growth rates
             :rtype: np.ndarray
        """
        return self.params.productivity_growth_init * np.exp(
            -self.params.productivity_decline * self.params.ts * self.params.t0
        )

    def population(self, i, df):
        """L, Population.

        Eq: $L(0) * [1 - L_{g}(t)] + L_{g}(t) * L_{max}

        Args:
            :param i: current time step
             :type i: int
            :param df: DiceDataMatrix
             :type df: obj

        Returns:
            :return: Array of population values
             :rtype: float
        """
        return (
            self.params.population_init *
            (1 - self.population_growth_rate[i]) +
            self.population_growth_rate[i] * self.params.popasym
        )

    def intensity_decline(self, i, df):
        """σ_g, Decline rate of decarbonization.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: σ_g(0) * exp(σ_d1 * t)
            :rtype: float
        """
        return (
            self.params.intensity_growth * np.exp(
                -self.params.intensity_decline_rate * self.params.ts *
                i - self.params.intensity_quadratic * self.params.ts *
                (i ** 2)
            )
        )

    def carbon_intensity(self, i, df):
        """σ, Carbon intensity.

        Eq: $σ(t-1) / [1 - σ_g(t)]$

        Args:
            :param i: current time step
             :type i: int
            :param df: DiceDataMatrix
             :type df: obj

        Returns:
            :return: Carbon intensity at t
             :rtype: float
        """
        intensity_decline = self.intensity_decline(i, df)
        return df.carbon_intensity[i - 1] / (
            1 - intensity_decline
        ), intensity_decline

    def capital(self, capital, depreciation, investment):
        """K(t), Capital, trillions $USD

        Eq: $K(t-1) * (1 - δ) + I$

        Args:
            :param capital: capital in prior time step
             :type i: float
            :param depreciation: depreciation rate
             :type i: float
            :param investment: investment in prior time step
             :type i: float

        Returns:
            :return: Depreciated capital plus investment at t
             :rtype: float
        """
        return capital * (1 - depreciation) ** self.params.ts + self.params.ts * investment

    def gross_output(self, productivity, capital, output_elasticity,
                     population):
        """Gross output, trillions USD

        Args:
            :param productivity: productivity in current time step
            :type i: float
            :param capital: capital in current time step
            :type i: float
            :param output_elasticity: elasticity of output
            :type i: float
            :param population: population in current time step
            :type i: float

        Returns:
            :returns: A(t) * K(t) ^ γ * L ^ (1 - γ)
            :rtype: float
        """
        return (
            productivity * capital ** output_elasticity *
            population ** (1 - output_elasticity)
        )

    def get_model_values(self, i, df):
        """Get values for model variables.

        Args:
            :param i: current time step
             :type i: int
            :param df: Matrix of variables
             :type df: DiceDataMatrix

        Returns:
            :return: Model variables: σ, A, K, BC_{g}, Y, σ_{g}, L
             :rtype: tuple
        """
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
            df.backstop[:] = self.backstop
            carbon_intensity = self.params.intensity_init
            productivity = self.params.productivity
            capital = self.params.capital_init
            gross_output = self.params.output_init
            intensity_decline = self.params.intensity_growth
            population = self.params.population_init

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


class Dice2007(ProductivityModel):
    pass


class Dice2010(ProductivityModel):
    def intensity_decline(self, i, df):
        return df.intensity_decline[i - 1] * (
            1 - self.params.intensity_decline_rate
        ) ** self.params.ts

    @property
    def productivity_growth(self):
        return self.params.productivity_growth_init * np.exp(
            -self.params.productivity_decline * self.params.ts * self.params.t0 *
        np.exp(-.002 * self.params.ts * self.params.t0))

    def carbon_intensity(self, i, df):
        intensity_decline = self.intensity_decline(i, df)
        return (
            df.carbon_intensity[i - 1] *
            (1 - df.intensity_decline[i - 1])
        ), intensity_decline

    def population(self, i, df):
        return (
            df.population[i - 1] * (
                self.params.popasym / df.population[i - 1]
            ) ** self.params.population_growth
        )


class DiceBackstop2013(Dice2010):
    """This cass is a hack to make the simpler backstop equations from
    DICE2013 available to the web front-end.
    """
    @property
    def backstop(self):
        """Cost of replacing with clean energy
        12/44 converts from $/C to $/CO2

        Returns:
            :returns: TKTK
            :rtype: np.ndarray
        """
        return self.params.backstop_init * (
            (1 - self.params.backstop_decline) ** self.params.t0
        ) * (12 / 44)


class Dice2013(Dice2010):
    @property
    def productivity_growth(self):
        """A_g, Growth rate of total factor productivity.

        Returns:
            :returns: A_g(0) * exp(-Δ_a * (t-1))
            :rtype: np.ndarray
        """
        return self.params.productivity_growth_init * np.exp(
            -self.params.productivity_decline * self.params.ts * self.params.t0
        )

    @property
    def backstop(self):
        return self.params.backstop_init * (
            (1 - self.params.backstop_decline) ** self.params.t0
        )

    def carbon_intensity(self, i, df):
        intensity_decline = self.intensity_decline(i, df)
        return (
            df.carbon_intensity[i - 1] *
            np.exp(df.intensity_decline[i - 1] * self.params.ts)
        ), intensity_decline

    def gross_output(self, productivity, capital, output_elasticity,
                     population):
        return (
            productivity * capital ** output_elasticity *
            (population * 1e-3) ** (1 - output_elasticity)
        )