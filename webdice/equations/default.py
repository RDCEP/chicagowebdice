import numpy as np

class Loop(object):
    """Default equation set."""
    def __init__(self):
        pass

    def capital(self, capital, dk, investment):
        """K(t), Capital, trillions $USD"""
        return capital * (1 - dk) ** 10 + 10 * investment

    def gross_output(self,al, capital, gama, l):
        """Gross output"""
        return al * capital ** gama * l ** (1 - gama)

    def emissions_ind(self, sigma, miu, gross_output):
        """E_ind, Industrial emissions, GtC"""
        return sigma * (1. - miu) * gross_output

    def emissions_total(self, emissions_ind, etree):
        """E, Total emissions, GtC"""
        return emissions_ind + etree

    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper, b):
        """M_AT, Carbon concentration in atmosphere, GtC"""
        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + (
            10 * emissions_total
        )

    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower, b):
        """M_UP, Carbon concentration in shallow oceans, GtC"""
        return b[0][1] * mass_atmosphere + b[1][1] * mass_upper + (
            b[2][1] * mass_lower
        )

    def mass_lower(self, mass_upper, mass_lower, b):
        """M_LO, Carbon concentration in lower oceans, GtC"""
        return b[1][2] * mass_upper + b[2][2] * mass_lower

    def forcing(self, fco22x, mass_atmosphere, matPI, forcoth):
        """F, Forcing, W/m^2"""
        return fco22x * np.log(mass_atmosphere / matPI) + forcoth
        # return fco22x * (np.log((
        #     ((mass_atmosphere + ma_next) / 2) + .000001
        # ) / matPI) / np.log(2)) + forcoth

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing,
                        fco22x, t2xco2, c):
        """T_AT, Temperature of atmosphere, degrees C"""
        return temp_atmosphere + c[0] * (
            forcing - (fco22x / t2xco2) * temp_atmosphere - c[2] * (
                temp_atmosphere - temp_lower
            )
        )

    def temp_lower(self, temp_atmosphere, temp_lower, c):
        """T_LO, Temperature of lower oceans, degrees C"""
        return temp_lower + c[3] * (temp_atmosphere - temp_lower)

    # @classmethod
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=None):
        """Omega, Damage, trillions $USD"""
        return gross_output * (1 - 1 / (
            1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
        ))

    def abatement(self, gross_output, miu, gcost1, expcost2, partfract):
        """Lambda, Abatement costs, trillions $USD"""
        return partfract ** (1 - expcost2) * gross_output * gcost1 * (
            miu ** expcost2)

    def output(self, gross_output, damage, abatement, a_savings=None,
               a_temp_atmosphere=None, a_aa=None):
        return (
            (gross_output - abatement) * (gross_output - damage)
        ) / gross_output

    def investment(self, savings, output):
        """I, Investment, trillions $USD"""
        return savings * output

    def consumption(self, output, savings, a_gross_output=None,
                    a_abatement=None, a_temp_atmosphere=None, a_aa=None):
        """C, Consumption, trillions $USD"""
        return output * (1.0 - savings)

    def consumption_pc(self, consumption, l):
        """c, Per capita consumption, thousands $USD"""
        return 1000 * consumption / l

    def consumption_discount(self, prstp, elasmu, c0, c1, i):
        """Discount rate for consumption"""
        # return (prstp * 100 + elasmu * (
        #         (c1 - c0) / c0
        #     ) * 10) / 100
        return 1 / (
            1 + (prstp * 100 + elasmu * (
                (c1 - c0) / c0
            ) * 10) / 100
        ) ** (10 * i)

    def utility(self, consumption_pc, elasmu, l):
        """U, Period utility function"""
        return (1 / (1 - elasmu + .000001)) * consumption_pc ** (1 - elasmu) + 1

    def utility_d(self, utility, rr, l):
        """Utility"""
        return rr * l * utility

    def welfare(self, utility_d, rr):
        return np.sum(utility_d)

    def miu(self, emissions_ind, ecap, _e2005, sigma, gross_output):
        """mu, Emissions reduction rate"""
        if ecap == 0:
            return 1.
        elif round(emissions_ind, 2) < round((_e2005 * ecap), 2):
            return 0.
        else: return 1 - ((_e2005 * ecap) / (sigma * gross_output))
