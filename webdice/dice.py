import numpy as np
from params import diceParams
from equations import nordhaus, matlab, docs

class dice2007(diceParams):
    def __init__(self, decade=False, eq='nordhaus', time_travel=True):
        #TODO: Sort out decade shit
        self.eq = nordhaus.Loop()
        if eq == 'matlab':
            self.eq = matlab.Loop()
        elif eq == 'docs':
            self.eq = docs.Loop()
        if decade:
            self.decade = 10
        else:
            self.decade = 1
        diceParams.__init__(self)
#    	if time_travel:
#            self.eq.forcing = excel.ExcelLoop.forcing
    @property
    def vars(self):
        return [
            'capital', 'gross_output', 'emissions_industrial',
            'emissions_total', 'mass_atmosphere', 'mass_upper',
            'mass_lower', 'forcing', 'temp_atmosphere',
            'temp_lower', 'damage', 'abatement', 'output',
            'investment', 'carbon_emitted', 'consumption',
            'consumption_percapita', 'utility', 'utility_discounted',
        ] 
    @property
    def aa(self):
        """temp coefficient; pi_2, temp squared coefficient; epsilon, damage exponent"""
        return np.array([self.a1, self.a2, self.a3])
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
    def gsig(self):
        """sigma_g, Rate of decline of carbon intensity"""
        return self._gsigma * np.exp(-self.dsig * 10 * self.t0 - self.dsig2 * 10 * (self.t0 ** 2))
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
    def ecap(self):
        """Build emissions caps from treaty inputs"""
        #TODO: Use this to build phi, partfract (below) ?
        return np.concatenate((
            np.linspace(0, 0, 5),
            np.linspace(self.e2050, self.e2050, 5),
            np.linspace(self.e2100, self.e2100, 5),
            np.linspace(self.e2150, self.e2150, 45),
            ))
    @property
    def partfract(self):
        """phi, Fraction of emissions in control regime"""
        return np.concatenate((
            np.linspace(self.partfract1, self.partfract1, 1),
            self.partfract21 + (self.partfract2 - self.partfract21) * np.exp(-self.dpartfract * np.arange(23)),
            np.linspace(self.partfract21, self.partfract21, 36),
            ))
    @property
    def forcoth(self):
        """F_EX, Exogenous forcing for other greenhouse gases"""
        return np.concatenate((
            self.fex0 + .1 * (self.fex1 - self.fex0) * np.arange(11),
            self.fex0 + np.linspace(.36,.36, 49),
            ))

    def loop(self):
        """Step function for calculating endogenous variables"""
        for i in range(self.tmax):
            if i > 0:
                self.sigma[i] = self.sigma[i-1] / (1 - self.gsig[i])
                #TODO: In Nordhaus and in optimized MATLAB, there's no .95. Ask David et al about this. This is self.alc, set in __init__, always 1 for now.
                self.al[i] = self.al[i-1] / (1 - self.ga[i-1])
                self.capital[i] = self.eq.capital(self.capital[i-1], self.dk,
                    self.investment[i-1])
            self.gross_output[i] = self.eq.gross_output(self.al[i], self.capital[i], self._gama, self.l[i])
            self.emissions_industrial[i] = self.decade * self.eq.emissions_industrial(self.sigma[i], self.miu[i], self.gross_output[i])
            self.emissions_total[i] = self.eq.emissions_total(self.emissions_industrial[i], self.etree[i])
            if i > 0:
                self.miu[i] = self.eq.miu(self.emissions_industrial[i], self.ecap[i], self._e2005, self.sigma[i], self.gross_output[i])
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
            self.consumption[i] = self.eq.consumption(self.output[i], self.savings)
            self.consumption_percapita[i] = self.eq.consumption_percapita(self.consumption[i], self.l[i])
            self.utility[i] = self.eq.utility(self.consumption_percapita[i], self.elasmu, self.l[i])
            if i > 0:
                self.pref_fac[i] = self.eq.preference_factor(self.prstp, self.pref_fac[i-1])
            self.utility_discounted[i] = self.eq.utility_discounted(self.utility[i], self.pref_fac[i], self.l[i])

    def format_output(self):
        """Output text for graphs"""
        #TODO: This is sloppy as shit.
        output = ''
        for v in self.vars:
            vv = getattr(self, v)
            output += '%s %s\n' % (v, ' '.join(map(str, list(vv))))
        return output

if __name__ == '__main__':
    import argparse
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-e EQUATION] variables')
    eq_help = """
    Options are 'nordhaus', 'docs', or 'matlab'. You can select any pair 
    of models by separating them with a comma: e.g. -e excel,matab.
    You can see output from all three models with the option 'all'.
    Default is 'nordhaus'.
    """
    var_help = """
    You can print the following: capital, gross_output, emissions_industrial,
    emissions_total, mass_atmosphere, mass_lower, mass_upper, forcing,
    temp_atmosphere, temp_lower, damage, abatement, output, investment,
    carbon_emitted, consumption, consumption_percapita, utility,
    utility_discounted, and welfare.
    """
    parser.add_argument('-e', '--equation', help=eq_help, metavar='var1[,var2[,...]]')
    parser.add_argument('variables', help=var_help, metavar='var1[,var2[,...]]')
    args = parser.parse_args()
    if args.equation:
        if args.equation == 'matlab':
            d = [dice2007(eq='matlab')]
        elif args.equation == 'docs':
            d = [dice2007(eq='docs')]
        elif args.equation == ('excel' or 'nordhaus'):
            d = [dice2007()]
        elif args.equation == 'all':
            d = [
                dice2007(),
                dice2007(eq='matlab'),
                dice2007(eq='docs'),
            ]
        else:
            d = []
            for e in args.equation.split(','):
                d.append(dice2007(eq=e))
    else:
        d = [dice2007()]
    for m in d:
        m.loop()
    try:
        for v in args.variables.split(','):
            try:
                for m in d:
                    print bcolors.HEADER, '%s %s:\n' % (
                        m.eq.__module__.split('.')[1], v
                    ), bcolors.ENDC, getattr(m, v)
            except:
                print bcolors.WARNING, 'No variable named %s' % v, bcolors.ENDC
    except:
        print 'No variables specified'
        print 'You can print the following: capital, gross_output, emissions_industrial,'
        print 'emissions_total, mass_atmosphere, mass_lower, mass_upper, forcing,'
        print 'temp_atmosphere, temp_lower, damage, abatement, output, investment,'
        print 'carbon_emitted, consumption, consumption_percapita, utility,'
        print 'utility_discounted, and welfare'
