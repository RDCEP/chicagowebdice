function vars = DICE2007Run(vars, param)
    % Step through standard run

    for t = 1:param.tmax
        vars = param.steps(vars, param, t);
    end

end
