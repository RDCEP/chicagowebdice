from __future__ import division
import numpy as np


class DamagesModel(object):
    """
    Subclass default equations for the sake of using alternate
    damages functions.
    ....
    Args
    ----
    prod_frac : float
    """
    def __init__(self, params):
        self.params = params
        self._temp_atmosphere = None
        self._aa = None

    @property
    def participation(self):
        """
        phi, Fraction of emissions in control regime
        ...
        Returns
        -------
        array
        """
        if self.params.treaty:
            p = [self.params.p2050, self.params.p2050, self.params.p2100,
                 self.params.p2150, self.params.pmax]
            return np.concatenate((
                (p[1] + (p[0] - p[1]) * np.exp(np.arange(5) * -.25)),
                (p[2] + (p[1] - p[2]) * np.exp(np.arange(5) * -.25)),
                (p[3] + (p[2] - p[3]) * np.exp(np.arange(5) * -.25)),
                (p[4] + (p[3] - p[4]) * np.exp(np.arange(45) * -.25)),
            ))
        return np.ones(self.params.tmax)

    @property
    def damages_terms(self):
        """
        temp coefficient; pi_2, temp squared coefficient;
        epsilon, damages exponent
        ...
        Returns
        -------
        array
        """
        return np.array([
            self.params.a1,
            self.params.damages_coefficient,
            self.params.damages_exponent
        ])

    def get_production_factor(self, temp_atmosphere):
        """
        Return default fraction of productivity
        """
        return 1.

    def get_model_values(self, i, df):
        """
        Calculate and return damages, output, and consumption
        ...
        Arguments
        ---------
        gross_output : float
        temp_atmosphere : float
        damages_terms : array
        abatement : float
        savings : float
        ...
        Returns
        -------
        array
        """
        if i == 0:
            df.participation = self.participation
        abatement = self.abatement(df.gross_output[i], df.miu[i],
                                   df.backstop_growth[i],
                                   df.participation[i])
        damages = self.damages(df.gross_output[i],
                               df.temp_atmosphere[i], abatement)
        output = self.output(df.gross_output[i], damages, abatement,
                             df.temp_atmosphere[i])
        output_abate = self.output_abate(abatement, df.gross_output[i])
        return [abatement, damages, output, output_abate]

    def abatement(self, gross_output, miu, backstop_growth, participation):
        """
        Lambda, Abatement costs, trillions $USD
        ...
        Returns
        -------
        float
        """
        return np.minimum(
            gross_output,
            gross_output *
            participation ** (1 - self.params.abatement_exponent) *
            backstop_growth * miu ** self.params.abatement_exponent
        )

    def damages(self, gross_output, temp_atmosphere, abatement=None):
        """
        Omega, Damage, trillions $USD
        ...
        Returns
        -------
        float
        """
        return gross_output * (1 - 1 / (
            1 + self.damages_terms[0] * temp_atmosphere +
            self.damages_terms[1] * temp_atmosphere ** self.damages_terms[2]
        ))

    def output(self, gross_output, damages, abatement,
               a_temp_atmosphere=None):
        """
        Net output after abatement and damages, trillions $USD
        ...
        Returns
        -------
        float
        """
        return (
            (gross_output - abatement) * (gross_output - damages)
        ) / gross_output

    def output_abate(self, abatement, gross_output):
        """
        Abatement as a percentage of output
        ...
        Returns
        -------
        array
        """
        return abatement / gross_output * 100


class Dice2007(DamagesModel):
    """
    Standard DICE2007 damages function
    """
    pass


class ExponentialMap(DamagesModel):
    """
    DICE2007 Damages with exponential mapping to output
    NB: This is currently unused.
    """
    def damages(self, gross_output, temp_atmosphere, abatement=None):
        return gross_output * (1 - np.exp(
            -(self.damages_terms[0] * temp_atmosphere +
            self.damages_terms[1] * temp_atmosphere ** self.damages_terms[2])
        ))


class IncommensurableDamages(DamagesModel):
    """
    Weitzman additive damages function
    """
    def __init__(self, params):
        DamagesModel.__init__(self, params)
        self._abatement = 0

    def get_model_values(self, index, df):
        """
        Calculate and return damages, output, and consumption
        ...
        Arguments
        ---------
        gross_output : float
        temp_atmosphere : float
        damages_terms : array
        abatement : float
        savings : float
        ...
        Returns
        -------
        array
        """
        if index == 0:
            df.participation = self.participation
        _go = df.gross_output[index]
        _miu = df.miu[index]
        _bg = df.backstop_growth[index]
        _ta = df.temp_atmosphere[index]
        _part = df.participation[index]
        abatement = self.abatement(_go, _miu, _bg, _part)
        damages = self.damages(_go, _ta, abatement)
        output = self.output(_go, damages, abatement, _ta)
        output_abate = self.output_abate(abatement, _go)
        return [abatement, damages, output, output_abate]

    def output(self, gross_output, damages, abatement, temp_atmosphere=None):
        C25d = 1.4771e-05
        output_no_damages = gross_output - abatement
        consumption_no_damages = (
            output_no_damages - output_no_damages * self.params.savings
        )
        consumption = (
            consumption_no_damages / (
                1 + consumption_no_damages * C25d *
                temp_atmosphere ** self.damages_terms[2]
            )
        )
        return consumption / (1 - self.params.savings)

    def damages(self, gross_output, temp_atmosphere, abatement=None):
        output_no_damages = gross_output - abatement
        output = self.output(gross_output, 0, abatement,
                             temp_atmosphere)
        return output_no_damages - output


class TippingPoint(DamagesModel):
    """
    Weitzman tipping point damages
    """
    def damages(self, gross_output, temp_atmosphere, a_abatement=None):
        return gross_output * (1 - 1 / (
            1 + (temp_atmosphere / 20.46) ** 2 + (
                (temp_atmosphere / 6.081) ** 6.754
            )))


class ProductivityFraction(DamagesModel):
    """
    Wiesbach and Moyer damages as a fraction of productivity
    """
    def damages(self, gross_output, temp_atmosphere, a_abatement=None):
        fD = self.get_production_factor(temp_atmosphere)
        damages_to_prod =  1 / (
            1 + self.damages_terms[0] * temp_atmosphere +
            self.damages_terms[1] * temp_atmosphere ** self.damages_terms[2]
        ) / fD
        return gross_output * (1 - damages_to_prod)

    def get_production_factor(self, temp_atmosphere):
        """
        Calculate fraction of productivity
        ...
        Arguments
        ---------
        damages_terms : array
        temp_atmosphere : float
        ...
        Returns
        -------
        float
        """
        D = 1 - 1 / (
            1 + self.damages_terms[0] * temp_atmosphere +
            self.damages_terms[1] * temp_atmosphere ** self.damages_terms[2]
        )
        return 1 - self.params.prod_frac * D


class Dice2010(DamagesModel):
    pass


class Dice2013(DamagesModel):

    def damages(self, gross_output, temp_atmosphere, abatement=None):
        """
        Omega, Damage, trillions $USD
        ...
        Returns
        -------
        float
        """
        D = self.damages_terms[0] * temp_atmosphere + (
            self.params.damages_multiplier * self.damages_terms[1] *
            temp_atmosphere ** self.damages_terms[2]) + (
            self.params.catastrophic_rate * self.params.catastrophic_gate *
            (temp_atmosphere / self.params.catastrophic_threshold) **
            self.params.catastrophic_exponent
        )
        return gross_output * D / (1 + D ** 10)