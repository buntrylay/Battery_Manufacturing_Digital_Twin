classdef MixingSimulation
    properties
        % tank properties
        Volume = 200;            % in Litres

        % expected ratios
        ActiveMaterialRatio = 0.598; % should take up 59.8 % of the tank
        BinderRatio = 0.013;
        ConductiveRatio = 0.039;
        SolventRatio = 0.35;
        
        % density constants of each type of components in the slurry
        % mixture.
        RHOAM = 2.11;            % unit: g/cm3
        RHOB = 1.78;
        RHOC = 1.8;
        RHOS = 1.03;
        
        % actual volume in the mixing tank
        SolventVolume
        BinderVolume = 0;
        CarbonBlackVolume = 0;
        ConductiveVolume = 0;
        ActiveMaterialVolume = 0;

        % time passed
        totalTime = 0;
    end
    methods
        function obj = initialise(obj)
            obj.SolventVolume = obj.SolventRatio * obj.Volume; % solvent is added at the start
            fprintf("Starting time: %s\n", datetime('now')); % start mixing simulation
            fprintf("Initialise tank and add solvent (%.2f L)\n", obj.SolventVolume);
            obj.printDensity();
        end
        function obj = runSimulation(obj)
            stepPercentage = 0.05;
            pauseTime = 5; % 5 seconds = 1 unit of time in simulation

            % Simulate binder addition (5% every 5s for 40min → 20 steps)
            fprintf("\nAdding Binder...\n");
            obj = obj.addInSteps('BinderVolume', obj.BinderRatio, stepPercentage, pauseTime);
            
            % Simulate carbon black addition (30min → 20 steps)
            fprintf("\nAdding Carbon Black...\n");
            obj = obj.addInSteps('CarbonBlackVolume', obj.ConductiveRatio, stepPercentage, pauseTime);

            % Simulate conductive additive addition (30min → 20 steps)
            fprintf("\nAdding Conductive Additive...\n");
            obj = obj.addInSteps('ConductiveVolume', obj.ConductiveRatio, stepPercentage, pauseTime);

            % Simulate active material addition (60min → 20 steps)
            fprintf("\nAdding Active Material...\n");
            obj = obj.addInSteps('ActiveMaterialVolume', obj.ActiveMaterialRatio, stepPercentage, pauseTime);

            fprintf("\nFinal Slurry Density:\n");
            obj.printDensity();
        end
        function obj = addInSteps(obj, propertyName, ratio, stepPercent, pauseSec)
            totalVolumeToAdd = ratio * obj.Volume;
            stepVolume = stepPercent * totalVolumeToAdd;
            numSteps = 1 / stepPercent;
            
            for i = 1:numSteps
                obj.(propertyName) = obj.(propertyName) + stepVolume;
                obj.totalTime = obj.totalTime + pauseSec;
                fprintf("Time %3d s: Added %.2f L to %s\n", obj.totalTime, stepVolume, propertyName);
                obj.printDensity();
                pause(pauseSec); % Simulate real-time progression
            end
        end
        function printDensity(obj)
            totalMass = ...
                obj.SolventVolume * obj.RHOS + ...
                obj.BinderVolume * obj.RHOB + ...
                obj.CarbonBlackVolume * obj.RHOC + ...
                obj.ConductiveVolume * obj.RHOC + ...
                obj.ActiveMaterialVolume * obj.RHOAM;

            totalVolume = ...
                obj.SolventVolume + ...
                obj.BinderVolume + ...
                obj.CarbonBlackVolume + ...
                obj.ConductiveVolume + ...
                obj.ActiveMaterialVolume;

            if totalVolume > 0
                density = totalMass / totalVolume; % general formula
            else
                density = 0;
            end

            fprintf("Current density: %.4f g/cm³\n\n", density);
        end
    end
end