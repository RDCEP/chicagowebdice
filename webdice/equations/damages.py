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
        self._params = params

    @property
    def participation(self):
        """
        phi, Fraction of emissions in control regime
        ...
        Returns
        -------
        array
        """
        if not self._params._treaty:
            return np.concatenate((
                np.linspace(
                    self._params._participation_2005, self._params._participation_2005, 1
                ),
                self._params._participation_2205 + (
                    self._params._participation_2015 - self._params._participation_2205
                ) * np.exp(
                    -self._params._participation_decline * np.arange(23)
                ),
                np.linspace(
                    self._params._participation_2205, self._params._participation_2205, 36
                ),
            ))
        p = [self._params.p2050, self._params.p2050, self._params.p2100, self._params.p2150, self._params._pmax]
        return np.concatenate((
            (p[1] + (p[0] - p[1]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[2] + (p[1] - p[2]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[3] + (p[2] - p[3]) * np.exp(np.arange(5) * -.25)) / 100.,
            (p[4] + (p[3] - p[4]) * np.exp(np.arange(45) * -.25)) / 100.,
        ))

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
        return np.array(
            [self._params._a1, self._params._damages_coefficient, self._params.damages_exponent]
        )

    def get_production_factor(self, temp_atmosphere):
        """
        Return default fraction of productivity
        """
        return 1.

    def abatement(self, gross_output, miu, backstop_growth, abatement_exponent,
                  participation):
        """
        Lambda, Abatement costs, trillions $USD
        ...
        Returns
        -------
        float
        """
        return (
            gross_output * participation ** (1 - abatement_exponent) *
            backstop_growth * miu ** abatement_exponent
        )

    def damages(self, gross_output, temp_atmosphere, a_abatement=None, a_savings=None):
        """
        Omega, Damage, trillions $USD
        ...
        Returns
        -------
        float
        """
        return gross_output * (1 - 1 / (
            1 + self._params._a1 * temp_atmosphere + self._params._damages_coefficient *
            temp_atmosphere ** self._params.damages_exponent
        ))

    def output(self, gross_output, damages, abatement, a_savings=None,
               a_temp_atmosphere=None, a_aa=None):
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

    def consumption(self, output, savings, a_gross_output=None,
                    a_abatement=None, a_temp_atmosphere=None, a_aa=None):
        """
        C, Consumption, trillions $USD
        ...
        Returns
        -------
        float
        """
        return output * (1.0 - savings)

    def output_abate(self, abatement, gross_output):
        """
        Abatement as a percentage of output
        ...
        Returns
        -------
        array
        """
        return abatement / gross_output * 100

    def get_model_values(self, index, data):
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
            data.participation = self.participation
        abatement = self.abatement(
            data.gross_output[index], data.miu[index],
            data.backstop_growth[index], self._params.abatement_exponent,
            data.participation[index]
        )
        damages = self.damages(
            data.gross_output[index], data.temp_atmosphere[index],
            abatement, self._params.savings
        )
        output = self.output(
            data.gross_output[index], damages, abatement, self._params.savings,
            data.temp_atmosphere[index]
        )
        consumption = self.consumption(
            output, self._params.savings, data.gross_output[index],
            abatement, data.temp_atmosphere[index]
        )
        output_abate = self.output_abate(abatement, data.gross_output[index])
        return [abatement, damages, output, consumption, output_abate]


class DiceDamages(DamagesModel):
    """
    Standard DICE2007 damages function
    """
    pass


class ExponentialMap(DamagesModel):
    """
    DICE2007 Damages with exponential mapping to output
    """
    def damages(self, gross_output, temp_atmosphere,
                a_abatement=None, a_savings=0):
        return gross_output * (1 - np.exp(
            -(self._params._a1 * temp_atmosphere + self._params._damages_coefficient *
              temp_atmosphere ** self._params.damages_exponent)
        ))


class AdditiveDamages(DamagesModel):
    """
    Weitzman additive damages function
    """
    def output_no_damages(self, gross_output, abatement):
        """
        Calculate output without damages
        ...
        Arguments
        ---------
        gross_output : float
        abatement : float
        ...
        Returns
        -------
        float
        """
        return gross_output - abatement

    def consumption_no_damages(self, gross_output, abatement, savings):
        """
        Calculate consumption without damages
        ...
        Arguments
        ---------
        gross_output : float
        abatement : float
        savings : float
        ...
        Returns
        -------
        float
        """
        ond = self.output_no_damages(gross_output, abatement)
        return ond - ond * savings

    def consumption(self, output, savings, a_gross_output=None,
                    a_abatement=None, a_temp_atmosphere=None, a_aa=None):
        Ct0 = 6.3745142949735118e-05
        C2d = 2.2337206076208615e-05
        C25d = 1.4797266368778764e-05
        C3d = 1.0102046050195233e-05
        cnd = self.consumption_no_damages(a_gross_output, a_abatement, savings)
        return cnd / (1 + cnd * C25d * a_temp_atmosphere ** a_aa[2])

    def output(self, gross_output, damages, abatement, a_savings=None,
               a_temp_atmosphere=None, a_aa=None):
        consumption = self.consumption(0, a_savings, gross_output, abatement,
                                       a_temp_atmosphere, a_aa)
        return consumption / (1 - a_savings)

    def damages(self, gross_output, temp_atmosphere,
                a_abatement=None, a_savings=0):
        output_no_damages = self.output_no_damages(gross_output, a_abatement)
        output = self.output(gross_output, 0, a_abatement, a_savings,
                             temp_atmosphere)
        return output_no_damages - output


class WeitzmanTippingPoint(DamagesModel):
    """
    Weitzman tipping point damages
    """
    def damages(self, gross_output, temp_atmosphere, a_abatement=None, a_savings=0):
        return gross_output * (1 - 1 / (
            1 + (temp_atmosphere / 20.46) ** 2 + (
                (temp_atmosphere / 6.081) ** 6.754
            )))


class ProductivityFraction(DamagesModel):
    """
    Wiesbach and Moyer damages as a fraction of productivity
    """
    def damages(self, gross_output, temp_atmosphere, a_abatement=None, a_savings=0):
        fD = self.get_production_factor(temp_atmosphere)
        damages_to_prod = 1 - (
            (1 - 1 / (
                1 + self._params._a1 * temp_atmosphere + self._params._damages_coefficient *
                temp_atmosphere ** self._params.damages_exponent
            )) / fD
        )
        return gross_output * (1. - damages_to_prod)

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
            1 + self._params._a1 * temp_atmosphere + self._params._damages_coefficient *
            temp_atmosphere ** self._params.damages_exponent
        )
        return 1 - self._params.prod_frac * D