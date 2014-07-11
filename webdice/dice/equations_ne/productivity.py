from __future__ import division
import numpy as np
import numexpr as ne


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

    def population(self, population_growth_rate, population_prev):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        p = self.params._population_2005
        pa = self.params.popasym
        return ne.evaluate('p * (1 - population_growth_rate) + population_growth_rate * pa')

    def intensity_decline(self, i, intensity_decline_prev):
        ig = self.params.intensity_growth
        id = self.params.intensity_decline_rate
        iq = self.params.intensity_quadratic
        return ne.evaluate('ig * exp(-id * 10 * i - iq * 10 * (i ** 2))')

    def carbon_intensity(self, carbon_intensity_prev, intensity_decline,
                         intensity_decline_prev):
        return ne.evaluate('carbon_intensity_prev / (1 - intensity_decline)')

    def get_model_values(self, i, df):
        if i > 0:
            ii = i - 1
            idp = df.intensity_decline[ii]
            intensity_decline = self.intensity_decline(i, idp)
            carbon_intensity = self.carbon_intensity(
                df.carbon_intensity[ii], intensity_decline,
                idp)
            pg = self.productivity_growth[ii]
            p = df.productivity[ii]
            productivity = ne.evaluate('p / (1 - pg)')
            capital = self.capital(
                df.capital[ii], self.params.depreciation,
                df.investment[ii]
            )
            population = self.population(
                self.population_growth_rate[i], df.population[ii])
            gross_output = self.gross_output(
                productivity, capital, self.params.output_elasticity,
                population
            )
        else:
            intensity_decline = self.params.intensity_growth
            df.backstop = self.backstop
            carbon_intensity = self.params.intensity_2005
            productivity = self.params.productivity
            capital = self.params.capital_2005
            gross_output = self.params.output_2005
            population = self.params.population_2005

        bs = df.backstop[i]
        ae = self.params.abatement_exponent
        backstop_growth = ne.evaluate('(bs * carbon_intensity / ae) * (44 / 12)')

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
        return ne.evaluate('capital * (1 - depreciation) ** 10 + 10 * investment')

    def gross_output(self, productivity, capital, output_elasticity,
                     population):
        """
        Gross output
        ...
        Returns
        -------
        float
        """
        return ne.evaluate('productivity * capital ** output_elasticity * population ** (1 - output_elasticity)')


class Dice2007(ProductivityModel):
    pass


class Dice2010(ProductivityModel):
    def intensity_decline(self, i, intensity_decline_prev):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return intensity_decline_prev * (
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

    def carbon_intensity(self, carbon_intensity_prev, intensity_decline,
                         intensity_decline_prev):
        return (
            carbon_intensity_prev *
            (1 - intensity_decline_prev)
        )

    def population(self, population_growth_rate, population_prev):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        pg = self.params.population_growth
        pa = self.params.popasym
        return (
            population_prev * (
                pa / population_prev
            ) ** pg
        )