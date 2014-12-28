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
        return self.params.backstop_init * (
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
        return self.params.productivity_growth_init * np.exp(
            -self.params.productivity_decline * self.params.ts * self.params.t0
        )

    def population(self, population_growth_rate, population_prev):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        p = self.params.population_init
        pa = self.params.popasym
        return ne.evaluate('p * (1 - population_growth_rate) + population_growth_rate * pa')

    def intensity_decline(self, i, intensity_decline_prev):
        ig = self.params.intensity_growth
        id = self.params.intensity_decline_rate
        iq = self.params.intensity_quadratic
        ts = self.params.ts
        return ne.evaluate('ig * exp(-id * ts * i - iq * ts * (i ** 2))')

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
            # df.backstop[:] = self.backstop
            carbon_intensity = self.params.intensity_init
            productivity = self.params.productivity
            capital = self.params.capital_init
            gross_output = self.params.output_init
            population = self.params.population_init

        bs = self.backstop[i]
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
        ts = self.params.ts
        return ne.evaluate('capital * (1 - depreciation) ** ts + ts * investment')

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
        id = self.params.intensity_decline_rate
        iq = self.params.intensity_quadratic
        ts = self.params.ts
        return ne.evaluate('intensity_decline_prev * (1 - (id * exp(-iq * ts * i))) ** ts')

    def carbon_intensity(self, carbon_intensity_prev, intensity_decline,
                         intensity_decline_prev):
        return ne.evaluate('carbon_intensity_prev * (1 - intensity_decline_prev)')

    @property
    def productivity_growth(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array
        """
        return self.params.productivity_growth_init * np.exp(
            -self.params.productivity_decline * self.params.ts * self.params.t0 *
        np.exp(-.002 * self.params.ts * self.params.t0))

    def population(self, population_growth_rate, population_prev):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        p = self.params.population_init
        pa = self.params.popasym
        return ne.evaluate('population_prev * (pa / population_prev) ** population_growth_rate')


class DiceBackstop2013(Dice2010):

    @property
    def backstop(self):
        """
        Cost of replacing clean energy
        ...
        Returns
        -------
        array
        """
        return self.params.backstop_init * (
            (1 - self.params.backstop_decline) ** self.params.t0
        ) * (12 / 44)


class Dice2013(Dice2010):

    @property
    def backstop(self):
        """
        Cost of replacing clean energy
        ...
        Returns
        -------
        array
        """
        return self.params.backstop_init * (
            (1 - self.params.backstop_decline) ** self.params.t0
        )

    def carbon_intensity(self, carbon_intensity_prev, intensity_decline,
                         intensity_decline_prev):
        ts = self.params.ts
        return ne.evaluate('carbon_intensity_prev * exp(intensity_decline_prev * ts)')

