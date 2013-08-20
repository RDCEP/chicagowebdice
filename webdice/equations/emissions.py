from __future__ import division
import numpy as np


class EmissionsModel(object):
    """
    EmissionsModel base class
    ...
    Properties
    ----------
    emissions_deforest : array
        Emission from deforestation
    emissions_cap : array
        Emissions caps for treaty
    user_tax_rate : array
        Array of user-determined annual tax rates
    ...
    Methods
    -------
    get_emissions_values()
    emissions_ind()
    emissions_total()
    carbon_emitted()
    get_miu()
    miu()
    tax_rate()
    """
    def __init__(self, params):
        self._params = params
        self.eps = params._eps

    @property
    def emissions_deforest(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array
        """
        return (
            self._params._emissions_deforest_2005 *
            (1 - .1) ** self._params._t0
        )

    @property
    def emissions_cap(self):
        """
        Emissions caps from treaty inputs
        ...
        Returns
        -------
        array
        """
        return np.concatenate((
            np.ones(5),
            (np.ones(5) * (1 - self._params.e2050)),
            (np.ones(5) * (1 - self._params.e2100)),
            (np.ones(45) * (1 - self._params.e2150)),
        ))

    @property
    def user_tax_rate(self):
        """
        Optional user-defined carbon tax
        ...
        Returns
        -------
        array
        """
        c = [0, self._params.c2050, self._params.c2100,
             self._params.c2150, self._params._cmax]
        return np.concatenate((
            c[0] + ((c[1] - c[0]) / 5 * np.arange(5)),
            c[1] + ((c[2] - c[1]) / 5 * np.arange(5)),
            c[2] + ((c[3] - c[2]) / 5 * np.arange(5)),
            c[3] + ((c[3] - c[2]) / 5 * np.arange(45)),
        ))

    def get_emissions_values(self, index, data, deriv=False, miu=None,
                             emissions_shock=0):
        miu = min(self.get_miu(index, data, deriv=deriv, miu=miu), 1.0)
        emissions_ind = self.emissions_ind(
            data.carbon_intensity[index], miu, data.gross_output[index]
        )
        emissions_total = self.emissions_total(
            emissions_ind, self.emissions_deforest[index]
        ) + emissions_shock
        carbon_emitted = self.carbon_emitted(emissions_total, index, data)
        if carbon_emitted > self._params.fosslim:
            emissions_total = 0.0
            carbon_emitted = self._params.fosslim
        tax_rate = self.tax_rate(miu, data.backstop[index])
        return (
            miu,
            emissions_ind,
            emissions_total,
            carbon_emitted,
            tax_rate,
        )

    def emissions_ind(self, intensity, miu, gross_output):
        """
        E_ind, Industrial emissions, GtC
        ...
        Returns
        -------
        float
        """
        return intensity * (1 - miu) * gross_output

    def emissions_total(self, emissions_ind, etree):
        """
        E, Total emissions, GtC
        ...
        Returns
        -------
        float
        """
        return emissions_ind + etree

    def carbon_emitted(self, emissions_total, index, data):
        if index > 0:
            return data.carbon_emitted[index - 1] + emissions_total * 10
        return emissions_total * 10

    def get_miu(self, index, data, deriv=False, miu=None):
        """
        Return miu for optimized, treaty, tax, basic scenarios
        ...
        Args
        ----
        index : int, index of time step
        data : pd.DataFrame
        ...
        Kwargs
        ------
        deriv : boolean
        miu : array
        ...
        Returns
        -------
        float
        """
        if self._params._optimize:
            if miu is not None:
                if deriv:
                    data.miu = miu
                    return data.miu[index] + self.eps
                else:
                    return miu[index]
        else:
            if index > 0:
                if data.carbon_emitted[index - 1] > self._params.fosslim:
                    return 1.0
                if self._params._treaty:
                    return self.miu(
                        data.emissions_ind[index - 1],
                        self.emissions_cap[index - 1],
                        data.emissions_ind[0],
                        data.carbon_intensity[index], data.gross_output[index]
                    )
                elif self._params._carbon_tax:
                    return (
                        (self.user_tax_rate[index] / (
                            data.backstop[index] * 1000)) ** (
                            1 / (self._params.abatement_exponent - 1))
                    )
                else:
                    return 0
            else:
                return self._params._miu_2005
        return data.miu[index]

    def miu(self, emissions_ind, emissions_cap, _e2005, intensity,
            gross_output):
        """
        mu, Emissions reduction rate
        ...
        Returns
        -------
        float
        """
        if emissions_cap == 0:
            return 1
        elif round(emissions_ind, 2) < round((_e2005 * emissions_cap), 2):
            return 0
        else: return 1 - ((_e2005 * emissions_cap) / (intensity * gross_output))

    def tax_rate(self, miu, backstop):
        """
        Implied tax rate, thousands $USD per ton CO_2
        ...
        Returns
        -------
        float
        """
        return (
            backstop * miu ** (self._params.abatement_exponent - 1) * 1000
        )


class Dice2007(EmissionsModel):
    pass


class Dice2010(EmissionsModel):
    @property
    def emissions_deforest(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array
        """
        return (
            self._params._emissions_deforest_2005 *
            .8 ** self._params._t0
        )