# openberg-project-apr2026

This repository provides explanations how to simulate iceberg drift and deterioration, suggestions on model settings and input, and example code, based on 3.5 years of doctoral studies conducted as part of the "RareIce" project at the Norwegian University of Science and Technology (Thesis: in Herrmannsdoerfer [2026]). The repository contains a short explanation on the iceberg model, the simulation platform, and suggestions on the model setup, input and initial conditions.
- Herrmannsdörfer, L. (2026), Impact of Environmental Inputs on Iceberg Drift and Deterioration Simulations, Doctoral thesis at NTNU, (url will follow).
  
## Iceberg drift and deterioration model
Iceberg drift and deterioration models simulate the icebergs movement and its decay based on initial conditions of the iceberg properties (iceberg size, position, time). The iceberg properties are updated every simulation time step (e.g. 1-hourly) with the physical equations, and the environmental input data (e.g. ocean currents, wind, sea ice, waves). Initial conditions and environmental data has to be supplied to the iceberg model. The iceberg model setup (selected physical processes and coefficients) can be adapted based on the application. The iceberg model outputs drift trajectories. The details on the herein used iceberg model, “OpenBerg”,  can be read under following references. OpenBerg is a component of the framework “Opendrift”.
-	Description of OpenDrift framework and code: https://opendrift.github.io/autoapi/opendrift/models/openberg/
-	Description of model physics and validation: Keghouche, I., F. Counillon, and L. Bertino (2010), Modeling dynamics and thermodynamics of icebergs in the Barents Sea from 1987 to 2005, J. Geophys. Res., 115, C12062, doi: https://doi.org/10.1029/2010JC006165. 
-	Background on iceberg simulations, model description and application: Herrmannsdoerfer [2026]
  
OpenBerg was adapted based on the findings in Herrmannsdörfer [2026]. The adapted version can be found under: https://github.com/lia-f-h/opendrift_2026. This version features an improved sea-ice-drag formulation and switches to dis/en-able all drift processes. In detail, the changes are:
- Modified sea-ice-drag formulations with flexible threshold for a lock-in, and a concentration-dependent sea-ice-drag coefficient. The lock-in threshold default is set to 0.7 (before: 0.9), in line with small Arctic icebergs.
- Switches to disable the drag by sea ice, water and wind, similarly to what was implemented for wave_rad. The default is set to True, so that the drag is automatically enabled, but can be set to False by expert users.
- The initial iceberg velocity is set to the velocity of sea ice in concentrations larger the threshold of iceberg lock-in. It is also set to the sea ice velocity when the initial velocity would be zero otherwise due to missing current, input, stokes input (which are usually used to calculate the initial velocity), the sea-ice-drag is enabled, and the concentration is larger 15%.
Also:
- The fallback values of water, wind and sea ice velocities are set to zero (instead of None) for using switches for drag processes suggested above.
- Default for wave_rad is set to False to disable highly unreliable wave forces. The default of stokes_drift is set to True as it proved to contribute significantly in one of the studied cases. The default of melting is set to True, as most iceberg drifts are impacted by melting.

See information of how to install the model under Section “Simulation platform”. The code in this repository provides examples of how to run the model and visualise the results.

## Iceberg model setup
Based on the research in Herrmannsdoerfer [2026], following model setup is suggested. The setup is in large parts implemented in https://github.com/lia-f-h/opendrift_2026 (Iceberg model) and this repository (code and simulation results). 
Iceberg drift processes: By wind, ocean current, sea ice, Coriolis force, stokes drift. The improved sea-ice-drag formulation is described and tested in the thesis. Drift due to reflected waves is neglected due to large error connected to the wave drag equation. Effects of sea surface slope are excluded due to missing implementation in OpenBerg.
Iceberg deterioration processes: by wave erosion, buoyant vertical convection, and forced convection by water
Drag coefficients: Following the promising simulation outcomes in my thesis, drag coefficients for water and air are set to Ca, Cw=1.5. The sea ice drag coefficient Csi is defined in relation to CI: Csi(CI) = 100 · (CI - CIlower)/( CIupper - CIlower)
With CIlower=0.15 and CIupper=0.7. (CIupper=0.7 is not implemented as default in the model and should be specified explicitly.)

