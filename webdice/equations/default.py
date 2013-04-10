import numpy as np

class Loop(object):
    """Default equation set."""
    def __init__(self):
        pass

    def capital(self, capital, tech_depreciation, investment):
        """K(t), Capital, trillions $USD"""
        return capital * (1 - tech_depreciation) ** 10 + 10 * investment

    def gross_output(self, productivity, capital, gama, l):
        """Gross output"""
        return productivity * capital ** gama * l ** (1 - gama)

    def emissions_ind(self, intensity, miu, gross_output):
        """E_ind, Industrial emissions, GtC"""
        return intensity * (1. - miu) * gross_output

    def emissions_total(self, emissions_ind, etree):
        """E, Total emissions, GtC"""
        return emissions_ind + etree

    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper,
                        carbon_matrix):
        """M_AT, Carbon concentration in atmosphere, GtC"""
        return (
            carbon_matrix[0][0] * mass_atmosphere + carbon_matrix[1][0] *
            mass_upper + (10 * emissions_total)
        )

    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower,
                   carbon_matrix):
        """M_UP, Carbon concentration in shallow oceans, GtC"""
        return (
            carbon_matrix[0][1] * mass_atmosphere + carbon_matrix[1][1] *
            mass_upper + (carbon_matrix[2][1] * mass_lower)
        )

    def mass_lower(self, mass_upper, mass_lower, carbon_matrix):
        """M_LO, Carbon concentration in lower oceans, GtC"""
        return (
            carbon_matrix[1][2] * mass_upper + carbon_matrix[2][2] * mass_lower
        )

    def forcing(self, _forcing_co2_doubling, mass_atmosphere,
                _mass_preindustrial, forcing_ghg):
        """F, Forcing, W/m^2"""
        return (
            _forcing_co2_doubling *
            np.log(mass_atmosphere / _mass_preindustrial) + forcing_ghg
        )
        # return _forcing_co2_doubling * (np.log((
        #     ((mass_atmosphere + ma_next) / 2) + .000001
        # ) / _mass_preindustrial) / np.log(2)) + forcing_ghg

    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing,
                        _forcing_co2_doubling, temp_co2_doubling,
                        thermal_transfer):
        """T_AT, Temperature of atmosphere, degrees C"""
        return (
            temp_atmosphere + thermal_transfer[0] * (
                forcing - (_forcing_co2_doubling / temp_co2_doubling) *
                temp_atmosphere - thermal_transfer[2] *
                (temp_atmosphere - temp_lower)
            )
        )

    def temp_lower(self, temp_atmosphere, temp_lower, thermal_transfer):
        """T_LO, Temperature of lower oceans, degrees C"""
        return (
            temp_lower + thermal_transfer[3] * (temp_atmosphere - temp_lower)
        )

    # @classmethod
    def damage(self, gross_output, temp_atmosphere, aa, a_abatement=None,
               a_savings=None):
        """Omega, Damage, trillions $USD"""
        return gross_output * (1 - 1 / (
            1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere ** aa[2]
        ))

    def abatement(self, gross_output, miu, backstop_growth, abatement_exponent,
                  participation):
        """Lambda, Abatement costs, trillions $USD"""
        return (
            gross_output * participation ** (1 - abatement_exponent) *
            backstop_growth * miu ** abatement_exponent
        )

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

    def miu(self, emissions_ind, emissions_cap, _e2005, intensity,
            gross_output):
        """mu, Emissions reduction rate"""
        if emissions_cap == 0:
            return 1.
        elif round(emissions_ind, 2) < round((_e2005 * emissions_cap), 2):
            return 0.
        else: return 1 - ((_e2005 * emissions_cap) / (intensity * gross_output))

    def tax_rate(self, backstop, miu, abatement_exponent):
        return (
            backstop * miu ** (abatement_exponent - 1)
        )