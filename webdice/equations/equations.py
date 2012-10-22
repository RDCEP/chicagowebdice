import numpy as np

class dice2007(object):
    def __init__(self):
        def calc_capital(self, capital, dk, savings, output):
            self.capital[i] = self.capital[i-1] * (1 - self.dk)**10 + (10 * self.savings) * self.output[i-1]
        def calc_mass_lower(self, i):
            self.mass_lower[i] = self.b23 * self.mass_upper[i-1] + self.b33 * self.mass_lower[i-1]
        def calc_mass_upper(self, i):
            self.mass_upper[i] = self.b12 * self.mass_atmosphere[i-1] * self.b22 * self.mass_upper[i-1] + self.b32 * self.mass_lower[i-1]
        def calc_mass_atmosphere(self, i):
            self.mass_atmosphere[i] = self.emissions_total[i-1] + self.b11 * self.mass_atmosphere[i-1] + self.b21 * self.mass_upper[i-1]
        def calc_forcing(self, i):
            self.forcing[i] = self.fco22x * np.log2((self.mass_atmosphere[i] + .000001) / self.matPI / np.log2(2)) +self.forcoth[i]
        def calc_temp_atmosphere(self, i):
            self.temp_atmosphere[i] = self.temp_atmosphere[i-1] + self.c1 * (self.forcing[i] - self.lam * self.temp_atmosphere[i-1] - self.c3 * (self.temp_atmosphere[i-1] - self.temp_lower[i-1]))
        def calc_temp_lower(self, i):
            self.temp_lower[i] = self.temp_lower[i-1] + self.c4 * (self.temp_atmosphere[i-1] - self.temp_lower[i-1])
        def calc_carbon_emitted(self, i):
            self.carbon_emitted[i] = self.carbon_emitted[i-1] + self.emissions_total[i]
        def calc_gross_output(self):
            self.gross_output = self.al * self.capital**self._gama * self.l**(1-self._gama)
        def calc_emissions_total(self):
            self.emissions_total = self.emissions_total + self.etree
        def calc_participation_markup(self):
            self.participation_markup = self.participation**(1-self.expcost2)
        def calc_abatement(self):
            self.abatement = self.participation_markup * self.gcost1 * self.miu**self.expcost2
        def calc_damage(self):
            self.damage = 1 / (1 + self.al * self.temp_atmosphere + self.a2 * self.temp_atmosphere**self.a3)
        def calc_output(self):
            self.output = self.gross_output * self.damage * (1 - self.abatement)
        def calc_investment(self):
            self.investment = self.savings * self.output
        def calc_consumption(self):
            self.consumption = (1 - self.savings) * self.output
        def calc_consumption_percapita(self):
            self.consumption_percapita = 1000 * self.consumption / self.l
        def calc_utility(self):
            self.utility = self.l * (self.consumption_percapita**(1 - self.elasmu) / (1 - self.elasmu))
        def calc_utility_discounted(self):
            self.utility_discounted = self.utility * self.rr
        def calc_welfare(self):
            self.welfare = -np.sum(self.utility * self.rr)
        def calc_miu(self):
            def emissions_cap_miu(miu, eind, ecap, sigma, al, capital, l):
                if eind > (ecap * self._e2005):
                    return 1 - (ecap * self._e2005) / (10 * sigma * al * (capital**self._gama) * (l**(1-self._gama)))
                else:
                    return miu
            ecm = np.vectorize(emissions_cap_miu)
            #TODO: Rewrite. miu can't be set as it's a property
            self.miu = ecm(self.miu, self.emissions_industrial, self.e2005cap, self.sigma, self.al, self.capital, self.l)
        def calc_emissions_industrial(self):
            def emissions_cap_ind(eind, ecap):
                if eind > (ecap * self._e2005):
                    return ecap * self._e2005
                else:
                    return eind
            eci = np.vectorize(emissions_cap_ind)
            self.emissions_industrial = eci(self.emissions_industrial, self.e2005cap)