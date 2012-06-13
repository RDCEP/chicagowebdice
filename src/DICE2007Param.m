% Creates a param struct with the default parameters from DICE-2007
% specifically the GAMS code at econ.yale.edu/~nordhaus/DICE2007_programs/

function [param] = DICE2007Param()

    param.steparray = {};
    
    %%%%%
    % Scalars
    %%%%%
    
    %% Preferences
    param.elasmu = 2.0; % Elasticity of marginal utility of consumption
    param.prstp = .015; % Initial rate of social time preference per year
    
    % the following were settings I made that were not in the GAMS code
    % most come from Bob Kopp's matDICE
    param.tmax = 60; % Time periods, in decades (60 * 10 = 600 years)
    param.numScen = 1; % Number of scenarios to run
    param.savings = .2; % Savings rate (constant)
    param.miu_2005 = 0; % emission control rate (fraction of uncontrolled emissions)
    
    %% Population and technology
    param.pop0 = 6514; % 2005 world population millions
    param.gpop0 = .35; % growth rate of population per decade
    param.popasym = 8600; % asymptotic population
    
    param.a0 = .02722; % Initial level of total factor productivity
    param.ga0 = .092; % Initial growth rate for technology per decade
    param.dela = .001; % Decline rate of technological change per decade
    
    param.dk = .100; % Depreciation rate on capital per year
    param.gama = .300; % Capital elasticity in production function
    
    param.q0 = 61.1; % 2005 world gross output trill 2005 US dollars
    param.k0 = 137.; % 2005 value capital trill 2005 US dollars
    
    %% Emissions
    param.sig0 = .13418; % CO2-equivalent emissions-GNP ratio 2005 (effectively intensity)
    param.gsigma = -.0730; % Initial growth of sigma per decade
    param.dsig = .003; % Decline rate of decarbonization per decade
    param.dsig2 = .000; % Quadratic term in decarbonization
    param.eland0 = 11.000; % Carbon emissions from land 2005 (GtC per decade)
    param.e2005 = 84.1910; % Year 2005 Emissions
    
    %% Carbon Cycle    
    param.mat2000 = 808.9; % Concentration in atmosphere 2005 (GtC)
    param.mu2000 = 1255; % Concentration in upper strata 2005 (GtC)
    param.ml2000 = 18365; % Concentration in lower strata 2005 (GtC)
    
    param.matPI = 278 * 2.13; % Preindustrial concentration in atmosphere 2005 (GtC)
    
    % Carbon cycle transition matrix
    % 1 = atmosphere
	% 2 = upper ocean
	% 3 = lower ocean
	% each carbon parameter has two values, the source and the destination
	% e.g. carbon12 is the carbon going FROM the atmosphere TO the upper ocean
    
    param.b11 = .810712;
    param.b12 = .189288;
    param.b21 = .097213;
    param.b22 = .852787;
    param.b23 = .05;
    param.b32 = .003119;
    param.b33 = .996881;
    
    %% Climate model
    param.t2xco2 = 3; % Equilibrium temp impact of CO2 doubling (degrees C)
    param.fex0 = -.06; % Estimate of 2000 forcings of non-CO2 GHG
    param.fex1 = .30; % Estimate of 2100 forcings of non-CO2 GHG
    
    param.tocean0 = .0068; % 2000 lower strat. temp change (C) from 1900
    param.tatm0 = .7307; % 2000 atmospheric temp change (C) from 1900
    
    param.c1 = .220; % Climate-equation coefficient for upper level
    param.c3 = .300; % Transfer coefficient upper to lower stratum
    param.c4 = .050; % Transfer coefficient for lower level
    
    param.fco22x = 3.8; % Estimated forcings of equilibrium CO2 doubling
    
    % Climate damage parameters, calibrated for quadratic at 2.5 C for 2105
    param.a1 = 0.00000; % Damage intercept
    param.a2 = 0.0028388; % Damage quadratic term
    param.a3 = 2.00; % Damage exponent
    
    %% Abatement cost
    param.expcost2 = 2.8; % Exponent of control cost function
    param.pback = 1.17; % Cost of backstop 2005, thousands of $ per tC 2005
    param.backrat = 2; % Ratio initial to final backstop cost
    param.gback = .05; % Initial cost decline backstop, % per decade
    param.limmiu = 1; % Upper limit on control rate
    
    %% Participation
    param.partfract1 = 1; % Fraction of emissions under control regime 2005
    param.partfract2 = 1; % Fraction of emissions under control regime 2015
    param.partfract21 = 1; % Fraction of emissions under control regime 2205
    param.dpartfract = 0; % Decline rate of participation
    
    %% Availability of fossil fuels
    param.fosslim = 6000; % Maximum cumulative extraction fossil fuels
    
    %% Scaling and inessential parameters
    param.scale1 = 194; % Scaling coefficient in the objective function
    param.scale2 = 381800; % Scaling coefficient in the objective function
    
    %% Initialized values for endogenous variables
    param.capital = param.k0;
    param.output = param.q0;

    param.massAtmosphere = param.mat2000;
    param.massUpper = param.mu2000;
    param.massLower = param.ml2000;

    param.tempAtmosphere = param.tatm0;
    param.tempLower = param.tocean0;


    
end
