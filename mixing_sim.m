classdef MixingSimulation
    properties
        % Tank properties
        Volume = 200;  % Total volume in Litres
        
        % Expected ratios
        AM_ratio = 0.495;
        PVDF_ratio = 0.05;
        CB_ratio = 0.045;
        NMP_ratio = 0.41;

        % Density (g/cm³)
        RHO_AM = 2.26;
        RHO_CB = 1.8;
        RHO_PVDF = 1.78;
        RHO_NMP = 1;

        % Empirical coefficients
        a = 0.9;  % AM coefficient
        b = 2.5;  % PVDF coefficient
        c = 0.3;  % CB coefficient
        s = -0.5; % Solvent coefficient

        % Component volumes
        NMP = 0;
        PVDF = 0;
        CB = 0;
        AM = 0;
        
        % Simulation results
        results = struct();
        totalTime = 0;
    end

    methods
        function obj = MixingSimulation()
            % Initialize with only NMP
            obj.NMP = obj.NMP_ratio * obj.Volume;
        end

        function obj = run(obj, stepPercent, pauseSec)
            if nargin < 2, stepPercent = 0.02; end
            if nargin < 3, pauseSec = 0.001; end

            obj = obj.addInSteps('PVDF', obj.PVDF_ratio, stepPercent, pauseSec);
            obj = obj.addInSteps('CB', obj.CB_ratio, stepPercent, pauseSec);
            obj = obj.addInSteps('AM', obj.AM_ratio, stepPercent, pauseSec);
        end

        function obj = addInSteps(obj, component, ratio, stepPercent, pauseSec)
            totalVolumeToAdd = ratio * obj.Volume;
            stepVolume = stepPercent * totalVolumeToAdd;
            numSteps = round(1 / stepPercent);

            for i = 1:numSteps
                obj.totalTime = obj.totalTime + pauseSec;
                obj.(component) = obj.(component) + stepVolume;

                % Simulated data
                timestamp = datestr(now, 'yyyy-mm-dd HH:MM:SS');
                temperature = round(20 + (25-20) * rand, 2);
                pressure = round(1 + (2-1) * rand, 2);
                rpm = randi([300, 600]);
                density = obj.calculateDensity();
                viscosity = obj.calculateViscosity();
                yieldStress = obj.calculateYieldStress();

                % Store result
                resultStruct = struct(...
                    'TimeStamp', timestamp, ...
                    'Duration', round(obj.totalTime, 2), ...
                    'AM', round(obj.AM, 3), ...
                    'CB', round(obj.CB, 3), ...
                    'PVDF', round(obj.PVDF, 3), ...
                    'NMP', round(obj.NMP, 3), ...
                    'Temperature', temperature, ...
                    'Pressure', pressure, ...
                    'Speed_RPM', rpm, ...
                    'Density', round(density, 4), ...
                    'Viscosity_mPa_s', round(viscosity, 2), ...
                    'Yield_Stress_Pa', round(yieldStress, 2) ...
                );

                % Append results
                obj.results(end+1) = resultStruct;

                pause(pauseSec);
            end
        end

        function density = calculateDensity(obj)
            % Mass of each component (g)
            m_NMP = obj.NMP * obj.RHO_NMP;
            m_PVDF = obj.PVDF * obj.RHO_PVDF;
            m_CB = obj.CB * obj.RHO_CB;
            m_AM = obj.AM * obj.RHO_AM;

            totalMass = m_NMP + m_PVDF + m_CB + m_AM;
            totalVolume = obj.NMP + obj.PVDF + obj.CB + obj.AM;
            
            if totalVolume > 0
                density = totalMass / totalVolume;
            else
                density = 0;
            end
        end

        function viscosity = calculateViscosity(obj)
            maxSolidFraction = 0.63;
            intrinsicViscosity = 3.0;

            totalVolume = obj.NMP + obj.PVDF + obj.CB + obj.AM;
            if totalVolume == 0
                viscosity = 0;
                return;
            end

            % Calculate solid volume fraction
            solidVolume = obj.PVDF + obj.CB + obj.AM;
            phi = solidVolume / totalVolume;

            % Cap phi to avoid division by 0
            if phi >= maxSolidFraction
                phi = maxSolidFraction - 0.001;
            end

            try
                % Krieger-Dougherty equation
                viscosity = (1 - (phi / maxSolidFraction)) ^ (-intrinsicViscosity * maxSolidFraction) * 2;
            catch
                viscosity = inf;
            end
        end

        function yieldStress = calculateYieldStress(obj)
            % Mass of each component (g)
            m_NMP = obj.NMP * obj.RHO_NMP;
            m_PVDF = obj.PVDF * obj.RHO_PVDF;
            m_CB = obj.CB * obj.RHO_CB;
            m_AM = obj.AM * obj.RHO_AM;

            yieldStress = (obj.a * m_AM) + (obj.b * m_PVDF) + (obj.c * m_CB) + (obj.s * m_NMP);
        end

        function saveToJSON(obj, filename)
            if nargin < 2, filename = "mixing_simulation.json"; end

            % Convert to JSON
            jsonStr = jsonencode(obj.results);

            % Save to file
            fid = fopen(filename, 'w');
            if fid == -1
                error('Could not open file for writing.');
            end
            fwrite(fid, jsonStr, 'char');
            fclose(fid);
            
            fprintf('Simulation data saved to %s\n', filename);
        end
    end
end
