from FuncDesigner import *
from openopt import NLP
import numpy as np

class Dice2007Optimizer(object):
    def __init__(self, dice):
        self.dice = dice
        self.dice.optimize = True
        self.MU = 1
        self.mu = oovar('mu')
        self.savings = self.dice.savings.value
        self.theta_2 = self.dice.expcost2.value
        self.alpha = self.dice.elasmu.value
        self.gamma = self.dice._gama
        self.delta_k = self.dice.dk.value
        self.aa = self.dice.aa
        self.bb = self.dice.bb
        self.cc = self.dice.cc
        self.nu = self.dice.fco22x
        self.sig = 1.
        self.lam = self.dice.lam
        self.matPI = self.dice.matPI
        #self.phi = .25372
        self.mu_tmp = np.array([.005])
    def get_mu(self):
        for i in range(1, self.dice.tmax):
            start_point = {self.mu: self.MU,}
            self.dice.loop(step=i, miu=self.mu_tmp)
            l = self.dice.l[i]
            a = self.dice.al[i]
            sigma = self.dice.sigma[i]
            rho = self.dice.rr[i]
            theta_1 = self.dice.gcost1[i]
            e_land = self.dice.etree[i]
            f_ex = self.dice.forcoth[i]
            phi = self.dice.partfract[i]
            m_at = self.dice.mass_atmosphere[i-1]
            m_up = self.dice.mass_upper[i-1]
            m_lo = self.dice.mass_lower[i-1]
            t_at = self.dice.temp_atmosphere[i-1]
            t_lo = self.dice.temp_lower[i-1]
            k = self.dice.capital[i-1]
            inv = self.dice.investment[i-1]
            capital = k * (1 - self.delta_k)**10 + 10 * inv
            gross_output = a * capital**self.gamma * l**(1-self.gamma)
            emissions = sigma * (1 - self.mu) * gross_output + e_land
            mass_at = self.bb[0][0] * m_at + self.bb[1][0] * m_up + 10 * emissions
#            mass_up = self.bb[0][1] * m_at + self.bb[1][1] * m_up + self.bb[2][1] * m_lo
#            mass_lo = self.bb[1][2] * m_up + self.bb[2][2] * m_lo
            forcing = self.nu * log(mass_at / self.matPI) + f_ex
            temp_at = t_at + self.cc[0] * (forcing - self.lam * t_at - self.cc[2] * (t_at - t_lo))
#            temp_lo = t_lo + self.cc[3] * (t_at - t_lo)
            damage = gross_output - gross_output / (1 + self.aa[1] * temp_at**self.aa[2])
            abatement = phi**(1-self.theta_2) * gross_output * theta_1 * self.mu**self.theta_2
            output = gross_output * ((1 - abatement / gross_output) / (gross_output/(gross_output - damage)))
#            investment = self.savings * output
            consumption = output - (output * self.savings)
            consumption_percap = consumption * 1000 / l
            utility = (1 / (1 - self.alpha)) * consumption_percap**(1-self.alpha) + 1
            utility_discount = rho * l * utility
            obj_func = sum(utility_discount)
            IPRINT = -1
            SOLVER = 'ralg'
            p = NLP(obj_func, start_point)
            p.constraints = [self.mu>=0., self.mu<=1., mass_at<4000.]
            r = p.maximize(SOLVER, iprint=IPRINT)
            self.mu_tmp = np.append(self.mu_tmp, r(self.mu))
        return self.mu_tmp