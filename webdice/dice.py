import numpy as np
from params import diceParams
from equations import excel

#class dice2007(diceParams, excel.ExcelLoop):
class dice2007(diceParams):
    def __init__(self, decade=False):
        self.eq = excel.ExcelLoop()
        if decade:
            self.decade = 10
        else:
            self.decade = 1
        diceParams.__init__(self)
    @property
    def gfacpop(self):
        """L_g, Population growth factor"""
        return (np.exp(self._gpop0 * self.t0) - 1) / (np.exp(self._gpop0 * self.t0))
    @property
    def l(self):
        """L, Population"""
        return self._pop0 * (1 - self.gfacpop) + self.gfacpop * self.popasym
    @property
    def ga(self):
        """A_g, Growth rate of total factor productivity"""
        return self._ga0 * np.exp(-self.dela * 10 * self.t0)
    @property
    def al(self):
        """A, Total factor productivity"""
        al = np.linspace(self._a0, self._a0, self.tmax)
        for i in range(self.tmax):
            if i > 0:
                #TODO: In Optimized run, there's no .95. Ask David et al about this.
#                al[i] = (.95 * al[i-1]) / (1 - self.ga[i-1])
                al[i] = al[i-1] / (1 - self.ga[i-1])
        return al
    @property
    def gsig(self):
        """sigma_g, Rate of decline of carbon intensity"""
        return self._gsigma * np.exp(-self.dsig * 10 * self.t0 - self.dsig2 * 10 * (self.t0 ** 2))
    @property
    def sigma(self):
        """sigma, Ratio of uncontrolled industrial emissions to output"""
        #TODO: Get rid of for loop -- use ufunc
        sigma = np.linspace(self._sig0, self._sig0, self.tmax)
        for i in range(self.tmax):
            if i > 0:
                sigma[i] = sigma[i-1] / (1 - self.gsig[i])
        return sigma
    @property
    def gcost1(self):
        """theta_1, Growth of cost factor"""
        return (self._pback * self.sigma / self.expcost2) *\
               ((self.backrat - 1 + np.exp(-self.gback * self.t0)) / self.backrat)
    @property
    def etree(self):
        #CHECKED (SCALED FOR DECADE)
        """E_land, Emissions from deforestation"""
        return self.decade * self._eland0 * (1 - .1)**self.t0
    @property
    def rr(self):
        """R, Average utility social discount rate"""
