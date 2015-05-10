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
        """Cost of replacing with clean energy
        12/44 converts from $/C to $/CO2

        Returns:
            :returns: BC(0) * (ratio - 1 + exp(-BC_g(0) * (t-1)) / ratio)
            :rtype: np.ndarray
        """
        return self.params.backstop_2005 * (
            (
                self.params.backstop_ratio - 1 + np.exp(
                    -self.params.backstop_decline * self.params.t0
                )) / self.params.backstop_ratio
        )

    @property
    def population_growth_rate(self):
        """L_g, Growth rate of population.

        Returns:
            :returns: exp(L_g * (t-1) - 1) / exp(L_g * (t-1))
            :rtype: np.ndarray
        """
        return (
            (np.exp(self.params.population_growth * self.params.t0) - 1) /
            (np.exp(self.params.population_growth * self.params.t0))
        )

    @property
    def productivity_growth(self):
        """A_g, Growth rate of total factor productivity.

        Returns:
            :returns: A_g(0) * exp(-Δ_a * (t-1))
            :rtype: np.ndarray
        """
        return self.params.productivity_growth * np.exp(
            -self.params.productivity_decline * 10 * self.params.t0
        )

    def population(self, i, df):
        """L, Population.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: L(0) * (1 - L_g(t)) + (L_g(t) * L_max
            :rtype: float
        """
        return (
            self.params.population_2005 *
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
                -self.params.intensity_decline_rate * 10 * i
            )
        )

    def carbon_intensity(self, i, df):
        """σ, Carbon intensity.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: σ(t-1) / (1 - σ_g(t))
            :rtype: float
        """
        intensity_decline = self.intensity_decline(i, df)
        # df.intensity_decline[i] = intensity_decline
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
            df.backstop[:] = self.backstop
            carbon_intensity = self.params.intensity_2005
            productivity = self.params.productivity
            capital = self.params.capital_2005
            gross_output = self.params.output_2005
            intensity_decline = self.params.intensity_growth
            population = self.params.population_2005

        backstop_growth = (
            df.backstop[i] * carbon_intensity /
            self.params.abatement_exponent
        )

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
        """K(t), Capital, trillions $USD

        Args:
            :param capital: capital in prior time step
            :type i: float
            :param depreciation: depreciation rate
            :type i: float
            :param investment: investment in prior time step
            :type i: float

        Returns:
            :returns: K(t-1) * (1 - δ) + I
            :rtype: float
        """
        return capital * (1 - depreciation) ** 10 + 10 * investment

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
            (population * 1000) ** (1 - output_elasticity)
        )


class Dice2007(ProductivityModel):
    pass


class Dice2010(ProductivityModel):
    def intensity_decline(self, i, df):
        """σ_g, Decline rate of decarbonization.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: σ_g(t-1) * (1 - σ_d1)
            :rtype: float
        """
        return df.intensity_decline[i - 1] * (
            1 - self.params.intensity_decline_rate
        ) ** 10

    @property
    def productivity_growth(self):
        """A_g, Growth rate of total factor productivity.

        Returns:
            :returns: A_g(0) * exp(-Δ_a * (t-1) * exp(-.002 * (t-1))
            :rtype: np.ndarray
        """
        return self.params.productivity_growth * np.exp(
            -self.params.productivity_decline * 10 * self.params.t0 *
        np.exp(-.002 * 10 * self.params.t0))

    def carbon_intensity(self, i, df):
        """σ, Carbon intensity.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: σ(t-1) * (1 - σ_g(t))
            :rtype: float
        """
        intensity_decline = self.intensity_decline(i, df)
        return (
            df.carbon_intensity[i - 1] *
            (1 - df.intensity_decline[i - 1])
        ), intensity_decline

    def population(self, i, df):
        """L, Population.

        Args:
            :param i: current time step
            :type i: int
            :param df: DiceDataMatrix
            :type df: obj

        Returns:
            :returns: L(t-1) * (L_max / L(t-1)) ** L_g
            :rtype: float
        """
        return (
            df.population[i - 1] * (
                self.params.popasym / df.population[i - 1]
            ) ** self.params.population_growth
        )


class DiceBackstop2013(Dice2010):
    """This cass is a hack to make the simpler backstop equations from
    DICE2013 available to the web front-end.
    """
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
            df.backstop[i] = df.backstop[i - 1] * (1 - self.params.backstop_decline)

        else:
            df.backstop[i] = self.params.backstop_2005
            carbon_intensity = self.params.intensity_2005
            productivity = self.params.productivity
            capital = self.params.capital_2005
            gross_output = self.params.output_2005
            intensity_decline = self.params.intensity_growth
            population = self.params.population_2005
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