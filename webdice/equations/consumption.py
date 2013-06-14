from webdice.params import Dice2007Params


PARAMS = Dice2007Params()


class ConsumptionModel(object):
    def __init__(self, params):
        self._params = params

    def get_model_values(self, index, data, prstp, elasmu, population, savings):
        consumption_pc = self.consumption_pc(
            data.consumption[index], population
        )
        return (
            consumption_pc,
            self.consumption_discount(
                prstp, population, elasmu,
                data.consumption_pc[0], consumption_pc, index
            ),
            self.investment(savings, data.output[index], index),
        )

    def consumption_pc(self, consumption, population):
        """
        c, Per capita consumption, thousands $USD
        ...
        Returns
        -------
        float
        """
        return 1000 * consumption / population

    def consumption_discount(self, prstp, population, elasmu, c0, c1, i):
        """Discount rate for consumption"""
        if i == 0:
            return 1
        return 1 / (
            1 + (prstp * 100 + elasmu * (
                (c1 - c0) / 10 / c0
            )) / 100
        ) ** (10 * i)

        # Ramsey discount from SCC paper
        # return np.exp(-(elasmu / (i + .000001) * np.log(
        #     c1 / c0) / 10 + prstp) * i * 10)

        # Constant rate from SCC paper
        # return 1 / ((1 + .03) ** (i * 10))

    def investment(self, savings, output, i):
        """
        I, Investment, trillions $USD
        ...
        Returns
        -------
        float
        """
        if i == 0:
            return savings * self._params._output_2005
        return savings * output

