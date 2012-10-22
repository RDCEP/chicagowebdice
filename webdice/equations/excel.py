import numpy as np

class ExcelLoop(object):
    """Equations from Nordhaus's GAMS code / Excel file"""
    def __init__(self):
        pass
    def capital(self, capital, dk, investment):
        """K(t), Capital, trillions $USD"""
        return (1 - dk)**10 * capital + 10 * investment
    def gross_output(self,al, capital, gama, l):
        """Gross output"""
        return al * capital**gama * l**(1-gama)
    def emissions_industrial(self, sigma, miu, gross_output):
        """E_ind, Industrial emissions, GtC"""
#        return 10 * sigma * (1 - miu) * gross_output
        return sigma * (1 - miu) * gross_output
    def emissions_total(self, emissions_industrial, etree):
        """E, Total emissions, GtC"""
        return emissions_industrial + etree
    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper, b):
        """M_AT, Carbon concentration in atmosphere, GtC"""
        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + emissions_total
#        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + 10 * emissions_total
    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower, b):
        """M_UP, Carbon concentration in shallow oceans, GtC"""
        return b[0][1] * mass_atmosphere + b[1][1] * mass_upper + b[2][1] * mass_lower
    def mass_lower(self, mass_upper, mass_lower, b):
        """M_LO, Carbon concentration in lower oceans, GtC"""
        return b[1][2] * mass_upper + b[2][2] * mass_lower
    def forcing(self, fco22x, mass_atmosphere, matPI, forcoth, ma_next):
        """F, Forcing, W/m^2"""
        return fco22x * np.log((((mass_atmosphere + ma_next)/2)+.000001)/matPI)/np.log(2) + forcoth
    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing, lam, c):
        """T_AT, Temperature of atmosphere, degrees C"""
        return temp_atmosphere + c[0] * (forcing - lam * temp_atmosphere - c[2] * (temp_atmosphere - temp_lower))
    def temp_lower(self, temp_atmosphere, temp_lower, c):
        """T_LO, Temperature of lower oceans, degrees C"""
        return temp_lower + c[3] * (temp_atmosphere - temp_lower)
    def damage(self, gross_output, temp_atmosphere, aa):
        """Omega, Damage, trillions $USD"""
        return gross_output - gross_output / (1 + temp_atmosphere * aa[0] + aa[1] * temp_atmosphere**aa[2])
    def abatement(self, gross_output, miu, gcost1, expcost2, partfract):
        """Lambda, Abatement costs, trillions $USD"""
        abatement = (gcost1 * miu**expcost2) * partfract**(1-expcost2)
        return gross_output * abatement
    def output(self, gross_output, damage, abatement):
        return (gross_output - damage) - abatement
    def investment(self, savings, output):
        """I, Investment, trillions $USD"""
        return savings * output
    def consumption(self, output, savings):
        """C, Consumption, trillions $USD"""
        return output - (savings * output)
    def consumption_percapita(self, consumption, l):
        """c, Per capita consumption, thousands $USD"""
        return (consumption / l) * 1000
    def utility(self, consumption_percapita, elasmu, l):
        """U, Period utility function"""
        return (1 / (1 - elasmu)) * consumption_percapita**(1-elasmu) + 1
    def utility_discounted(self, utility, pref_fac, l):
        """Utility"""
        return pref_fac * l * utility
    def preference_factor(self, prstp, pref_fac):
        return pref_fac / (1 + prstp)**10
    def welfare(self, utility, rr):
        return -np.sum(utility * rr)
    def miu(self, emissions_industrial, ecap, _e2005, sigma, gross_output):
        """mu, Emissions reduction rate"""
        if emissions_industrial < (_e2005 * ecap):
            return 0.
        else: return 1 - ((emissions_industrial * ecap) / (sigma * gross_output))