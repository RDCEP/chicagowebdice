class ConsumptionModel(object):
    """
    ConsumptionModel base class
    ...
    Properties
    ----------
    initial_values : array
        Values for consumption_discount and investment at t=0
    ...
    Methods
    -------
    get_model_values()
    consumption_pc()
    consumption_discount()
    investment()
    """
    def __init__(self, params):
        self._params = params

    @property
    def initial_values(self):
        return (
            1,
            self._params._output_2005 * self._params.savings,
        )

    def get_model_values(self, index, data):
        consumption = self.consumption(data.output[index], self._params.savings)
        consumption_pc = self.consumption_pc(
            consumption, data.population[index]
        )
        if index == 0:
            return (consumption, consumption_pc,) + self.initial_values
        return (
            consumption,
            consumption_pc,
            self.consumption_discount(
                data.consumption_pc[0], consumption_pc, index
            ),
            self.investment(self._params.savings, data.output[index]),
        )

    def consumption(self, output, savings):
        """
        C, Consumption, trillions $USD
        ...
        Returns
        -------
        float
        """
        return output * (1.0 - savings)

    def consumption_pc(self, consumption, population):
        """
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return 1000 * consumption / population

    def consumption_discount(self, c0, c1, i):
        """Discount rate for consumption"""
        return 1 / (
            1 + (self._params.prstp * 100 + self._params.elasmu * (
                (c1 - c0) / 10 / c0
            )) / 100
        ) ** (10 * i)

        # Ramsey discount from SCC paper
        # return np.exp(-(elasmu / (i + .000001) * np.log(
        #     c1 / c0) / 10 + prstp) * i * 10)

        # Constant rate from SCC paper
        # return 1 / ((1 + .03) ** (i * 10))

    def investment(self, savings, output):
        """
        I, Investment, trillions $USD
        ...
        Returns
        -------
        float
        """
        return savings * output

class DiceConsumption(ConsumptionModel):
    pass