#        return 1 / ((1 + self.prstp)**(10*self.t0))
        return 1 / ((1 + self.prstp)**(self.decade*self.t0))
    @property
    def partfract(self):
        """phi, Fraction of emissions in control regime"""
        return np.concatenate((
            np.linspace(self.partfract1, self.partfract1, 1), # 1
            self.partfract21 + (self.partfract2 - self.partfract21) * np.exp(-self.dpartfract * np.arange(23)), # 23
            np.linspace(self.partfract21, self.partfract21, 36), # 36
            ))
    @property
    def forcoth(self):
        """F_EX, Exogenous forcing for other greenhouse gases"""
        return np.concatenate((
            self.fex0 + .1 * (self.fex1 - self.fex0) * np.arange(11),
            self.fex0 + np.linspace(.36,.36, 49),
            ))
    def calc_miu(self):
        """mu, emissions reduction rate"""
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
        self.emissions_total = self.emissions_total + self.etree

    def loop(self):
        """Step function for calculating endogenous variables"""
        for i in range(self.tmax):
            if i > 0:
                self.capital[i] = self.eq.capital(self.capital[i-1], self.dk, self.investment[i-1])
            self.gross_output[i] = self.eq.gross_output(self.al[i], self.capital[i], self._gama, self.l[i])
            self.emissions_industrial[i] = self.decade* self.eq.emissions_industrial(self.sigma[i], self.miu[i], self.gross_output[i])
            if self.eq.__module__ != 'equations.excel':
                if self.emissions_industrial[i] > (self.e2005cap[i] * self._e2005):
                    self.miu[i] = 1 - (self.e2005cap[i] * self._e2005) / (10 * self.sigma[i] * self.gross_output[i])
                    self.emissions_industrial[i] = self.e2005cap[i] * self._e2005
            self.emissions_total[i] = self.eq.emissions_total(self.emissions_industrial[i], self.etree[i])
            if i > 0:
                self.carbon_emitted[i] = self.carbon_emitted[i-1] + self.emissions_total[i]
            if self.carbon_emitted[i] > self.fosslim:
                self.miu[i] = 1
                self.emissions_total[i] = 0
                self.carbon_emitted[i] = self.fosslim
            if i > 0:
                self.mass_atmosphere[i] = self.eq.mass_atmosphere(self.emissions_total[i-1],
                    self.mass_atmosphere[i-1], self.mass_upper[i-1], self.bb)
                self.mass_upper[i] = self.eq.mass_upper(self.mass_atmosphere[i-1], self.mass_upper[i-1], self.mass_lower[i-1], self.bb)
                self.mass_lower[i] = self.eq.mass_lower(self.mass_upper[i-1], self.mass_lower[i-1], self.bb)

            self.forcing[i] = self.fco22x * np.log((self.mass_atmosphere[i] / self.matPI)) + self.forcoth[i]
            ma2 = self.eq.mass_atmosphere(self.emissions_total[i],self.mass_atmosphere[i], self.mass_upper[i], self.bb)
            self.forcing[i] = self.eq.forcing(self.fco22x, self.mass_atmosphere[i], self.matPI, self.forcoth[i], ma2)
            if i > 0:
                self.temp_atmosphere[i] = self.eq.temp_atmosphere(self.temp_atmosphere[i-1], self.temp_lower[i-1],
                    self.forcing[i], self.lam, self.cc)
                self.temp_lower[i] = self.eq.temp_lower(self.temp_atmosphere[i-1], self.temp_lower[i-1], self.cc)
            self.damage[i] = self.eq.damage(self.gross_output[i], self.temp_atmosphere[i], self.aa)
            self.abatement[i] = self.eq.abatement(self.gross_output[i], self.miu[i], self.gcost1[i], self.expcost2, self.partfract[i])
            self.output[i] = self.eq.output(self.gross_output[i], self.damage[i], self.abatement[i])
            self.investment[i] = self.eq.investment(self.savings, self.output[i])

            self.consumption[i] = self.eq.consumption(self.output[i], self.investment[i])
            self.consumption_percapita[i] = self.eq.consumption_percapita(self.consumption[i], self.l[i])
            self.utility[i] = self.eq.utility(self.consumption_percapita[i], self.elasmu, self.l[i])
            if i > 0:
                self.pref_fac[i] = self.eq.preference_factor(self.prstp, self.pref_fac[i-1])
            self.utility_discounted[i] = self.eq.utility_discounted(self.utility[i], self.pref_fac[i], self.l[i])

d = dice2007()
d.loop()
print getattr(d,'al')
#print 'capital: ', d.capital
#print 'gross_output: ', d.gross_output
#print 'emissions_ind: ', d.emissions_industrial
#print 'emissions_total: ', d.emissions_total
#print 'mass_atmosphere: ', d.mass_atmosphere[-1]
#print 'mass_upper: ', d.mass_upper[-1]
#print 'mass_lower: ', d.mass_lower[-1]
#print 'forcing: ', d.forcing
#print 'temp_lower: ', d.temp_lower
#print 'temp_atmosphere: ', d.temp_atmosphere
#print 'damage: ', d.damage[-1]
#print 'abatement: ', d.abatement[-1]
#print 'output: ', d.output
#print 'investment: ', d.investment
#print 'capital: ', d.capital

#print 'carbon emitted: ', d.carbon_emitted
#print 'participation: ', d.participation
#print 'participation_markup: ', d.participation_markup
#print 'consumption: ', d.consumption
#print 'consumption_percapita: ', d.consumption_percapita
#print 'utility: ', d.utility
#print 'utility_discounted: ', d.utility_discounted
#print 'miu: ', d.miu
#print d.welfare
