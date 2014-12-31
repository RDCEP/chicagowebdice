from __future__ import division
import numpy as np
import numexpr as ne


class EmissionsModel(object):
    def __init__(self, params):
        self.params = params

    @property
    def emissions_deforest(self):
        return (
            self.params.emissions_deforest_init *
            (1 - .1) ** self.params.t0
        )

    @property
    def emissions_cap(self):
        return np.concatenate((
            np.ones(5),
            (np.ones(5) * (1 - self.params.e2050)),
            (np.ones(5) * (1 - self.params.e2100)),
            (np.ones(45) * (1 - self.params.e2150)),
        ))

    @property
    def user_tax_rate(self):
        c = [0, self.params.c2050, self.params.c2100,
             self.params.c2150, self.params.cmax]
        return np.concatenate((
            c[0] + ((c[1] - c[0]) / 5 * np.arange(5)),
            c[1] + ((c[2] - c[1]) / 5 * np.arange(5)),
            c[2] + ((c[3] - c[2]) / 5 * np.arange(5)),
            c[3] + ((c[3] - c[2]) / 5 * np.arange(45)),
        ))

    def emissions_ind(self, intensity, miu, gross_output):
        return ne.evaluate('intensity * (1 - miu) * gross_output')

    def emissions_total(self, emissions_ind, etree):
        return ne.evaluate('emissions_ind + etree')

    def carbon_emitted(self, emissions_total, carbon_emitted):
        ts = self.params.ts
        return ne.evaluate('carbon_emitted + emissions_total * ts')

    def get_miu(self, i, df, deriv=False, opt=False, miu=None):
        if opt:
            if miu is not None:
                if deriv:
                    return miu
                return miu[i]
        elif miu is None:
            if i > 0:
                if df.carbon_emitted[i - 1].any() > self.params.fosslim:
                    return 1.0
                if self.params.treaty:
                    return min(self.miu(
                        df.emissions_ind[i - 1],
                        self.emissions_cap[i - 1],
                        df.emissions_ind[0],
                        df.carbon_intensity[i], df.gross_output[i]
                    ), 1.0)
                elif self.params.carbon_tax:
                    return min(
                        (self.user_tax_rate[i] / (
                            df.backstop[i] * 1000)) ** (
                            1 / (self.params.abatement_exponent - 1)),
                        1.0
                    )
                else:
                    return 0
            else:
                return self.params.miu_init
        else:
            return min(miu[i], 1.0)
        return min(df.miu[i], 1.0)

    def miu(self, emissions_ind, emissions_cap, _e2005, intensity,
            gross_output):
        if emissions_cap == 0:
            return 1
        elif round(emissions_ind, 2) < round((_e2005 * emissions_cap), 2):
            return 0
        else: return ne.evaluate('1 - ((_e2005 * emissions_cap) / (intensity * gross_output))')

    def tax_rate(self, miu, backstop):
        ae = self.params.abatement_exponent
        return ne.evaluate('backstop * miu ** (ae - 1) * 1000 * 12 / 44')

    def get_model_values(self, i, df, deriv=False, opt=False,
                         miu=None, emissions_shock=0):
        miu = self.get_miu(i, df, deriv=deriv, opt=opt, miu=miu)
        emissions_ind = self.emissions_ind(
            df.carbon_intensity[i], miu, df.gross_output[i]
        )
        emissions_total = self.emissions_total(
            emissions_ind, self.emissions_deforest[i]
        ) + emissions_shock
        carbon_emitted = emissions_total * self.params.ts \
            if i == 0 \
            else self.carbon_emitted(emissions_total, df.carbon_emitted[i - 1])
        if np.max(carbon_emitted) > self.params.fosslim:
            emissions_total = 0.0
            carbon_emitted = self.params.fosslim
        tax_rate = self.tax_rate(miu, df.backstop[i])
        return (
            miu,
            emissions_ind,
            emissions_total,
            carbon_emitted,
            tax_rate,
        )


class Dice2007(EmissionsModel):
    pass


class Dice2010(EmissionsModel):
    @property
    def emissions_deforest(self):
        return (
            self.params.emissions_deforest_init *
            .8 ** self.params.t0
        )


class Dice2013(Dice2010):
    pass