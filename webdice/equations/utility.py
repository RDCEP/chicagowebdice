from __future__ import division


class UtilityModel(object):
    """
    UtilityModel base class
    ...
    Properties
    ----------
    utility_discount : array
        Average utility discount rate
    ...
    Methods
    -------
    get_model_values()
    utility()
    utility_discounted()
    """
    def __init__(self, params):
        self._params = params

    @property
    def utility_discount(self):
        """
        R, Average utility discount rate
        ...
        Returns
        -------
        array
        """
        return 1 / ((1 + self._params.prstp) ** (10 * self._params._t0))

    def get_model_values(self, index, data):
        utility = self.utility(data.consumption_pc[index])
        return (
            utility,
            self.utility_discounted(
                utility, self.utility_discount[index], data.population[index]
            )
        )

    def utility(self, consumption_pc):
        """
        U, Period utility function
        ...
        Returns
        -------
        float
        """
        return (
            (1 / (1 - self._params.elasmu + .000001)) *
            consumption_pc ** (1 - self._params.elasmu) + 1
        )

    def utility_discounted(self, utility, utility_discount, l):
        """
        Utility discounted
        ...
        Returns
        -------
        float
        """
        return utility_discount * l * utility


class DiceUtility(UtilityModel):
    pass