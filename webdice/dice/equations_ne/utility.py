from __future__ import division
import numexpr as ne


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
        self.params = params

    @property
    def utility_discount(self):
        """
        R, Average utility discount rate
        ...
        Returns
        -------
        array
        """
        return 1 / ((1 + self.params.prstp) ** (self.params.ts * self.params.t0))

    def get_model_values(self, i, df):
        utility = self.utility(df.consumption_pc[i])
        return (
            utility,
            self.utility_discounted(
                utility, self.utility_discount[i], df.population[i]
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
        if self.params.elasmu == 1:
            return ne.evaluate('log(consumption_pc)')
        d = 1.0 - self.params.elasmu
        return ne.evaluate('consumption_pc ** d / d + 1')

    def utility_discounted(self, utility, utility_discount, l):
        """
        Utility discounted
        ...
        Returns
        -------
        float
        """
        return ne.evaluate('utility_discount * l * utility')


class Dice2007(UtilityModel):
    pass


class Dice2010(UtilityModel):
    pass


class Dice2013(Dice2010):
    def utility(self, consumption_pc):
        """
        U, Period utility function
        ...
        Returns
        -------
        float
        """
        if self.params.elasmu == 1:
            return ne.evaluate('log(consumption_pc)')
        d = 1.0 - self.params.elasmu
        return ne.evaluate('(consumption_pc ** d - 1) / d - 1')