function [vars] = DICE2007Step(vars, param, t )
    %% This functions steps through the DICE 2007 model
    % one time-step at a time (time-step = 10 years)
    
    vars = DICE2007Economy(vars, param, t);
    vars = DICE2007Emissions(vars, param, t);
    vars = DICE2007Carbon(vars, param, t);
    vars = DICE2007Temp(vars, param, t);
    vars = DICE2007Damages(vars, param, t);
    vars = DICE2007Utility(vars, param, t);
    vars = DICE2007Welfare(vars, param, t);

end

function [vars] = DICE2007Economy(vars, param, t)
    % A.9
  if t ~= 1
    %vars.capital(t) = vars.capital(t-1) * (1 - param.dk) + (param.savings * vars.output(t-1)); 
    vars.capital(t) = (vars.capital(t-1)) * (1 - param.dk)^10 + 10 * (param.savings * vars.output(t-1)); % Scaled for 10-year time step
  end
    vars.grossoutput(t) = param.al(t) * (vars.capital(t)^param.gama) * (param.l(t)^(1-param.gama)); 
  
end

function [vars] = DICE2007Emissions(vars, param, t)
    %display(param.miu(t));
    % A.10
        vars.emissionsIndustrial(t) = 10 * param.sigma(t) * (1 - param.miu(t)) * param.al(t) * (vars.capital(t)^param.gama) * (param.l(t)^(1-param.gama)); 
        % A.10 % Scaled for 10-year time step
                                                                                                                                                       %vars.emissionsIndustrial(t) = param.sigma(t) * (1 - param.miu_2005) * param.al(t) * (vars.capital(t)^param.gama) * (param.l(t)^(1-param.gama)); % A.10
    % A.12
    vars.emissionsTotal(t) = vars.emissionsIndustrial(t) + param.etree(t);
    if t > 1
        vars.carbonEmitted(t) = vars.carbonEmitted(t-1) + vars.emissionsTotal(t);
    end

    % Set miu if out of carbon to emit
    if vars.carbonEmitted(t) > param.fosslim
        %display(t);
        %display(vars.carbonEmitted(t));
        %display(param.fosslim);
        %pause;
        param.miu(t) = 1;
        vars.emissionsTotal(t) = 0;
        vars.carbonEmitted(t) = param.fosslim;
    end

end

function [vars] = DICE2007Carbon(vars, param, t)
  if t~=1
    % A.13
    vars.massAtmosphere(t) = vars.emissionsTotal(t-1) + param.b11 * vars.massAtmosphere(t-1) + param.b21*vars.massUpper(t-1);
    % A.14
    vars.massUpper(t) = param.b12*vars.massAtmosphere(t-1) + param.b22*vars.massUpper(t-1) + param.b32*vars.massLower(t-1);
    % A.15
    vars.massLower(t) = param.b23*vars.massUpper(t-1) + param.b33*vars.massLower(t-1);
  end
end

function [vars] = DICE2007Temp(vars, param, t)
  if t~=1
    % A.16
    vars.forcing(t) = param.fco22x * log2((vars.massAtmosphere(t) + .000001)/param.matPI/log2(2)) + param.forcoth(t);
    % A.17
    vars.tempAtmosphere(t) = vars.tempAtmosphere(t-1) + param.c1 * (vars.forcing(t) - param.lam * vars.tempAtmosphere(t-1) - param.c3 * (vars.tempAtmosphere(t-1) - vars.tempLower(t-1)));
    % A.18
    vars.tempLower(t) = vars.tempLower(t-1) + param.c4 * (vars.tempAtmosphere(t-1) - vars.tempLower(t-1));
  end
end

function [vars] = DICE2007Damages(vars, param, t)
    % miu
    vars.participation(t) = param.partfract(t);
    % A.19
    vars.participationMarkup(t) = vars.participation(t)^(1-param.expcost2);
    % A.5
    vars.damage(t) = 1/( 1 + param.a1 * vars.tempAtmosphere(t) + param.a2 * vars.tempAtmosphere(t)^param.a3);
    % A.6
    vars.abatement(t) = vars.participationMarkup(t) * param.gcost1(t) * (param.miu(t) ^ param.expcost2);
    % A.4
    vars.output(t) = vars.grossoutput(t)*vars.damage(t)*(1-vars.abatement(t));
end

function [vars] = DICE2007Utility(vars, param, t)
    vars.investment(t) = (param.savings) * vars.output(t);
    % A.7
    vars.consumption(t) = (1 - param.savings) * vars.output(t);
    % A.8
    vars.consumptionpercapita(t) = 1000* vars.consumption(t) / param.l(t);
    % A.3
    vars.utility(t) = param.l(t) * ((vars.consumptionpercapita(t))^(1-param.elasmu) / (1-param.elasmu));
    vars.utilitydiscounted(t) = vars.utility(t) * param.rr(t);
end

function [vars] = DICE2007Welfare(vars, param, t)
    % A.2
    
    % A.1
    vars.welfare = -sum(vars.utility .* param.rr);
end
