import numpy as np

class MatlabLoop(object):
    def __init__(self):
        def capital(self, capital, dk, savings, output):
            return capital * (1 - dk)**10 + 10 * (savings * output)
        def gross_output(self,al, capital, gama, l):
            return al * capital**gama * l**(1-gama)
        def emissions_industrial(self, sigma, miu, al, capital, gama, l):
            return 10 * sigma * (1 - miu) * al * capital**gama * l**(1-gama)
#        if vars.emissionsIndustrial > (e2005cap * e2005)
#        miu = 1 - (e2005cap * e2005) / (10 * sigma * al * (vars.capital^gama) * (l^(1-gama)))
#            emissions_industrial e2005cap * e2005
        def emissions_total(self, emissions_industrial, etree):
            return emissions_industrial + etree
        def mass_atmosphere(self, emissions_total, mass_atmosphere, mass_upper, b):
            return emissions_total + b[0][0] * mass_atmosphere + b[1][0] * mass_upper
        def mass_upper(self, mass_atmosphere, mass_upper, mass_lower, b):
            return b[0][1] * mass_atmosphere + b[1][1] * mass_upper + b[2][1] * mass_lower
        def mass_lower(self, mass_upper, mass_lower, b):
            return b[1][2] * mass_upper + b[2][2] * mass_lower
        def forcing(self, fco22x, mass_atmosphere, matPI, forcoth):
            return fco22x * np.log((mass_atmosphere + .000001)/matPI/np.log(2)) + forcoth
        def temp_atmosphere(self, temp_atmosphere, temp_lower, forcing, lam, c):
            return temp_atmosphere + c[0] * (forcing - lam * temp_atmosphere - c[2] * (temp_atmosphere - temp_lower))
        def temp_lower(self, temp_atmosphere, temp_lower, c):
            return temp_lower + c[3] * (temp_atmosphere - temp_lower)
        def participation(self, partfract):
            return partfract
        def participation_markup(self, participation, expcost2):
            return participation**(1-expcost2)
        def damage(self, temp_atmosphere, aa):
            return 1/( 1 + aa[0] * temp_atmosphere + aa[1] * temp_atmosphere**aa[2])
        def abatement(self, participation_markup, gcost1, miu, expcost2):
            return participation_markup * gcost1 * (miu**expcost2)
        def output(self, gross_output, damage, abatement):
            return gross_output * damage * (1-abatement)
        def investment(self, savings, output):
            return savings * output
        def consumption(self, savings, output):
            return (1 - savings) * output
        def consumption_percapita(self, consumption, l):
            return 1000 * consumption / l
        def utility(self, consumption_percapita, elasmu, l):
            return l * (consumption_percapita**(1-elasmu) / (1 - elasmu))
        def utility_discounted(self, utility, rr):
            return utility * rr
        
        
        
        
        
        
        def foo(self):
            return-sum(vars.utility .* rr)
        
        
