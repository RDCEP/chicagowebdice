%{

%simDICE.m

%[vars, param] = simDICE(options)
%Cell => [Struct, Struct]

%}

function [vars, param] = simDICE(options)
  
  % Parse the options into the program
  [param] = parseOptions(options);
  
  % Setup variables for model
  vars = struct;
  vars = param.setup(vars, param);
  
  % Run the model according to the specified run style
  vars = param.run(vars, param);

end

% Parses the options into the program, setting up the appropriate
% parameters, variables, and step functions for the model

% Options is a {cell array}, with alternating strings and values(which may be also strings)
% e.g. options = {'setup','DICE2007Setup'}

% Several options are necessary to the program and must be set, these are:
% paramset, paramsetexo, setup, run, step

% Between these, paramset and paramsetexo govern the default values for
% parameters, setup instantiates the variables for the model, run controls
% the high level structure of the computations, and step controls the
% individual modules (i.e. functions, equations) that make up the model.

function [param] = parseOptions(options)
  % Setup a database in memory of functions
  % db is a struct, function name to function handle
  db = functionDB();
  
  %% Default Options

  % Default parameters
  %param = OptimizeParam();
  %param = OptimizeParamExo(param);
				 
  %param = GlotterParam();
  param = DICE2007Param();
  %param.paramexo = db.('OptimizeParamExo');
  param.paramexo = db.('DICE2007ParamExo');

  % Default variable setup
  param.setup = @DICE2007Setup;
  
  % Default run style
  param.run = @DICE2007Run;
  %param.run = @OptimizeRun;
  
  % Default model steps
  param.steps = @DICE2007Step;
  
  %% Parsing Options
  
  % Major options array: these are the macro-level options above the step functions
  optionsMajor = {'setup','run'};

  % Set up the array of functions that will make up a 'step'
  param.steparray = {};
  %param.steparray = [param.steparray,'GlotterStep_nonlin'];
  %param.steparray = [param.steparray,'GlotterStep'];
  param.steparray = [param.steparray,'DICE2007Step'];
  
  % Iterates through the options
  for i=1:length(options)
    % If one of the options is for setting a 'major option'
    if any(strcmpi(options{i},optionsMajor))
        
      % Set the major option
      param.(options{i}) = db.(options{i+1});
      
    % If one of the options is for setting a 'step option'
    elseif strcmpi(options{i},'step')
      param.steparray = [param.steparray,options{i+1}];
      
    % If one of the options is for setting a 'set' of parameters 
    % (this must be the first option, since it reassigns param)
    elseif strcmpi(options{i},'ps')
      param = db.(options{i+1})();
        
    elseif strcmpi(options{i},'pse')
      param.paramexo = db.(options{i+1});
    
    % Otherwise, the option is for setting an individual parameter
    elseif strcmpi(options{i}, 'param')
      param.(options{i+1}) = options{i+2};
    end
  end
  
  %% Compute Exogenous variables
  param = param.paramexo(param);
  
  %% Build the specific Step Function
  param.steps = @(vars, param, t) buildStepFunction(param.steparray,db,vars,param,t);
end


%% Step Function Generator
% This function builds the step function for a given set of options
% given a list of modules/functions, it executes the functions in order
function vars = buildStepFunction(steparray, db, vars, param, t)
  % For each step function (vars,param,t)=>(vars), run it mutating vars
  
  for i=1:length(steparray)
      vars = db.(steparray{i})(vars, param, t);
  end
  
end

