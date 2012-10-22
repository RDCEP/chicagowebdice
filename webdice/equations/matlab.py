import numpy as np

class MatlabLoop(object):
    def __init__(self):
        pass
    def capital(self, capital, dk, investment):
        return capital * (1 - dk)**10 + 10 * investment
    def gross_output(self,al, capital, gama, l):
        return al * capital**gama * l**(1-gama)
    def emissions_industrial(self, sigma, miu, gross_output):
#        return 10 * sigma * (1 - miu) * gross_output
        return sigma * (1 - miu) * gross_output
    def emissions_total(self, emissions_industrial, etree):
        return emissions_industrial + etree
    def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper, b):
        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + emissions_total
#        return b[0][0] * mass_atmosphere + b[1][0] * mass_upper + 10 * emissions_total
    def mass_upper(self, mass_atmosphere, mass_upper, mass_lower, b):
        return b[0][1] * mass_atmosphere + b[1][1] * mass_upper + b[2][1] * mass_lower
    def mass_lower(self, mass_upper, mass_lower, b):
        return b[1][2] * mass_upper + b[2][2] * mass_lower
    def forcing(self, fco22x, mass_atmosphere, matPI, forcoth, ma_next):
        return fco22x * np.log((mass_atmosphere + .000001)/matPI/np.log(2)) + forcoth
    def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing, lam, c):
        return temp_atmosphere + c[0] * (forcing - lam * temp_atmosphere - c[2] * (temp_atmosphere - temp_lower))
    def temp_lower(self, temp_atmosphere, temp_lower, c):
        return temp_lower + c[3] * (temp_atmosphere - temp_lower)
    def damage(self, gross_output, temp_atmosphere, aa):
        return 1/( 1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere**aa[2])
    def abatement(self, gross_output, miu, gcost1, expcost2, partfract):
        return partfract**(1-expcost2) * gcost1 * (miu**expcost2)
    def output(self, gross_output, damage, abatement):
        return gross_output * damage * (1-abatement)
    def investment(self, savings, output):
        return savings * output
    def consumption(self, output, savings):
        return (1 - savings) * output
    def consumption_percapita(self, consumption, l):
        return 1000 * consumption / l
    def utility(self, consumption_percapita, elasmu, l):
        return l * (consumption_percapita**(1-elasmu) / (1 - elasmu))
    def preference_factor(self, prstp, pref_fac):
        return 1
    def utility_discounted(self, utility, pref_fac, rr):
        return utility * rr
    def welfare(self, utility, rr):
        return -np.sum(utility * rr)
    def miu(self, emissions_industrial, ecap, _e2005, sigma, gross_output):
        if emissions_industrial < (_e2005 * ecap):
            return 0.
        else: return 1 - ((emissions_industrial * ecap) / (sigma * gross_output))