## Initial iceberg conditions: 
Initial iceberg conditions need to be supplied to the iceberg model. Individual icebergs can be seeded by supplying the iceberg properties: time, latitude, longitude, length (width, sail, draft). To receive iceberg statistics (large amounts of trajectories), those simulations are repeated using iceberg properties, sampled from size distributions and glacial release rates, as provided in Monteban [2020]. Note that OpenBerg can parallelise simulations of icebergs of similar starting time, approximate initial position (within a radius), and varied initial sizes. See the example code for clarification on how to define the initial conditions.
- D. Monteban, R. Lubbad, I. Samardzija and S. Løset, ‘Enhanced iceberg drift modelling in the Barents Sea with estimates of the release rates and size characteristics at the major glacial sources using Sentinel-1 and Sentinel-2,’ Cold Regions Science and Technology, vol. 175, p. 103 084, 2020, ISSN: 0165-232X. DOI: 10.1016/j.coldregions.2020.103084 

## Input data
Environmental input needs to be supplied to the iceberg model. From Herrmannsdörfer [2026], it is suggested to create “Iceberg-ensembles” based on varied input. This means that the same iceberg trajectories and statistics should be run with varied inputs, to account for the uncertainty in the input and the iceberg model. Depending on the simulation goal and application, especially ocean and sea ice data should be varied. Variation of wind input is suggested for some applications (see Herrmannsdörfer [2026]). The recommended input data for use in the European Arctic is provided below.

#### Ocean models	 	 	 
Arctic Ocean Physics Reanalysis	(Topaz4b, 1991-2026), Arctic Ocean Physics Analysis and Forecast (Topaz5, 2021-present), Global Ocean Physics Reanalysis	(GLORYS, 1993-present), 
Global Ocean Physics Analysis and Forecast	(Mercator, 2020-present)
#### Seperate sea ice models	 	 	 
Arctic Ocean Sea Ice Reanalysis	 (neXtSIM R, 1992-2024), Arctic Ocean Sea Ice Analysis and Forecast	 (neXtSIM F, 2020-2026)
#### Wind models 	 	 
ERA5, CARRA
#### Wave models (Stokes drift)*	 	 	
Arctic Ocean Wave Analysis and Forecast	(ARC MFC WAM,	2017-present), Arctic Ocean Wave Hindcast	ERA5 (ARC MFC WAM,	1977-present), Global Ocean Wave Analysis and Forecast (mfwam, Nov 2022-present), Global Ocean Wave Reanalysis	WAVERYS (1980-present), *Select one wave model. Stokes drift proved to be very similar in those models.


## Simulation platform
- [Expert use]: Openberg can be downloaded and installed on your local machine as a python package. Follow the installation instructions (https://opendrift.github.io/install.html), but clone the repository https://github.com/lia-f-h/opendrift_2026 instead. Note that you may have to resolve the dependencies manually, depending on your python installation.
- [Easy use]: The service Edito (European Digital Twin Ocean, https://www.edito.eu/) features a convenient pre-installation of OpenDrift and connection to Copernicus Marine, providing ocean and sea ice data. Edito also has an option to use a custom version of OpenBerg. Note that your code and simulation results are not backed up by Edito and might disappear! Download your files regularly or use version control with Github (recommended).
  
#### Additional instructions for Edito:
-	Sign up for Edito: https://www.edito.eu/
-	If you have not already, sign up on Copernicus Marine: https://marine.copernicus.eu/ 
-	Go to Edito datalab/Service catalog: https://datalab.dive.edito.eu/catalog/all  and launch “Jupyter-python-opendrift” using following settings:
  - Copernicus Marine Service credentials enabled, provide user name and password
  -	(Github access – can be done later as well)
  -	(Vault- passwords and accesses you have provided in Edito under “Your Secrets”.)
  -	Init (IMPORTANT!): Personalinit: bash: https://gitlab.mercator-ocean.fr/pub/edito-model-lab/wp4-core/edito-jupyter-opendrift/-/raw/custom_init/custom_init.sh, PersonalInitArgs: https://github.com/lia-f-h/opendrift_2026 This allows you to use this specific version of OpenBerg. More information: https://mercator-ocean.atlassian.net/wiki/external/NGZiYTNiYjhkZTIxNGU3YmFhMzE3OTFkMzY1ZmQ3OTk#Example-1%3A-Installing-a-Python-File. 
-	Coupling Edito with Github:
  o	Create Github account if you don’t have one already.
  o	Launch edito service. In the service, go to home directory (folder icon). In the service: Git: Initialize new repository. 
  o	Now, create new repository on Github.
  o	In the Edito service, open terminal and run following lines:
  git remote add origin https://github.com/<youraccount>/<repository>
  git branch -M main
  git push -u origin main'
  -	In the Edito service, commit and push to remote (advanced) giving your github name and token. 




