import numpy as np
from webdice.params import Dice2007Params


PARAMS = Dice2007Params()


class EmissionsModel(object):
    def __init__(self):
        pass

    @property
    def emissions_deforest(self):
        """
        E_land, Emissions from deforestation
        ...
        Returns
        -------
        array
        """
        return PARAMS._emissions_deforest_2005 * (1 - .1) ** PARAMS.t0

    def get_emissions_values(self, index, data):
        emissions_ind = self.emissions_ind(
            data.intensity[index], data.miu[index], data.gross_output[index]
        )
        emissions_total = self.emissions_total(
            emissions_ind, self.emissions_deforest
        )
        carbon_emitted = self.carbon_emitted(emissions_total, index, data)
        if carbon_emitted > PARAMS.fosslim:
            emissions_total = 0.0
            carbon_emitted = PARAMS.fosslim
        return (
            emissions_ind,
            emissions_total,
            carbon_emitted,
        )

    def emissions_ind(self, intensity, miu, gross_output):
        """
        E_ind, Industrial emissions, GtC
        ...
        Returns
        -------
        float
        """
        return intensity * (1. - miu) * gross_output

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