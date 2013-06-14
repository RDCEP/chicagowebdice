import numpy as np


class ProductivityModel(object):
    def __init__(self, params):
        self._params = params

    @property
    def population_growth(self):
        """
        L_g, Population growth factor
        ...
        Returns
        -------
        array
        """
        return (
            (np.exp(self._params._population_growth * self._params.t0) - 1) /
            (np.exp(self._params._population_growth * self._params.t0))
        )

    @property
    def population(self):
        """
        L, Population.
        ...
        Returns
        -------
        array
        """
        return self._params._population_2005 * (1 - self.population_growth) + \
               self.population_growth * self._params.popasym

    @property
    def productivity_growth(self):
        """
        A_g, Growth rate of total factor productivity.
        ...
        Returns
        -------
        array
        """
        return self._params._productivity_growth * np.exp(
            -(self._params.productivity_decline / 100.) * 10 * self._params.t0
        )

    @property
    def intensity_decline(self):
        """
        sigma_g, Rate of decline of carbon intensity
        ...
        Returns
        -------
        array
        """
        return (
            self._params._intensity_growth * np.exp(
                -(self._params.intensity_decline_rate / 100) * 10 *
                self._params.t0 - self._params._intensity_quadratic * 10 * (self._params.t0 ** 2)
            )
        )

    def get_model_values(self, index, data, backstop):
        if index > 0:
            carbon_intensity = data.carbon_intensity[index - 1] / (
                1 - self.intensity_decline[index]
            )
            productivity = data.productivity[index - 1] / (
                1 - self.productivity_growth[index - 1])
            capital = self.capital(
                data.capital[index - 1], self._params.depreciation,
                data.investment[index - 1]
            )
        else:
            carbon_intensity = self._params._intensity_2005
            productivity = self._params._productivity
            capital = self._params._capital_2005
        backstop_growth = (
            backstop * data.carbon_intensity[index] / self._params.abatement_exponent
        )
        gross_output = self.gross_output(
            data.productivity[index], data.capital[index], self._params._output_elasticty,
            self.population[index]
        )
        return (
            carbon_intensity,
            productivity,
            capital,
            backstop_growth,
            gross_output,
        )

    def capital(self, capital, depreciation, investment):
        """
        K(t), Capital, trillions $USD
        ...
        Returns
        -------
        Float
        """
        return capital * (1 - depreciation) ** 10 + 10 * investment

    def gross_output(self, productivity, capital, output_elasticty, population):
        """
        Gross output
        ...
        Returns
        -------
        float
        """
        return (
            productivity * capital ** output_elasticty *
            population ** (1 - output_elasticty)
        )

