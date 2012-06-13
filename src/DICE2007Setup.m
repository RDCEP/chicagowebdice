% Sets up the appropriate arrays for the endogenous variables for 
% the DICE 2007 model, modifying the struct vars to hold the arrays

function [vars] = DICE2007Setup(vars, param)

    %% We declare the endogenous variables as members of struct vars
    
    vars.welfare = 0;
    vars.utility = zeros(param.tmax, 1);
	
    vars.consumption = zeros(param.tmax, 1);
    vars.consumptionpercapita = zeros(param.tmax, 1);
    vars.investment = zeros(param.tmax, 1);
    vars.capital = zeros(param.tmax, 1);
    vars.grossoutput = zeros(param.tmax, 1);
    vars.output = zeros(param.tmax, 1);
    
    vars.abatement = zeros(param.tmax, 1);
    vars.emissionsIndustrial = zeros(param.tmax, 1);
    vars.emissionsTotal = zeros(param.tmax, 1);
    vars.carbonEmitted = zeros(param.tmax, 1);
    vars.emissionsControl = zeros(param.tmax, 1);
    
    vars.damage = zeros(param.tmax, 1);
    
    vars.participation = zeros(param.tmax, 1);
    vars.participationMarkup = zeros(param.tmax, 1);
    vars.emissionsOutputRatio = zeros(param.tmax, 1);
    
    vars.forcing = zeros(param.tmax, 1);
    vars.tempAtmosphere = zeros(param.tmax, 1);
    vars.tempLower = zeros(param.tmax, 1);
    
    vars.massAtmosphere = zeros(param.tmax, 1);
    vars.massUpper = zeros(param.tmax, 1);
    vars.massLower = zeros(param.tmax, 1);

    % for each endogenous variable, if there is a field of
    % param that has the same name, take it as its initial value
    
    for f = fieldnames(vars)'
      if isfield(param,char(f))
	      vars.(char(f))(1) = param.(char(f));
      end
    end
    
end
