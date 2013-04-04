import numpy as np
from default import Loop


class DamagesModel(Loop):
    def __init__(self, prod_frac):
        Loop.__init__(self)
        self.prod_frac = prod_frac

    def get_production_factor(self, aa, temp_atmosphere):
        return 1.

    def get_model_values(self, gross_output, temp_atmosphere,
                         aa, abatement, savings):
        damage = self.damage(gross_output, temp_atmosphere, aa,
                             abatement, savings)
        output = self.output(gross_output, damage, abatement, savings,
                             temp_atmosphere, aa)
        consumption = self.consumption(output, savings, gross_output,
                                       abatement, temp_atmosphere, aa)
        return [damage, output, consumption]


class DiceDamages(DamagesModel):
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=0):
        return gross_output * (1 - 1 / (
            1 + aa[0] * temp_atmosphere + (
                aa[1] * temp_atmosphere ** aa[2]
        )))


class ExponentialMap(DamagesModel):
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=0):
        return gross_output * (1 - np.exp(
            -(aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2])
        ))


class AdditiveDamages(DamagesModel):
    def output_no_damage(self, gross_output, abatement):
        return gross_output * (1 - (abatement / gross_output))

    def consumption_no_damage(self, gross_output, abatement, savings):
        ond = self.output_no_damage(gross_output, abatement)
        return ond - ond * savings

    def consumption(self, output, savings, a_gross_output=None,
                    a_abatement=None, a_temp_atmosphere=None, a_aa=None):
        cnd = self.consumption_no_damage(a_gross_output, a_abatement, savings)
        return cnd / (1 + cnd * 6.3842e-6 * a_temp_atmosphere ** a_aa[2])

    def output(self, gross_output, damage, abatement, a_savings=None,
               a_temp_atmosphere=None, a_aa=None):
        consumption = self.consumption(0, a_savings, gross_output, abatement,
                                       a_temp_atmosphere, a_aa)
        return consumption / (1 - a_savings)

    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=0):
        return self.output_no_damage(
            gross_output, a_abatement
        ) - self.output(gross_output, 0, a_abatement, a_savings,
                        temp_atmosphere, aa)


class WeitzmanTippingPoint(DamagesModel):
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=0):
        return gross_output * (1 - 1 / (
            1 + (temp_atmosphere / 20.46) ** 2 + (
                (temp_atmosphere / 6.081) ** 6.754
        )))


class ProductivityFraction(DamagesModel):
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=0):
        d = self.get_production_factor(aa, temp_atmosphere)
        damage_to_prod = 1. - (
            (1. - aa[1] * temp_atmosphere ** aa[2]) / d
        )
        # print (d, damage_to_prod, self.prod_frac),
        return gross_output * damage_to_prod

    def get_production_factor(self, aa, temp_atmosphere):
        dmg = aa[1] * temp_atmosphere ** aa[2]
        return 1. - (dmg * self.prod_frac)


