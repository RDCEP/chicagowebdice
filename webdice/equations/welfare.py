from webdice.params import Dice2007Params


class UtilityModel(object):
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
        return 1 / ((1 + self._params.prstp) ** (10 * self._params.t0))

    def get_model_values(self, index, data, population):
        utility = self.utility(data.consumption_pc[index])
        return (
            utility,
            self.utility_discounted(
                utility, self.utility_discount[index], population
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
            (1 / (1 - self._params.elasmu + .000001)) * consumption_pc ** (1 - self._params.elasmu) + 1
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
