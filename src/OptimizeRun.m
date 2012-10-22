function [vars] = OptimizeRun(vars, param)
  % This runs the model with optimization for a given variable
  % using the fmincon function from the optimization toolbox

  % we should be able to specify the exact algorithm used

  % Set up the optimization values

  x0 = param.optInit; % Initial value
  %myRun = @(x) Run(param.optVariable, x, vars, param); % Welfare function w/ param setting
  myRun = @(x) Run('miu', x, vars, param);
  
  % Set up optimization options
  fitoptions=optimset('Display','iter','TolX',1e-10,'TolFun',1e-20,'MaxIter',param.maxIter,'Algorithm','sqp');

  % Run optimization
  % x = fmincon(fun, x0, A,       b,       Aeq,beq,lb,       ub,       nonlcon,options)
  % x = fmincon(myRun,
  x = fmincon(myRun, x0, param.A, param.b, [], [], param.lb, param.ub, [], fitoptions);

  param.(param.optVariable) = x;
  vars.x = x;
  
  % Generate the other variables in the model
  for t = 1:param.tmax
      vars = param.steps(vars, param, t);
  end
  
end

% This is the function that will be optimized
% we want to set a variable or param as x
% and get welfare (according to welfare function)
function wlf = Run(variablename,x, vars, param)
  param.(variablename) = x;
  
  for t = 1:param.tmax
    vars = param.steps(vars, param, t);
  end

  wlf = vars.welfare;
end