%% Function Database
function [db] = functionDB()

  % To add new functions, either setup or step, we would have to
  % add the functions in this file (or in a file accessible by the
  % simDICE function) and add it to the db struct.

  %% Major options (these are just function handles)
  db.DICE2007Setup = @DICE2007Setup;
  db.MonteCarloSetup = @MonteCarloSetup;

  db.DICE2007Run = @DICE2007Run;
  db.MonteCarloRun = @MonteCarloRun;
  db.OptimizeRun = @OptimizeRun;
  
  %% Parameter sets
  db.DICE2007Param = @DICE2007Param;
  db.GlotterParam = @GlotterParam;
  db.MonteCarloParam = @MonteCarloParam;
  db.OptimizeParam = @OptimizeParam;
  
  %% Exo Parameter sets
  db.DICE2007ParamExo = @DICE2007ParamExo;
  db.MonteCarloParamExo = @MonteCarloParamExo;
  db.OptimizeParamExo = @OptimizeParamExo;
  
  
  %% Step Functions
  % This is an example of a step function
  % Step functions should be stored in this format. we will transition
  % to storing in this format at some point. Hopefully the setup function
  % will be able to be generated from the step functions, in addition to
  % checking all parameters and sorting the step functions into the correct
  % order.
  
  %{
%  (db.DICE2007Economy).func = @DICE2007Economy;
%  (db.DICE2007Economy).in = {};
%  (db.DICE2007Economy).out = {'capital', 'grossoutput'};
%  (db.DICE2007Economy).vars = {'capital', 'grossoutput', 'output'};
  %}

  db.DICE2007Step = @DICE2007Step;
  db.GlotterStep = @GlotterStep;
  db.GlotterStep_nonlin = @GlotterStep_nonlin;
  db.DICE2007Economy = @DICE2007Economy;
  db.DICE2007Emissions = @DICE2007Emissions;
  db.DICE2007Carbon = @DICE2007Carbon;
  db.GlotterCarbon = @GlotterCarbon;
  db.DICE2007Temp = @DICE2007Temp;
  db.DICE2007Damages = @DICE2007Damages;
  db.DICE2007Utility = @DICE2007Utility;
  db.DICE2007Welfare = @DICE2007Welfare;
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
    vars.emissionsIndustrial(t) = 10 * param.sigma(t) * (1 - param.miu(t)) * param.al(t) * (vars.capital(t)^param.gama) * (param.l(t)^(1-param.gama)); % A.10 % Scaled for 10-year time step
    %vars.emissionsIndustrial(t) = param.sigma(t) * (1 - param.miu_2005) * param.al(t) * (vars.capital(t)^param.gama) * (param.l(t)^(1-param.gama)); % A.10
    % A.12
    vars.emissionsTotal(t) = vars.emissionsIndustrial(t) + param.etree(t);
end

function [vars] = DICE2007Carbon(vars, param, t)
  if t~=1
    % A.13
    vars.massAtmosphere(t) = vars.emissionsTotal(t) + param.b11 * vars.massAtmosphere(t-1) + param.b21*vars.massUpper(t-1);
    % A.14
    vars.massUpper(t) = param.b12*vars.massAtmosphere(t-1) + param.b22*vars.massUpper(t-1) + param.b32*vars.massLower(t-1);
    % A.15
    vars.massLower(t) = param.b23*vars.massUpper(t-1) + param.b33*vars.massLower(t-1);
  end
end

function [vars] = GlotterCarbon(vars, param, t)
  if t == 2
    vars.massAtmosphere(1) = vars.massAtmosphere(1) + vars.emissionsTotal(1);
  end
  if t~=1
    vars.massAtmosphere(t-1) = vars.massAtmosphere(t-1) - param.massAtmosphere;
    vars.massUpper(t-1) = vars.massUpper(t-1) - param.massUpper;
    vars.massLower(t-1) = vars.massLower(t-1) - param.massLower;

    vars.massAtmosphere(t) = -param.ka * (vars.massAtmosphere(t-1) - param.Bfact * vars.massUpper(t-1)) + vars.emissionsTotal(t);
    vars.massUpper(t) = param.ka * (vars.massAtmosphere(t-1) - param.Bfact * vars.massUpper(t-1)) - param.kd * (vars.massUpper(t-1) - (vars.massLower(t-1)/param.DeepRat));
    vars.massLower(t) = param.kd * (vars.massUpper(t-1) - (vars.massLower(t-1)/param.DeepRat));
    
    vars.massAtmosphere(t) = vars.massAtmosphere(t) + vars.massAtmosphere(t-1) + param.massAtmosphere;
    vars.massUpper(t) = vars.massUpper(t) + vars.massUpper(t-1) + param.massUpper;
    vars.massLower(t) = vars.massLower(t) + vars.massLower(t-1) + param.massLower;

    vars.massAtmosphere(t-1) = vars.massAtmosphere(t-1)  + param.massAtmosphere;
    vars.massUpper(t-1) = vars.massUpper(t-1) + param.massUpper;
    vars.massLower(t-1) = vars.massLower(t-1) + param.massLower;
  end
end


%function [vars] = NonLinearCarbon(vars, param, t)
%  if t == 1
%    vars.massAtmosphere(1) = vars.massAtmosphere(1) + vars.emissionsTotal(1);
%  end
%  if t ~= 1
%    function [] = Bfactfun()
%      hplus = 
%    end
    
%    vars.massAtmosphere(t) = -param.ka * (vars.massAtmosphere(t-1) - vars.Arat * Bfactfun * vars.massUpper(t-1)) + vars.emissionsTotal(t);
%    vars.massUpper(t) = param.ka * (vars.massAtmosphere(t-1) - vars.Arat * Bfactfun * vars.massUpper(t-1)) - param.kd * (vars.massUpper(t-1) - (vars.massLower(t-1)/param.DeepRat));
%    vars.massLower(t) = param.kd * (vars.massUpper(t-1) - (vars.massLower(t-1)/param.DeepRat));
%  end
%end

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