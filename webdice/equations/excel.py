import numpy as np

class ExcelLoop(object):
    def __init__(self):
        pass
    def capital(self, capital, dk, investment):
        return (1 - dk)**10 * capital + 10 * investment
    def gross_output(self,al, capital, gama, l):
        return al * capital**gama * l**(1-gama)
    def emissions_industrial(self, sigma, miu, gross_output):
        return sigma * (1 - miu) * gross_output
    def emissions_total(self, emissions_industrial, etree):
        return emissions_industrial + etree
    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper, b):
        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + 10 * emissions_total
    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower, b):
        return b[0][1] * mass_atmosphere + b[1][1] * mass_upper + b[2][1] * mass_lower
    def mass_lower(self, mass_upper, mass_lower, b):
        return b[1][2] * mass_upper + b[2][2] * mass_lower
    def forcing(self, fco22x, mass_atmosphere, matPI, forcoth, ma_next):
        return fco22x * (np.log((((mass_atmosphere + ma_next)/2)+.000001)/matPI)/np.log(2)) + forcoth
    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing, lam, c):
        return temp_atmosphere + c[0] * (forcing - lam * temp_atmosphere - c[2] * (temp_atmosphere - temp_lower))
    def temp_lower(self, temp_atmosphere, temp_lower, c):
        return temp_lower + c[3] * (temp_atmosphere - temp_lower)
    def damage(self, gross_output, temp_atmosphere, aa): # $ trillions per year
        return gross_output - gross_output / (1 + temp_atmosphere * aa[0] + aa[1] * temp_atmosphere**aa[2])
#    def abatement_fraction(self, gcost1, miu, expcost2, partfract): # fraction of output
#        return (gcost1 * miu**expcost2) * partfract**(1-expcost2)
    def abatement(self, gross_output, miu, gcost1, expcost2, partfract): # $ trillions per year
        abatement = (gcost1 * miu**expcost2) * partfract**(1-expcost2)
        return gross_output * abatement
    def output(self, gross_output, damage, abatement):
        return (gross_output - damage) - abatement
    def investment(self, savings, output):
        return savings * output
    def consumption(self, output, savings):
        return output - (savings * output)
    def consumption_percapita(self, consumption, l):
        return (consumption / l) * 1000
    def utility(self, consumption_percapita, elasmu, l):
        return (1 / (1 - elasmu)) * consumption_percapita**(1-elasmu) + 1
    def utility_discounted(self, utility, pref_fac, l):
#            return utility * rr
        return pref_fac * l * utility
    def preference_factor(self, prstp, pref_fac):
        return pref_fac / (1 + prstp)**10
    def welfare(self, utility, rr):
        return -np.sum(utility * rr)
    def miu(self, emissions_industrial, ecap, _e2005, sigma, gross_output):
        if emissions_industrial < (_e2005 * ecap):
            return 0.
        else: return 1 - ((emissions_industrial * ecap) / (sigma * gross_output))
