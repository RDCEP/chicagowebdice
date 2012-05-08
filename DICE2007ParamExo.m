% Creates a param struct with exfdsaogenous variables
% from a previous parameter w/o exogenous variables

function [param] = DICE2007ParamExo(param)

    %%%%%
    % Parameters dependent upon other parameters
    %%%%%
    
    param.lam = param.fco22x/ param.t2xco2; % Climate model parameter
    
    %%%%%
    % Exogenous Variables
    %%%%%
    
    %% Set up the arrays for the exogenous variables
    
    param.miu = zeros(param.tmax, 1); % Emissions control rate (zero for now)
    %param.miu = [.0047,.1660,.2017,

    % Population
    param.gfacpop = zeros(param.tmax, 1); % Growth factor population
    param.l = zeros(param.tmax, 1); % Labor (population)
    
    % Productivity
    param.ga = zeros(param.tmax, 1); % Growth rate of productivity from 0 to tmax
    param.al = zeros(param.tmax, 1); % level of total factor productivity
    
    % Climate
    param.gsig = zeros(param.tmax, 1); % Cumulative improvement of energy efficiency
    param.sigma = zeros(param.tmax, 1); % CO2-equivalent-emissions output ratio
    param.gcost1 = zeros(param.tmax, 1); % growth of cost factor
    param.etree = zeros(param.tmax, 1); % Emissions from deforestation
    
    param.rr = zeros(param.tmax, 1); % Average utility social discount rate
    param.forcoth = zeros(param.tmax, 1); % Exogenous forcing for other greenhouse gases
    param.partfract = zeros(param.tmax, 1); % Fraction of emissions in control regime
    
    %% Step through the time steps to set up endogenous variable arrays
    % This section should be replaced to eliminate the for loop with array
    % operations
    for i = 1:param.tmax
        param.miu(i) = param.miu_2005;
        %param.miu(i) = 1;
        
        param.gfacpop(i) = (exp(param.gpop0*(i-1))-1)/exp(param.gpop0*(i-1));
        param.l(i) = param.pop0 * (1 - param.gfacpop(i)) + param.gfacpop(i) * param.popasym;
        
        
        param.gsig(i) = param.gsigma * exp(-param.dsig * 10 * (i - 1) - param.dsig2 * 10 * ((i - 1)^2));
        param.etree(i) = param.eland0 * (1 - 0.1)^(i-1);
	param.rr(i) = 1 / ((1 + param.prstp)^(10 * (i-1)));
        
        param.ga(i) = param.ga0 * exp(-param.dela * 10 * (i-1));
        if i == 1
            param.al(i) = param.a0;
            param.sigma(i) = param.sig0;
        else
            param.al(i) = .95 * param.al(i-1) / (1 - param.ga(i-1));
	    %param.al(i) = param.a0;
            param.sigma(i) = param.sigma(i-1)/(1-param.gsig(i));
        end
        
        if i < 12
            param.forcoth(i) = param.fex0 + .1 * (param.fex1 - param.fex0) * (i-1);
        elseif i >= 12
            param.forcoth(i) = param.fex0 + .36;
        end
        
        if i == 1
            param.partfract(i) = param.partfract1;
        elseif i < 25
            param.partfract(i) = param.partfract21 + (param.partfract2 - param.partfract21) * exp(-param.dpartfract * (i-2));
        else
            param.partfract(i) = param.partfract21;
        end
        
        param.gcost1(i) = (param.pback * param.sigma(i) / param.expcost2) * (param.backrat - 1 + exp(-param.gback * (i-1))/param.backrat);
        
    end

end