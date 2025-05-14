%Volume of tank is equal to 200L - meaning the tank level being to high is
%200
TK001_LLH = 200;
%Inital tank volume with the NMP added is 80L
T001_LT = 80;

% Ratio of Active amterial 59.8%
RAM = 0.598;

% Ratio of Binder 1.3%
RB = 0.013;

% Ratio of Conductivie Additive 3.9%
RC = 0.039;

% Ratio of Solvent 35%
RS = 0.35;

% Density of Active Material 2.11 g/cm3
RHOAM = 2.11;

% Density of Binder 1.78 g/cm3
RHOB = 1.78 ;

% Density of Conductivie Additive 1.8-2.1 g/cm3
RHOC = 1.8;

% Density of Solvent 1.03 g/cm3
RHOS = 1.03;

mixingStarted = false;

%Density of entire mix
mixingStarted = true;
pmixGuessed=RS*RHOS + RB*RHOB + RC*RHOC + RAM*RHOAM /RS+ RB +RC + RAM;

%to get deinsity at interval point the density calulation will be modifed
%Starting Tank - 40% of the whatever the amount of active material that wil
%be added -- NOTE: this has been set up so the whole exquation will be 100%
%so solvent calculation has already been completed.

% -first step- Assume Solvent is already in tank - time = 0 mins form 0 add 5% 
%  of the Binder solution every 5 seconds until complete amount of binder is added
pmix1=RS*RHOS + RB*RHOB/RS+ RB;

% t = 40 mins Conductive Additive (carbon black)(viscosity and density parameter to of being met) , 
pmix2=RS*RHOS + RB*RHOB + RC*RHOC /RS+ RB +RC;

% t= 30 minutes active material
pmix3 = RS*RHOS + RB*RHOB + RC*RHOC + RAM*RHOAM /RS+ RB +RC + RAM

% t= 60 minute there will be a slurry.
mixingStarted = false;
%density parameters are met then send to next tank



%first we have the active material which is 40% of the 200ml Tank

%Once the mixing begins and adds in 
%will then wait for 40 mins from the inital start time

%solvent is 40% of the overall active materials
