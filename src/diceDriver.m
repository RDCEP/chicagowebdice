function [v,p] = diceDriver(source,target)
    % source is a csv file, with the arguments to simDICE
    % format of source:
    % 'param', parameter, parameter_value
    
    % Parse input data
    args = parseArguments(source);
    
    % Run SIMDICE
    [v,p] = simDICE(args);
    
    % Get results data
    outputVars = {'emissionsTotal','massAtmosphere','tempAtmosphere','consumptionpercapita'};
    vals = extractVars(v,outputVars);
    
    % Write the results to file
    cell2csv(target, vals, ',');
    
end

% Reads data from csv file and parses into cell array
function [vals] = parseArguments(source)
    f = fopen(source);
    args = textscan(f,'%s');
    vals = cell(length(args{1}),1);
    for i = 1:length(args{1})
        vals{i} = args{1}{i};
        if str2num(vals{i})
            vals{i} = str2num(vals{i});
        end
    end
    fclose(f);
end

% Extracts desired values from cell array and writes into second array
function vals = extractVars(var, outputVars)
    vals = {length(outputVars),length(var.(outputVars{1}))};
    for i = 1:length(outputVars)
        vals(i,1) = {outputVars{i}};
        data = var.(outputVars{i});
        for j = 1:length(data)
            vals(i,j+1) = {data(j)};
        end
    end
end