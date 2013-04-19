import numpy as np
from default import Loop


class DamagesModel(Loop):
    """
    Subclass default equations for the sake of using alternate
    damages functions.
    ....
    Args
    ----
    prod_frac : float
    """
    def __init__(self, prod_frac):
        Loop.__init__(self)
        self.prod_frac = prod_frac

    def get_production_factor(self, damages_terms, temp_atmosphere):
        """
        Return default fraction of productivity
        """
        return 1.

    def get_model_values(self, gross_output, temp_atmosphere,
                         damages_terms, abatement, savings):
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
        damages = self.damages(gross_output, temp_atmosphere, damages_terms,
                               abatement, savings)
        output = self.output(gross_output, damages, abatement, savings,
                             temp_atmosphere, damages_terms)
        consumption = self.consumption(output, savings, gross_output,
                                       abatement, temp_atmosphere,
                                       damages_terms)
        return [damages, output, consumption]


class DiceDamages(DamagesModel):
    """
    Standard DICE2007 damages function
    """
    def damages(self, gross_output, temp_atmosphere, damages_terms,
                a_abatement=None, a_savings=0):
        return gross_output * (1 - 1 / (
            1 + damages_terms[0] * temp_atmosphere + damages_terms[1] *
            temp_atmosphere ** damages_terms[2]
        ))


class ExponentialMap(DamagesModel):
    """
    DICE2007 Damages with exponential mapping to output
    """
    def damages(self, gross_output, temp_atmosphere, damages_terms,
                a_abatement=None, a_savings=0):
        return gross_output * (1 - np.exp(
            -(damages_terms[0] * temp_atmosphere + damages_terms[1] *
              temp_atmosphere ** damages_terms[2])
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

    def damages(self, gross_output, temp_atmosphere, damages_terms,
                a_abatement=None, a_savings=0):
        output_no_damages = self.output_no_damages(gross_output, a_abatement)
        output = self.output(gross_output, 0, a_abatement, a_savings,
                             temp_atmosphere, damages_terms)
        return output_no_damages - output


class WeitzmanTippingPoint(DamagesModel):
    """
    Weitzman tipping point damages
    """
    def damages(self, gross_output, temp_atmosphere, damages_terms,
                a_abatement=None, a_savings=0):
        return gross_output * (1 - 1 / (
            1 + (temp_atmosphere / 20.46) ** 2 + (
                (temp_atmosphere / 6.081) ** 6.754
            )))


class ProductivityFraction(DamagesModel):
    """
    Wiesbach and Moyer damages as a fraction of productivity
    """
    def damages(self, gross_output, temp_atmosphere, damages_terms,
                a_abatement=None, a_savings=0):
        fD = self.get_production_factor(damages_terms, temp_atmosphere)
        damages_to_prod = 1 - (
            (1 - 1 / (
                1 + damages_terms[0] * temp_atmosphere + damages_terms[1] *
                temp_atmosphere ** damages_terms[2]
            )) / fD
        )
        return gross_output * (1. - damages_to_prod)

    def get_production_factor(self, damages_terms, temp_atmosphere):
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
            1 + damages_terms[0] * temp_atmosphere + damages_terms[1] *
            temp_atmosphere ** damages_terms[2]
        )
        return 1 - self.prod_frac * D