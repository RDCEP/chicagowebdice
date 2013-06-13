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
        return emissions_ind, emissions_total

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
