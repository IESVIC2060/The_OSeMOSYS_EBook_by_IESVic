#!/usr/bin/env python
# coding: utf-8

# # IESVic OSeMOSYS Notebook
# 
# This notebook contains the OSeMOSYS framework for energy modelling with an implementation in Python, using the Pyomo module. This Jupyter file is best run using Google Colab. The flowchart below contains the workflow for this notebook.
# 
# <p class="aligncenter">
# <img align="middle" src="https://github.com/criscfer/Personal_Storage_Folder/blob/main/Images/OSeMOSYS_Notebook_flowchart.png?raw=true"/>
# </p>
# The table below contains the available linear solvers inside this notebook. For a more detailed explanation on using and installing different solvers inside Google Colab, see [this link](https://jckantor.github.io/ND-Pyomo-Cookbook/notebooks/01.02-Running-Pyomo-on-Google-Colab.html)
# 
# <table>
#     <tr>
#     <th>Solver</th>
#     <th>Use</th>
#     <th>Call inside Pyomo</th>
#     </tr>
#     <tr>
#     <td class="solid"><a href="https://github.com/coin-or/Clp">COIN-OR Clp</a></td>
#     <td class="solid">LP</td>
#     <td class="solid"><em>opt = SolverFactory('clp')</em></td>
#     </tr>
#     <tr>
#     <td class="solid"><a href="https://github.com/coin-or/Cbc">COIN-OR Cbc</a></td>
#     <td class="solid">MILP</td>
#     <td class="solid"><em>opt = SolverFactory('cbc')</em></td>
#     </tr>
#     <tr>
#     <td class="solid"><a href="https://github.com/coin-or/Ipopt">COIN-OR Ipopt</a></td>
#     <td class="solid">NLP</td>
#     <td class="solid"><em>opt = SolverFactory('ipopt')</em></td>
#     </tr>
#     <tr>
#     <td class="solid"><a href="https://github.com/coin-or/Bonmin">COIN-OR Bonmin</a></td>
#     <td class="solid">MINLP</td>
#     <td class="solid"><em>opt = SolverFactory('bonmin')</em></td>
#     </tr>
#     <tr>
#     <td class="solid"><a href="https://github.com/coin-or/Couenne">COIN-OR Couenne</a></td>
#     <td class="solid">Global MINLP</td>
#     <td class="solid"><em>opt = SolverFactory('couenne')</em></td>
#     </tr>
# </table>
# 

# In[1]:


# Installations for Google Collab - Uncomment if running through Collab

get_ipython().run_line_magic('%capture', '')
import sys
import os

#!pip install pyomo
get_ipython().system('pip install idaes-pse --pre')
get_ipython().system('idaes get-extensions --to ./bin')
os.environ['PATH'] += ':bin'

##############################################################################

# Imports
from __future__ import division
from fileinput import filename
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np
import math
import random
from Objective_Function import ObjectiveFunction_rule
from Model_Constraints import *
#from Model_Debugging_Tools import Variable_Frame
#from Model_Sel_Res import Selected_Results

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



# In[ ]:


def Process_Data(data, component="set"):
    data = data.to_dict('list') # Transform dataframe into dictionary of lists
    #print(data)    
    included = data.pop('Included') # Get the 'Included' column as a separate list (alternative way of achieving this: list(data.values())[0] )
    value = list(data.values())[-1] # Get parameter values as a separate list
    if component == "set": # Initialize sets
        initializer = []
        for k in range(len(value)):
            if included[k] == "Yes":
                initializer.append(value[k])
    elif component == "parameter": # Initialize parameters
        initializer = {}
        sets = list(data.values())[0:-1]
        set_tuples = [tuple([i[j] for i in sets]) for j in range(len(sets[0]))] # Get sets indexing the parameter as tuples
        for k, i, j in zip(included, set_tuples, value):
            if(k == 'No'):                continue
            if not math.isnan(j):
                initializer[i] = j
    return initializer


# # Important for Google Colab users
# 
# If the notebook is being executed in exercise mode, you might need to re-run the initialization of a few parameters. This happens because, while Pyomo allows us to set some of the parameters as "mutable" to be changed in real time with the previous solution of the model still stored in memory, other parameters cannot be set as mutable if the constraints in which they are envolved are of a boolean nature.
# A boolean constraint is one where the condition for the model remain within that boundary is of True vs False nature. This is not always the case, since in some occasion, it may be that the constraint is only assessing if a particular value is contained within numerical boundaries, and not necessarely if a condition is true, or not.
# 
# Some of the parameters which will not be mutable for the purposes of this model are the "efficiencies", or the input and output `Activity Ratios`, and the `Specified Demand Profiles`. In order to change these parameters, set the `Exercise_Flag` to **True** and then select the scenario you wish to run by changing the `sheet_name` variable of the `read_excel` method from Pandas. These scenarios are different sheets from the amples Excel files provided.

# In[ ]:


# File paths inside Google Colab's main folder

sets_file = "/content/Sets_toy_model.xlsx"
parameters_file = "/content/Param_toy_model.xlsx"


# Activity Ratio files - to be used in exercises (set flag to True and re-run the model when using these files)
Exercise_Flag = True

if Exercise_Flag is True:
    print("Which scenario (from 1 to 5) would you like to select? ")
    select_IAR = input("For the input activity ratios (1 is the default scenario): ")
    if float(select_IAR) > 5 or float(select_IAR) < 1:
      raise Exception("No input activity ratio for scenario " + select_IAR)
    select_SDP = input("For the specified demand profile (1 is the default scenario): ") 
    if float(select_SDP) > 5 or float(select_SDP) < 1:
      raise Exception("No specified demand profile for scenario " + select_SDP)
    IAR_exercise = pd.DataFrame(pd.read_excel("/content/Input_Activity_Ratio_Samples.xlsx", sheet_name="IAR_Sample"+select_IAR))
    SDP_exercise = pd.DataFrame(pd.read_excel("/content/Demand_Profile_Samples.xlsx", sheet_name="SDP_Sample"+select_SDP))




model = AbstractModel(name="OSeMOSYS_IESVic") # Create model object and give it a name


# -------------------------------------------------------------------------------------------------

# # Initializations

# In[ ]:


'Dataframes:'
#------------------------------------------------------------------------------------------------------#
'Sets'
YEAR_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="YEAR"))
TECHNOLOGY_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="TECHNOLOGY"))
TIMESLICE_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="TIMESLICE"))
FUEL_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="FUEL",  header=0))
EMISSION_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="EMISSION"))
MODE_OF_OPERATION_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="MODE_OF_OPERATION"))
REGION_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="REGION"))
SEASON_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="SEASON"))
DAYTYPE_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="DAYTYPE"))
DAILYTIMEBRACKET_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="DAILYTIMEBRACKET"))
STORAGE_df = pd.DataFrame(pd.read_excel(sets_file, sheet_name="STORAGE"))

#------------------------------------------------------------------------------------------------------#
'Parameters'    
    
'Global'
YEARSPLIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Year_Split"))
DISCOUNTRATE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Discount_Rate"))
DAYSPLIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Day_Split"))
CONVERSIONLS_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Conversionls"))
CONVERSIONLD_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Conversionld"))
CONVERSIONLH_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Conversionlh"))
DAYSINDAYTYPE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Days_In_Day_Type"))    
TRADEROUTE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Trade_Route"))
DEPRECIATIONMETHOD_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Depreciation_Method"))
    
'Demands'
SPECIFIEDANNUALDEMAND_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Specified_Annual_Demand"))
SPECIFIEDDEMANDPROFILE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Specified_Demand_Profile"))
ACCUMULATEDANNUALDEMAND_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Accumulated_Annual_Demand"))
    
'Performance'
CAPACITYTOACTIVITYUNIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Capacity_To_Activity_Unit"))
CAPACITYFACTOR_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Capacity_Factor"))
AVAILABILITYFACTOR_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Availability_Factor"))
OPERATIONALLIFE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Operational_Life"))
RESIDUALCAPACITY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Residual_Capacity"))
INPUTACTIVITYRATIO_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Input_Activity_Ratio"))
OUTPUTACTIVITYRATIO_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Output_Activity_Ratio"))

'Technology Costs'
CAPITALCOST_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Capital_Cost"))
VARIABLECOST_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Variable_Cost"))
FIXEDCOST_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Fixed_Cost"))

'Storage'
TECHNOLOGYTOSTORAGE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Technology_To_Storage"))
TECHNOLOGYFROMSTORAGE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Technology_From_Storage"))
STORAGELEVELSTART_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Storage_Level_Start"))
'Adding storage level finish'
STORAGELEVELFINISH_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Storage_Level_Finish"))
STORAGEMAXCHARGERATE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Storage_Max_Charge_Rate"))
STORAGEMAXDISCHARGERATE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Storage_Max_Discharge_Rate"))
MINSTORAGECHARGE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Min_Storage_Charge"))
OPERATIONALLIFESTORAGE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="OperationalLife_Storage"))
CAPITALCOSTSTORAGE_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Capital_Cost_Storage"))
RESIDUALSTORAGECAPACITY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Residual_Storage_Capacity"))
    
'Capacity Constraints'
CAPACITYOFONETECHNOLOGYUNIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Capacity_1_Technology_Unit"))
TOTALANNUALMAXCAPACITY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Total_Annual_Max_Capacity"))
TOTALANNUALMINCAPACITY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Total_Annual_Min_Capacity"))
    
'Investment Constraints'
TOTALANNUALMAXCAPACITYINVESTMENT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="T_AnnualMax_CapacityInvestment"))
TOTALANNUALMINCAPACITYINVESTMENT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="T_AnnualMin_CapacityInvestment"))
    
'Activity Constraints'
TOTALTECHNOLOGYANNUALACTIVITYUPPERLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="TotalTechAnnualActivityUpLimit"))
TOTALTECHNOLOGYANNUALACTIVITYLOWERLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="TotalTechAnnualActivityLowLimit"))
TOTALTECHNOLOGYMODELPERIODACTIVITYUPPERLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="T_TechModelPeriodActivity_UL"))
TOTALTECHNOLOGYMODELPERIODACTIVITYLOWERLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="T_TechModelPeriodActivity_LL"))
    
'Reserve Margin'
RESERVEMARGINTAGTECHNOLOGY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Reserve_Margin_Tag_Technology"))
RESERVEMARGINTAGFUEL_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Reserve_Margin_Tag_Fuel"))
RESERVEMARGIN_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Reserve_Margin"))
    
'RE Generation Target'
RETAGTECHNOLOGY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="RE_Tag_Technology"))
RETAGFUEL_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="RE_Tag_Fuel"))
REMINPRODUCTIONTARGET_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="RE_Min_Production_Target"))
    
'Emissions'
EMISSIONACTIVITYRATIO_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Emission_Activity_Ratio"))
EMISSIONSPENALTY_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Emissions_Penalty"))
ANNUALEXOGENOUSEMISSION_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Annual_Exogenous_Emission"))
ANNUALEMISSIONLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Annual_Emission_Limit"))
MODELPERIODEXOGENOUSEMISSION_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="ModelPeriod_Exogenous_Emission"))
MODELPERIODEMISSIONLIMIT_df = pd.DataFrame(pd.read_excel(parameters_file, sheet_name="Model_Period_Emission_Limit"))
    


# In[ ]:


#------------------------------------------------------------------------------------------------------#
'Initializing'
   
'Sets'
model.YEAR = Set(initialize=Process_Data(YEAR_df, component="set"))
model.TECHNOLOGY = Set(initialize=Process_Data(TECHNOLOGY_df,component="set"))
model.TIMESLICE = Set(initialize=Process_Data(TIMESLICE_df,component="set"))
model.FUEL = Set(initialize=Process_Data(FUEL_df, component="set"))
model.EMISSION = Set(initialize=Process_Data(EMISSION_df, component="set"))
model.MODE_OF_OPERATION = Set(initialize=Process_Data(MODE_OF_OPERATION_df, component="set"))
model.REGION = Set(initialize=Process_Data(REGION_df, component="set"))
model.SEASON = Set(initialize=Process_Data(SEASON_df,component="set"))
model.DAYTYPE = Set(initialize=Process_Data(DAYTYPE_df,component="set"))
model.DAILYTIMEBRACKET = Set(initialize=Process_Data(DAILYTIMEBRACKET_df, component="set"))
model.STORAGE = Set(initialize=Process_Data(STORAGE_df, component="set"))

'Parameters'    
   
'Global parameters'
# 25-Oct-2022: Added definitions for global parameters

model.YearSplit = Param(model.TIMESLICE, model.YEAR, initialize=Process_Data(YEARSPLIT_df, component="parameter"))
# Definition: Duration of a modelled time slice, expressed as a fraction of the year. The sum of each entry over one modelled year should equal 1.
# Default = 1 / 8760

model.DiscountRate = Param(model.REGION, default=0.05, initialize=Process_Data(DISCOUNTRATE_df, component="parameter"))
# Definition: Region specific value for the discount rate, expressed in decimals (e.g. 0.05).

model.DaySplit = Param(model.DAILYTIMEBRACKET, model.YEAR, default=0.00137, initialize=Process_Data(DAYSPLIT_df, component="parameter"))
# Length of one DailyTimeBracket in one specific day as a fraction of the year (e.g., when distinguishing between days and night: 12h/(24h*365d)).
# Default = 1 / 8760

model.Conversionls = Param(model.TIMESLICE, model.SEASON, default=0, initialize=Process_Data(CONVERSIONLS_df, component="parameter"))
# Binary parameter linking one TimeSlice to a certain Season. It has value 0 if the TimeSlice does not pertain to the specific season, 1 if it does.
# Season: It gives indication (by successive numerical values) of how many seasons (e.g. winter, intermediate, summer) are accounted for and in 
# which order. This set is needed if storage facilities are included in the model.

model.Conversionld = Param(model.TIMESLICE, model.DAYTYPE, default=0, initialize=Process_Data(CONVERSIONLD_df, component="parameter"))
# Binary parameter linking one TimeSlice to a certain DayType. It has value 0 if the TimeSlice does not pertain to the specific DayType, 1 if it does.
# Day Type: It gives indication (by successive numerical values) of how many day types (e.g. workday, weekend) are accounted for and in which order. 
# This set is needed if storage facilities are included in the model.

model.Conversionlh = Param(model.TIMESLICE, model.DAILYTIMEBRACKET, default=0, initialize=Process_Data(CONVERSIONLH_df, component="parameter")) 
# Binary parameter linking one TimeSlice to a certain DailyTimeBracket. It has value 0 if the TimeSlice does not pertain to the specific DailyTimeBracket, 1 if it does.    
# Daily Time Bracket: It gives indication (by successive numerical values) of how many parts the day is split into (e.g. night, morning, afternoon, evening) 
# and in which order these parts are sorted. This set is needed if storage facilities are included in the model.

model.DaysInDayType = Param(model.SEASON, model.DAYTYPE, model.YEAR, default=7, initialize=Process_Data(DAYSINDAYTYPE_df, component="parameter"))
# Number of days for each day type, within one week (natural number, ranging from 1 to 7)

model.TradeRoute = Param(model.REGION, model.REGION, model.FUEL, model.YEAR, default=0, initialize=Process_Data(TRADEROUTE_df, component="parameter"))
# Binary parameter defining the links between region r and region rr, to enable or disable trading of a specific commodity. It has value 1 when two regions are linked, 0 otherwise

model.DepreciationMethod = Param(model.REGION, default=1, initialize=Process_Data(DEPRECIATIONMETHOD_df, component="parameter"))
# Binary parameter defining the type of depreciation to be applied. It has value 1 for sinking fund depreciation, value 2 for straight-line depreciation.

#------------------------------------------------------------------------------------------------------#
'Demands'

model.SpecifiedAnnualDemand = Param(model.REGION, model.FUEL, model.YEAR, default=0, initialize=Process_Data(SPECIFIEDANNUALDEMAND_df, component="parameter"))
# Total specified demand for the year, linked to a specific ‘time of use’ during the year.

if Exercise_Flag is True:
   model.SpecifiedDemandProfile = Param(model.REGION, model.FUEL, model.TIMESLICE, model.YEAR, default=0, initialize=Process_Data(SDP_exercise, component="parameter"))
else:
   model.SpecifiedDemandProfile = Param(model.REGION, model.FUEL, model.TIMESLICE, model.YEAR, default=0, initialize=Process_Data(SPECIFIEDDEMANDPROFILE_df, component="parameter"))
# Annual fraction of energy-service or commodity demand that is required in each time slice. For each year, all the defined SpecifiedDemandProfile input values should sum up to 1.

model.AccumulatedAnnualDemand = Param(model.REGION, model.FUEL, model.YEAR, default=0, initialize=Process_Data(ACCUMULATEDANNUALDEMAND_df, component="parameter"))
# Accumulated Demand for a certain commodity in one specific year. It cannot be defined for a commodity if its SpecifiedAnnualDemand for the same year is already defined and vice versa.

#------------------------------------------------------------------------------------------------------#
'Performance'

model.CapacityToActivityUnit = Param(model.REGION, model.TECHNOLOGY, default=8760, initialize=Process_Data(CAPACITYTOACTIVITYUNIT_df, component="parameter"))
# Conversion factor relating the energy that would be produced when one unit of capacity is fully used in one year.
# 24-Nov-2022 (CM): In the Pyomo-OSeMOSYS go-by, the default = 1, which is incorrect. The capacity_to_activity_unit should default to 8760; because that is how many hours are there in a year.

model.CapacityFactor = Param(model.REGION, model.TECHNOLOGY, model.TIMESLICE, model.YEAR, default=1, initialize=Process_Data(CAPACITYFACTOR_df, component="parameter"))
# Capacity available per each TimeSlice expressed as a fraction of the total installed capacity, with values ranging 
# from 0 to 1. It gives the possibility to account for forced outages.

model.AvailabilityFactor = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=1, initialize=Process_Data(AVAILABILITYFACTOR_df, component="parameter"))
# Maximum time a technology can run in the whole year, as a fraction of the year ranging from 0 to 1. It gives the
# possibility to account for planned outages.

model.OperationalLife = Param(model.REGION, model.TECHNOLOGY, default=1, initialize=Process_Data(OPERATIONALLIFE_df, component="parameter"))
# Useful lifetime of a technology, expressed in years.
# 24-Nov-2022 (CM): In the Pyomo-OSeMOSYS go-by, the default = 1. In Kevin Palmer-Wilson's model, it was 80. Given that many of my models will be in the sub-annual range, either is fine.
# 24-Nov-2022 (CM): A good practice would be to specify operational life all the time.

model.ResidualCapacity = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(RESIDUALCAPACITY_df, component="parameter"))
# Remained capacity available from before the modelling period.

if Exercise_Flag is True:
   model.InputActivityRatio = Param(model.REGION, model.TECHNOLOGY, model.FUEL, model.MODE_OF_OPERATION, model.YEAR, default=0, initialize=Process_Data(IAR_exercise, component="parameter"))
else:
   model.InputActivityRatio = Param(model.REGION, model.TECHNOLOGY, model.FUEL, model.MODE_OF_OPERATION, model.YEAR, default=0, initialize=Process_Data(INPUTACTIVITYRATIO_df, component="parameter"))
   
# Rate of use of a commodity by a technology, as a ratio of the rate of activity.

model.OutputActivityRatio = Param(model.REGION, model.TECHNOLOGY, model.FUEL, model.MODE_OF_OPERATION, model.YEAR, default=0, initialize=Process_Data(OUTPUTACTIVITYRATIO_df, component="parameter"))
# Rate of commodity output from a technology, as a ratio of the rate of activity.

#------------------------------------------------------------------------------------------------------#
'Technology Costs'

model.CapitalCost = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0.000001, initialize=Process_Data(CAPITALCOST_df, component="parameter"), mutable=True)
# Capital investment cost of a technology, per unit of capacity.

model.VariableCost = Param(model.REGION, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, default=0.000001, initialize=Process_Data(VARIABLECOST_df, component="parameter"), mutable=True)
# Cost of a technology for a given mode of operation (Variable O&M cost), per unit of activity.

model.FixedCost = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(FIXEDCOST_df, component="parameter"))
# Fixed O&M cost of a technology, per unit of capacity.

#------------------------------------------------------------------------------------------------------#
'Storage'

model.TechnologyToStorage = Param(model.REGION, model.TECHNOLOGY, model.STORAGE, model.MODE_OF_OPERATION, default=0, initialize=Process_Data(TECHNOLOGYTOSTORAGE_df, component="parameter"))
# Binary parameter linking a technology to the storage facility it charges. It has value 1 if the technology and the storage facility are linked, 0 otherwise.

model.TechnologyFromStorage = Param(model.REGION, model.TECHNOLOGY, model.STORAGE, model.MODE_OF_OPERATION, default=0, initialize=Process_Data(TECHNOLOGYFROMSTORAGE_df, component="parameter"))
# Binary parameter linking a storage facility to the technology it feeds. It has value 1 if the technology and the storage facility are linked, 0 otherwise.

model.StorageLevelStart = Param(model.REGION, model.STORAGE, default=0.0000001, initialize=Process_Data(STORAGELEVELSTART_df, component="parameter"), mutable=True)
# Level of storage at the beginning of first modelled year, in units of activity.

'Adding storage level finish'
model.StorageLevelFinish = Param(model.REGION, model.STORAGE, default=0.0000001, initialize=Process_Data(STORAGELEVELFINISH_df, component="parameter"), mutable=True)

model.StorageMaxChargeRate = Param(model.REGION, model.STORAGE, default=9999999, initialize=Process_Data(STORAGEMAXCHARGERATE_df, component="parameter"))
# Maximum charging rate for the storage, in units of activity per year.
   
model.StorageMaxDischargeRate = Param(model.REGION, model.STORAGE, default=9999999, initialize=Process_Data(STORAGEMAXDISCHARGERATE_df, component="parameter"))
# Maximum discharging rate for the storage, in units of activity per year.

model.MinStorageCharge = Param(model.REGION, model.STORAGE, model.YEAR, default=0, initialize=Process_Data(MINSTORAGECHARGE_df, component="parameter"), mutable=True)
# It sets a lower bound to the amount of energy stored, as a fraction of the maximum, with a number reanging between 
# 0 and 1. The storage facility cannot be emptied below this level.

model.OperationalLifeStorage = Param(model.REGION, model.STORAGE, default=0, initialize=Process_Data(OPERATIONALLIFESTORAGE_df, component="parameter"))
# Useful lifetime of the storage facility.

model.CapitalCostStorage = Param(model.REGION, model.STORAGE, model.YEAR, default=0, initialize=Process_Data(CAPITALCOSTSTORAGE_df, component="parameter"))
# Investment costs of storage additions, defined per unit of storage capacity.
   
model.ResidualStorageCapacity = Param(model.REGION, model.STORAGE, model.YEAR, default=0, initialize=Process_Data(RESIDUALSTORAGECAPACITY_df, component="parameter"))
# Exogenously defined storage capacities.

#------------------------------------------------------------------------------------------------------#
'Capacity Constraints'

model.CapacityOfOneTechnologyUnit = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(CAPACITYOFONETECHNOLOGYUNIT_df, component="parameter"))
# Capacity of one new unit of a technology. In case the user sets this parameter, the related technology will be installed only in batches of the 
# specified capacity and the problem will turn into a Mixed Integer Linear Problem.

model.TotalAnnualMaxCapacity = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=9999999, initialize=Process_Data(TOTALANNUALMAXCAPACITY_df, component="parameter"))
# Total maximum existing (residual plus cumulatively installed) capacity allowed for a technology in a specified year.

model.TotalAnnualMinCapacity = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(TOTALANNUALMINCAPACITY_df, component="parameter"))
# Total minimum existing (residual plus cumulatively installed) capacity allowed for a technology in a specified year.

#------------------------------------------------------------------------------------------------------#
'Investment Constraints'  

model.TotalAnnualMaxCapacityInvestment = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=9999999, initialize=Process_Data(TOTALANNUALMAXCAPACITYINVESTMENT_df, component="parameter"))
# Maximum capacity of a technology, expressed in power units.

model.TotalAnnualMinCapacityInvestment = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(TOTALANNUALMINCAPACITYINVESTMENT_df, component="parameter"))
# Minimum capacity of a technology, expressed in power units.

#------------------------------------------------------------------------------------------------------#
'Activity Constraints'

model.TotalTechnologyAnnualActivityUpperLimit = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=9999999, initialize=Process_Data(TOTALTECHNOLOGYANNUALACTIVITYUPPERLIMIT_df, component="parameter"))
# Total maximum level of activity allowed for a technology in one year.

model.TotalTechnologyAnnualActivityLowerLimit = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(TOTALTECHNOLOGYANNUALACTIVITYLOWERLIMIT_df, component="parameter"), within=Reals)
# Total minimum level of activity allowed for a technology in one year.

model.TotalTechnologyModelPeriodActivityUpperLimit = Param(model.REGION, model.TECHNOLOGY, default=9999999, initialize=Process_Data(TOTALTECHNOLOGYMODELPERIODACTIVITYUPPERLIMIT_df, component="parameter"))
# Total maximum level of activity allowed for a technology in the entire modelled period.

model.TotalTechnologyModelPeriodActivityLowerLimit = Param(model.REGION, model.TECHNOLOGY, default=0, initialize=Process_Data(TOTALTECHNOLOGYMODELPERIODACTIVITYLOWERLIMIT_df, component="parameter"), within=Reals)
# Total minimum level of activity allowed for a technology in the entire modelled period.
#------------------------------------------------------------------------------------------------------#
'Reserve Margin'

model.ReserveMarginTagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(RESERVEMARGINTAGTECHNOLOGY_df, component="parameter"))
# Binary parameter tagging the renewable technologies that must contribute to reaching the indicated minimum renewable 
# production target. It has value 1 for thetechnologies contributing, 0 otherwise.

model.ReserveMarginTagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0, initialize=Process_Data(RESERVEMARGINTAGFUEL_df, component="parameter"))
# Binary parameter tagging the fuels to which the renewable target applies to. It has value 1 if the target applies, 0 otherwise.

model.ReserveMargin = Param(model.REGION, model.YEAR, default=1, initialize=Process_Data(RESERVEMARGIN_df, component="parameter"))
# Minimum ratio of all renewable commodities tagged in the RETagCommodity parameter, to be produced by the technologies 
# tagged with the RETechnology parameter.
#------------------------------------------------------------------------------------------------------#
'RE Generation Target'

model.RETagTechnology = Param(model.REGION, model.TECHNOLOGY, model.YEAR, default=0, initialize=Process_Data(RETAGTECHNOLOGY_df, component="parameter"))
# Binary parameter tagging the renewable technologies that must contribute to reaching the indicated minimum
# renewable production target. It has value 1 for thetechnologies contributing, 0 otherwise.

model.RETagFuel = Param(model.REGION, model.FUEL, model.YEAR, default=0, initialize=Process_Data(RETAGFUEL_df, component="parameter"))
# Binary parameter tagging the fuels to which the renewable target applies to. It has value 1 if the target applies, 0 otherwise.

model.REMinProductionTarget = Param(model.REGION, model.YEAR, default=0, initialize=Process_Data(REMINPRODUCTIONTARGET_df, component="parameter"))
# Minimum ratio of all renewable commodities tagged in the RETagCommodity parameter, to be produced by the technologies 
# tagged with the RETechnology parameter.

#------------------------------------------------------------------------------------------------------#
'Emissions & Penalties'

model.EmissionActivityRatio = Param(model.REGION, model.TECHNOLOGY, model.EMISSION, model.MODE_OF_OPERATION, model.YEAR, default=0, initialize=Process_Data(EMISSIONACTIVITYRATIO_df, component="parameter"))
# Emission factor of a technology per unit of activity, per mode of operation.

model.EmissionsPenalty = Param(model.REGION, model.EMISSION, model.YEAR, default=0, initialize=Process_Data(EMISSIONSPENALTY_df, component="parameter"))
# Penalty per unit of emission.

model.AnnualExogenousEmission = Param(model.REGION, model.EMISSION, model.YEAR, default=0, initialize=Process_Data(ANNUALEXOGENOUSEMISSION_df, component="parameter"))
# It allows the user to account for additional annual emissions, on top of those computed endogenously by the model (e.g. emissions generated outside the region).

model.AnnualEmissionLimit = Param(model.REGION, model.EMISSION, model.YEAR, default=9999999, initialize=Process_Data(ANNUALEMISSIONLIMIT_df, component="parameter"))
# Annual upper limit for a specific emission generated in the whole modelled region.

model.ModelPeriodExogenousEmission = Param(model.REGION, model.EMISSION, default=0, initialize=Process_Data(MODELPERIODEXOGENOUSEMISSION_df, component="parameter"))
# It allows the user to account for additional emissions over the entire modelled period, on top of those computed 
# endogenously by the model (e.g. generated outside the region).

model.ModelPeriodEmissionLimit = Param(model.REGION, model.EMISSION, default=9999999, initialize=Process_Data(MODELPERIODEMISSIONLIMIT_df, component="parameter"))
# Annual upper limit for a specific emission generated in the whole modelled region, over the entire modelled period.



# In[ ]:


'Model Variables'

my_seed = random.seed(0) # Create a seed value to initialize variables with a random number
rand_init = random.random()

# model.StorageLevelStart = Var(model.REGION, model.STORAGE, bounds=(0, None), domain=Reals, initialize=rand_init)
# 26-Oct-2022: Troubleshooting; StorageLevelStart is now classified as a parameter - hence it is deleted as a variable now.

#------------------------------------------------------------------------------------------------------#
'Demands'

model.RateOfDemand = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.Demand = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
# 31-Oct-2022: Re-organized as per the same order in documentation

#------------------------------------------------------------------------------------------------------#
'Storage'

model.RateOfStorageCharge = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)
# Intermediate variable. It represents the commodity that would be charged to the storage facility s in one time slice if the latter lasted the whole year. It is a function of the RateOfActivity and the parameter TechnologyToStorage.
model.RateOfStorageDischarge = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)
# Intermediate variable. It represents the commodity that would be discharged from storage facility s in one time slice if the latter lasted the whole year. It is a function of the RateOfActivity and the parameter TechnologyFromStorage.
model.NetChargeWithinYear = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)
# Net quantity of commodity charged to storage facility s in year y. It is a function of the RateOfStorageCharge and the RateOfStorageDischarge and it can be negative.
model.NetChargeWithinDay = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, initialize=0.0)
# Net quantity of commodity charged to storage facility s in daytype ld. It is a function of the RateOfStorageCharge and the RateOfStorageDischarge and can be negative.
model.StorageLevelYearStart = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Level of stored commodity in storage facility s in the first time step of year y.
model.StorageLevelYearFinish = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Level of stored commodity in storage facility s in the last time step of year y.
model.StorageLevelSeasonStart = Var(model.REGION, model.STORAGE, model.SEASON, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Level of stored commodity in storage facility s in the first time step of season ls.
model.StorageLevelDayTypeStart = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Level of stored commodity in storage facility s in the first time step of daytype ld.
model.StorageLevelDayTypeFinish = Var(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
# Level of stored commodity in storage facility s in the last time step of daytype ld.
#model.StorageLevelTSStart = Var(model.REGION, model.STORAGE, model.TIMESLICE, model.YEAR, bounds = (0, None), domain=Reals, initialize=rand_init)
# 27-Sep-2022 Removed StorageLevelTSStart
model.StorageLowerLimit = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Minimum allowed level of stored commodity in storage facility s, as a function of the storage capacity and the user-defined MinStorageCharge ratio.
model.StorageUpperLimit = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Maximum allowed level of stored commodity in storage facility s. It corresponds to the total existing capacity of storage facility s (summing newly installed and pre-existing capacities).
model.AccumulatedNewStorageCapacity = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Cumulative capacity of newly installed storage from the beginning of the time domain to year y.
model.NewStorageCapacity = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Capacity of newly installed storage in year y.
model.CapitalInvestmentStorage = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Undiscounted investment in new capacity for storage facility s. Derived from the NewStorageCapacity and the parameter CapitalCostStorage.
model.DiscountedCapitalInvestmentStorage = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Investment in new capacity for storage facility s, discounted through the parameter DiscountRate.
model.SalvageValueStorage = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Salvage value of storage facility s in year y, as a function of the parameters OperationalLifeStorage and DepreciationMethod.
model.DiscountedSalvageValueStorage = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Salvage value of storage facility s, discounted through the parameter DiscountRate.
model.TotalDiscountedStorageCost = Var(model.REGION, model.STORAGE, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
# Difference between the discounted capital investment in new storage facilities and the salvage value in year y.

#------------------------------------------------------------------------------------------------------#
'Capacity Variables'

model.NumberOfNewTechnologyUnits = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Integers, initialize=0)
model.NewCapacity = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0) # This vaiable must be within Real numbers for feasible solution
model.AccumulatedNewCapacity = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.TotalCapacityAnnual = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)

#------------------------------------------------------------------------------------------------------#
'Activity Variables'

model.RateOfActivity = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, bounds = (0, None), domain=Reals, initialize=0)  # Eliminated the >=0 constraint (PMT) #18-Nov-2022: The number needs to be non-negative real number. PMT removed it for some reason, but it causes problems with multiple modes of operation.
model.RateOfTotalActivity = Var(model.REGION, model.TECHNOLOGY, model.TIMESLICE, model.YEAR, bounds=(0,None), domain=Reals, initialize=0.0)
model.TotalTechnologyAnnualActivity = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), initialize=0.0)
model.TotalAnnualTechnologyActivityByMode = Var(model.REGION, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, bounds = (0, None), initialize=0.0)
model.RateOfProductionByTechnologyByMode = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.RateOfProductionByTechnology = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.ProductionByTechnology = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.ProductionByTechnologyAnnual = Var(model.REGION, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.RateOfProduction = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.Production = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.RateOfUseByTechnologyByMode = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.RateOfUseByTechnology = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.UseByTechnologyAnnual = Var(model.REGION, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.RateOfUse = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.UseByTechnology = Var(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.Use = Var(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.Trade = Var(model.REGION, model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, initialize=0.0)
model.TradeAnnual = Var(model.REGION, model.REGION, model.FUEL, model.YEAR, initialize=0.0)
model.ProductionAnnual = Var(model.REGION, model.FUEL, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.UseAnnual = Var(model.REGION, model.FUEL, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
#model.DemandAnnual = Var(model.REGION, model.FUEL, model.YEAR, bounds=(0, None), initialize=0)
# 31-Oct-2022: An element from Kevin Palmer-Wilson's model; verify if needed.
# 04-Nov-2022: Turning off as not needed.

#------------------------------------------------------------------------------------------------------#
'Costing Variables'

model.CapitalInvestment = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.DiscountedCapitalInvestment = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.SalvageValue = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.DiscountedSalvageValue = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.OperatingCost = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.DiscountedOperatingCost = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds = (0, None), domain=Reals, initialize=0.0)
model.AnnualVariableOperatingCost = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds=(0, None), initialize=0.0)
model.AnnualFixedOperatingCost = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.VariableOperatingCost = Var(model.REGION, model.TECHNOLOGY, model.TIMESLICE, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.TotalDiscountedCostByTechnology = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.TotalDiscountedCost = Var(model.REGION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.ModelPeriodCostByRegion = Var(model.REGION, bounds=(0, None), domain=Reals, initialize=0.0)

#------------------------------------------------------------------------------------------------------#
'Reserve Margin'

model.TotalCapacityInReserveMargin = Var(model.REGION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.DemandNeedingReserveMargin = Var(model.REGION, model.TIMESLICE, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)

#------------------------------------------------------------------------------------------------------#
'RE Gen Target'

model.TotalREProductionAnnual = Var(model.REGION, model.YEAR, initialize=0.0)
model.RETotalProductionOfTargetFuelAnnual = Var(model.REGION, model.YEAR, initialize=0.0)
model.TotalTechnologyModelPeriodActivity = Var(model.REGION, model.TECHNOLOGY, initialize=0.0)

#------------------------------------------------------------------------------------------------------#
'Emissions'

model.AnnualTechnologyEmissionByMode = Var(model.REGION, model.TECHNOLOGY, model.EMISSION, model.MODE_OF_OPERATION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.AnnualTechnologyEmission = Var(model.REGION, model.TECHNOLOGY, model.EMISSION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.AnnualTechnologyEmissionPenaltyByEmission = Var(model.REGION, model.TECHNOLOGY, model.EMISSION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.AnnualTechnologyEmissionsPenalty = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.DiscountedTechnologyEmissionsPenalty = Var(model.REGION, model.TECHNOLOGY, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.AnnualEmissions = Var(model.REGION, model.EMISSION, model.YEAR, bounds=(0, None), domain=Reals, initialize=0.0)
model.ModelPeriodEmissions = Var(model.REGION, model.EMISSION, bounds=(0, None), domain=Reals, initialize=0.0)


# In[ ]:


'Model Equations & Constraints'
'This section includes the constraints & associated equations as per the OSeMOSYS documentation'
##################################################################################################
'Objective Function'

'This equation represents the overall objective of the model. The default in OSeMOSYS is to minimise the total system cost, over the entire model period.'

model.OBJ = Objective(rule=ObjectiveFunction_rule, sense= minimize)
# minimize cost: sum{r in REGION, y in YEAR} TotalDiscountedCost[r,y];

##################################################################################################
'Demand Constraints'

'The equation below is used to generate the term RateOfDemand, from the user-provided data for SpecifiedAnnualDemand and SpecifiedDemandProfile.'
' The RateOfDemand is defined for each combination of commodity, TimeSlice and Year.'

model.EQ_SpecifiedDemand_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EQ_SpecifiedDemand_rule)
# SpecifiedAnnualDemand[r,f,y]*SpecifiedDemandProfile[r,f,l,y] / YearSplit[l,y]=RateOfDemand[r,l,f,y];

# model.Demand_constraint = Constraint(model.REGION, model.FUEL, model.YEAR, rule=Demand_rule)
# 31-Oct-2022: Verify if this is equation is as per the documentation or not.
# 04-Nov-2022: Turning off as it is not needed.

##################################################################################################
'Capacity Adequacy A'

'''
Used to first calculate total capacity of each technology for each year based on existing capacity 
from before the model period (ResidualCapacity), AccumulatedNewCapacity during the modelling period, and NewCapacity 
installed in each year. It is then ensured that this Capacity is sufficient to meet the RateOfTotalActivity in each 
TimeSlice and Year. An additional constraint based on the size, or capacity, of each unit of a Technology is included 
(CapacityOfOneTechnologyUnit). This stipulates that the capacity of certain Technology can only be a multiple of the 
user-defined CapacityOfOneTechnologyUnit.
'''

model.CAa1_TotalNewCapacity_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CAa1_TotalNewCapacity_rule)

model.CAa2_TotalAnnualCapacity_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CAa2_TotalAnnualCapacity_rule)

model.CAa3_TotalActivityOfEachTechnology_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.TIMESLICE, model.YEAR, rule=CAa3_TotalActivityOfEachTechnology_rule)
# 31-Oct-2022: Added from documentation.

model.CAa4_ConstraintCapacity_constraint = Constraint(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.YEAR, rule=CAa4_ConstraintCapacity_rule,)

#model.CAa4b_Constraint_Capacity_constraint = Constraint(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.YEAR, rule=CAa4b_Constraint_Capacity_rule)
# 31-Oct-2022: Removed and replaced with documentation version.

model.CAa5_TotalNewCapacity_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CAa5_TotalNewCapacity_rule)

##################################################################################################
'Capacity Adequacy B'

'''
Ensures that adequate capacity of technologies is present to at least meet the average annual demand.
'''

model.CAb1_PlannedMaintenance_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CAb1_PlannedMaintenance_rule)

model.CAb1_PlannedMaintenance_Negative_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CAb1_PlannedMaintenance_Negative_rule)

##################################################################################################
'Energy Balance A'

'''
Ensures that demand for each commodity is met in each TimeSlice.
'''

model.EBa1_RateOfFuelProduction1_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, rule=EBa1_RateOfFuelProduction1_rule) 

model.EBa2_RateOfFuelProduction2_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.TECHNOLOGY, model.YEAR, rule=EBa2_RateOfFuelProduction2_rule)

model.EBa3_RateOfFuelProduction3_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa3_RateOfFuelProduction3_rule)

model.EBa4_RateOfFuelUse1_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, rule=EBa4_RateOfFuelUse1_rule)

model.EBa5_RateOfFuelUse2_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.TECHNOLOGY, model.YEAR, rule=EBa5_RateOfFuelUse2_rule)

model.EBa6_RateOfFuelUse3 = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa6_RateOfFuelUse3_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.EBa7_EnergyBalanceEachTS1_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa7_EnergyBalanceEachTS1_rule)

model.EBa8_EnergyBalanceEachTS2_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa8_EnergyBalanceEachTS2_rule)

model.EBa9_EnergyBalanceEachTS3_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa9_EnergyBalanceEachTS3_rule)

model.EBa10_EnergyBalanceEachTS4_constraint = Constraint(model.REGION, model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa10_EnergyBalanceEachTS4_rule)

model.EBa11_EnergyBalanceEachTS5 = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa11_EnergyBalanceEachTS5_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

#model.EBa11_EnergyBalanceEachTS5_constraint = Constraint( model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EBa11_EnergyBalanceEachTS5_rule)

##################################################################################################
'Energy Balance B'

'''
Ensures that demand for each commodity is met in each Year.
'''

#model.EBb3_EnergyBalanceEachYear3_constraint = Constraint(model.REGION, model.REGION, model.FUEL, model.YEAR, rule=EBb3_EnergyBalanceEachYear3_rule)

model.EBb1_EnergyBalanceEachYear1 = Constraint(model.REGION, model.FUEL, model.YEAR, rule=EBb1_EnergyBalanceEachYear1_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.EBb2_EnergyBalanceEachYear2_constraint = Constraint(model.REGION, model.FUEL, model.YEAR, rule=EBb2_EnergyBalanceEachYear2_rule)

model.EBb3_EnergyBalanceEachYear3_constraint = Constraint(model.REGION, model.REGION, model.FUEL, model.YEAR, rule=EBb3_EnergyBalanceEachYear3_rule)

model.EBb4_EnergyBalanceEachYear4_constraint = Constraint(model.REGION, model.FUEL, model.YEAR, rule=EBb4_EnergyBalanceEachYear4_rule)

#model.EnergyBalanceEachTS5_constraint = Constraint(model.REGION, model.TIMESLICE, model.FUEL, model.YEAR, rule=EnergyBalanceEachTS5_rule)
# 31-Oct-2022: Replaced with EBa11 - to be deleted later.

#model.EnergyConstraint_constraint = Constraint(model.REGION, model.YEAR, rule=EnergyConstraint_rule)
# 31-Oct-2022: Verify what this equation is; seems to be a relic from Kevin Palmer-Wilson's model.
# 04-Nov-2022: This is Kevin Palmer-Wilson's expression of RE4; which has been inserted elsewhere already.

##################################################################################################
'Accounting Technology Production/Use'

'''
Accounting equations used to generate specific intermediate variables
'''

model.Acc1_FuelProductionByTechnology_constraint = Constraint(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, rule=Acc1_FuelProductionByTechnology_rule)

model.Acc2_FuelUseByTechnology_constraint = Constraint(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.FUEL, model.YEAR, rule=Acc2_FuelUseByTechnology_rule)

model.Acc3_AverageAnnualRateOfActivity_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, rule=Acc3_AverageAnnualRateOfActivity_rule)

model.Acc4_ModelPeriodCostByRegion_constraint = Constraint(model.REGION, rule=Acc4_ModelPeriodCostByRegion_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

##################################################################################################
'Storage Equations'

model.S1_RateofStorageCharge_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, model.TECHNOLOGY, model.MODE_OF_OPERATION, rule=S1_RateofStorageCharge_rule)

model.S2_RateofStorageDischarge_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, model.TECHNOLOGY, model.MODE_OF_OPERATION, rule=S2_RateOfStorageDischarge_rule)

model.S3_NetChargeWithinYear_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule=S3_NetChargeWithinYear_rule)

model.S4_NetChargeWithinDay_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule=S4_NetChargeWithinDay_rule)

model.S5_S6_StorageLevelYearStart_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=S5_S6_StorageLevelYearStart_rule)

model.S7_S8_StorageLevelYearFinish_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=S7_S8_StorageLevelYearFinish_rule)

model.S9_S10_StorageLevelSeasonStart_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.YEAR, rule=S9_S10_StorageLevelSeasonStart_rule)
# 04-Oct-2022: Added S9_S10_StorageLevelSeasonStart_constraint

model.S11_S12_StorageLevelDayTypeStart_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.YEAR, rule=S11_S12_StorageLevelDayTypeStart_rule)
# 04-Oct-2022: Added S11_S12_StorageLevelDayTypeStart_constraint

model.S13_S14_S15_StorageLevelDayTypeFinish_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.YEAR, rule=S13_S14_S15_StorageLevelDayTypeFinish_rule)
# 04-Oct-2022: Added S13_S14_S15_StorageLevelDayTypeFinish_constraint

#model.S1_StorageLevelYearStart_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=S1_StorageLevelYearStart_rule)
# 27-Sep-2022: Removed S1_StorageLevelYearStart

#model.S2_StorageLevelTSStart_constraint = Constraint(model.REGION, model.STORAGE, model.TIMESLICE, model.YEAR, rule=S2_StorageLevelTSStart_rule)
# 27-Sep-2022: Removed S2_StorageLevelTSStart

##################################################################################################
'Storage Constraints'

#model.SC8_StorageRefilling_constraint = Constraint(model.STORAGE, model.REGION, rule= SC8_StorageRefilling_rule)
# 23-Sep-2022: Discussed with Cristiano; only relevant to Kevin's model.

#model.SC9_StopModeLeakage_constraint = Constraint(model.REGION, model.TIMESLICE, model.YEAR, model.MODE_OF_OPERATION, model.TECHNOLOGY, model.STORAGE, rule= SC9_StopModeLeakage_rule) 
# 23-Sep-2022: Discussed with Cristiano; only relevant to Kevin's model.

#model.NonStorageConstraint_constraint = Constraint(model.REGION, model.TIMESLICE, model.TECHNOLOGY, model.MODE_OF_OPERATION, model.YEAR, rule=NonStorageConstraint_rule)
# 23-Sep-2022: Discussed with Cristiano; only relevant to Kevin's model.

model.SC1_LowerLimit_1TimeBracket1InstanceOfDayType1week_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC1_LowerLimit_1TimeBracket1InstanceOfDayType1week_rule) 
# 18-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC1_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

model.SC1_UpperLimit_1TimeBracket1InstanceOfDayType1week_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC1_UpperLimit_1TimeBracket1InstanceOfDayType1week_rule)
# 18-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC1_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInFirstWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

model.SC2_LowerLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC2_LowerLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_rule)
# 18-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC2_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}: 

model.SC2_UpperLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC2_UpperLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_rule)
# 18-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC2_UpperLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInFirstWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

model.SC3_LowerLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC3_LowerLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_rule)
# 18-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC3_LowerLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

model.SC3_UpperLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC3_UpperLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_rule)
# 19-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC3_UpperLimit_EndOfDailyTimeBracketOfLastInstanceOfDayTypeInLastWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:  

model.SC4_LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC4_LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule)
# 19-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC4_LowerLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

model.SC4_UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC4_UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule)
# 19-Oct-2022: Added the OSeMOSYS documentation definition
# s.t. SC4_UpperLimit_BeginningOfDailyTimeBracketOfFirstInstanceOfDayTypeInLastWeekConstraint{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}:

#model.SC1a_LowerLimitEndofModelPeriod_constraint = Constraint(model.STORAGE, model.YEAR, model.REGION, rule=SC1a_LowerLimitEndofModelPeriod_rule)
#model.SC2_UpperLimit_constraint = Constraint(model.REGION, model.STORAGE, model.TIMESLICE, model.YEAR, rule=SC2_UpperLimit_rule)
#model.SC2a_UpperLimitEndofModelPeriod_constraint = Constraint(model.STORAGE,model.YEAR,model.REGION, rule=SC2a_UpperLimitEndofModelPeriod_rule)
#model.SC2a_UpperLimitEndofModelPeriod_Negative_constraint = Constraint(model.STORAGE, model.YEAR, model.REGION, rule= SC2a_UpperLimitEndofModelPeriod_Negative_rule)
#model.SC7_StorageMaxUpperLimit_constraint = Constraint(model.STORAGE, model.YEAR, model.REGION, rule= SC7_StorageMaxUpperLimit_rule)
# 27-Sep-2022: This could refer to SC5 that is entered below.

model.SC5_MaxCharge_constraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC5_MaxCharge_rule)
# 27-Sep-2022: Added MaxCharge_constraint

model.SC6_MaxDischarge_consraint = Constraint(model.REGION, model.STORAGE, model.SEASON, model.DAYTYPE, model.DAILYTIMEBRACKET, model.YEAR, rule= SC6_MaxDischarge_rule)
# 27-Sep-2022: Added MaxDischarge_constraint

'Adding storage level finish'
model.TEMP_StorageLevelFinish_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule = TEMP_StorageLevelFinish_rule)

##################################################################################################
'Storage Investments'

'''
Calculates the total discounted capital costs expenditure for each storage technology in each year.
'''

model.SI1_StorageUpperLimit_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI1_StorageUpperLimit_rule)

model.SI2_StorageLowerLimit_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI2_StorageLowerLimit_rule)

model.SI3_TotalNewStorage_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI3_TotalNewStorage_rule)

model.SI4_UndiscountedCapitalInvestmentStorage_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI4_UndiscountedCapitalInvestmentStorage_rule)

model.SI5_DiscountingCapitalInvestmentStorage_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI5_DiscountingCapitalInvestmentStorage_rule)

model.SI6_SI7_SI8_SalvageValueStorageAtEndOfPeriod_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI6_SI7_SI8_SalvageValueStorageAtEndOfPeriod_rule)

model.SI9_SalvageValueDiscountedToStartYear_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI9_SalvageValueStorageDiscountedToStartYear_rule)

model.SI10_TotalDiscountedCostByStorage_constraint = Constraint(model.REGION, model.STORAGE, model.YEAR, rule=SI10_TotalDiscountedCostByStorage_rule)

##################################################################################################
'Capital Costs'

'''
Calculates the total discounted capital cost expenditure for each technology in each year.
'''

model.CC1_UndiscountedCapitalInvestment_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CC1_UndiscountedCapitalInvestment_rule)

model.CC2_DiscountedCapitalInvestment_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=CC2_DiscountedCapitalInvestment_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

##################################################################################################
'Salvage Value'

'''
Calculates the fraction of the initial capital cost that can be recouped at the end of a technologies operational life. 
The salvage value can be calculated using one of two depreciation methods: straight line and sinking fund.
'''

model.SV1_SV2_SV3_SalvageValueAtEndOfPeriod_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=SV1_SV2_SV3_SalvageValueAtEndOfPeriod_rule)

model.SV4_SalvageValueDiscountedToStartYear_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=SV4_SalvageValueDiscountedToStartYear_rule)

##################################################################################################
'Operating Costs'

'''
Calculates the total variable and fixed operating costs for each technology, in each year.
'''

model.OC1_OperatingCostsVariable_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=OC1_OperatingCostsVariable_rule)

model.OC2_OperatingCostsFixedAnnual_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=OC2_OperatingCostsFixedAnnual_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.OC3_OperatingCostsTotalAnnual_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=OC3_OperatingCostsTotalAnnual_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.OC4_DiscountedOperatingCostsTotalAnnual_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=OC4_DiscountedOperatingCostsTotalAnnual_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

##################################################################################################
'Total Discounted Costs'

'''
Calculates the total discounted system cost over the entire model period to give the TotalDiscountedCost. This is the variable that is minimized in the model’s objective function.
'''

model.TDC1_TotalDiscountedCostByTechnology_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=TDC1_TotalDiscountedCostByTechnology_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.TDC2_TotalDiscountedCost_constraint = Constraint(model.REGION, model.YEAR, rule=TDC2_TotalDiscountedCost_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

##################################################################################################
'Total Capacity Constraints'

'''
Ensures that the total capacity of each technology in each year is greater than and less 
than the user-defined parameters TotalAnnualMinCapacityInvestment and TotalAnnualMaxCapacityInvestment respectively.
'''

model.TCC1_TotalAnnualMaxCapacityConstraint_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=TCC1_TotalAnnualMaxCapacityConstraint_rule)
        
model.TCC2_TotalAnnualMinCapacityConstraint_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=TCC2_TotalAnnualMinCapacityConstraint_rule)

##################################################################################################
'New Capacity Constraints'

'''
Ensures that the new capacity of each technology installed in each year is greater than and less than the 
user-defined parameters TotalAnnualMinCapacityInvestment and TotalAnnualMaxCapacityInvestment respectively.
'''

model.NCC1_TotalAnnualMaxNewCapacityConstraint_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=NCC1_TotalAnnualMaxNewCapacityConstraint_rule)

model.NCC2_TotalAnnualMinNewCapacityConstraint_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=NCC2_TotalAnnualMinNewCapacityConstraint_rule)

##################################################################################################
'Annual Activity Constraints'

'''
Ensures that the total activity of each technology over each year is greater than and less than the user-defined parameters 
TotalTechnologyAnnualActivityLowerLimit and TotalTechnologyAnnualActivityUpperLimit respectively.
'''

model.AAC1_TotalAnnualTechnologyActivity_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=AAC1_TotalAnnualTechnologyActivity_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.AAC2_TotalAnnualTechnologyActivityUpperLimit_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=AAC2_TotalAnnualTechnologyActivityUpperLimit_rule)

model.AAC3_TotalAnnualTechnologyActivityLowerLimit_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=AAC3_TotalAnnualTechnologyActivityLowerLimit_rule)    

##################################################################################################
'Total Activity Constraints'

'''
Ensures that the total activity of each technology over the entire model period is greater than and less than the
user-defined parameters TotalTechnologyModelPeriodActivityLowerLimit and TotalTechnologyModelPeriodActivityUpperLimit respectively.
'''

model.TAC1_TotalModelHorizonTechnologyActivity_constraint = Constraint(model.REGION, model.TECHNOLOGY, rule=TAC1_TotalModelHorizonTechnologyActivity_rule)

model.TAC2_TotalModelHorizonTechnologyActivityUpperLimit_constraint = Constraint(model.REGION, model.TECHNOLOGY, rule= TAC2_TotalModelHorizonTechnologyActivityUpperLimit_rule)

model.TAC3_TotalModelHorizonTechnologyActivityLowerLimit_constraint = Constraint(model.REGION, model.TECHNOLOGY, rule= TAC3_TotalModelHorizenTechnologyActivityLowerLimit_rule)

##################################################################################################
'Reserve Margin Constraints'

'''
Ensures that sufficient reserve capacity of specific technologies 
(ReserveMarginTagTechnology = 1) is installed such that the user-defined ReserveMargin is maintained.
'''

model.RM1_ReserveMargin_TechnologiesIncluded_constraint = Constraint(model.REGION, model.TIMESLICE, model.YEAR, rule=RM1_ReserveMargin_TechnologiesIncluded_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.RM2_ReserveMargin_FuelsIncluded_constraint = Constraint(model.REGION, model.TIMESLICE, model.YEAR, rule=RM2_ReserveMargin_FuelsIncluded_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.RM3_ReserveMargin_Constraint_constraint = Constraint(model.REGION, model.TIMESLICE, model.YEAR, rule= RM3_ReserveMargin_Constraint_rule)

##################################################################################################
'RE Production Target'

'''
Ensures that production from technologies tagged as renewable energy technologies 
(RETagTechnology = 1) is at least equal to the user-defined renewable energy (RE) target.
'''
model.RE1_FuelProductionByTechnologyAnnual_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.FUEL, model.YEAR, rule=RE1_FuelProductionByTechnologyAnnual_rule)

model.RE2_TechIncluded_constraint = Constraint(model.REGION, model.YEAR, rule=RE2_TechIncluded_rule)

model.RE3_FuelIncluded_constraint = Constraint(model.REGION, model.YEAR, rule=RE3_FuelIncluded_rule)

model.RE4_EnergyConstraint_constraint = Constraint(model.REGION, model.YEAR, rule= RE4_EnergyConstraint_rule)

model.RE5_FuelUseByTechnologyAnnual_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.FUEL, model.YEAR, rule=RE5_FuelUseByTechnologyAnnual_rule)

##################################################################################################
'Emissions Accounting'

'''
Calculates the annual and model period emissions from each technology, for each type of emission. 
It also calculates the total associated emission penalties, if any. Finally, it ensures that emissions are maintained before 
stipulated limits that may be defined for each year and/or the entire model period.
'''

model.E1_AnnualEmissionProductionByMode_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.EMISSION, model.MODE_OF_OPERATION, model.YEAR, rule=E1_AnnualEmissionProductionByMode_rule) 
# 31-Oct-2022: Added equation from documentation & go-by.

model.E2_AnnualEmissionProduction = Constraint(model.REGION, model.TECHNOLOGY, model.EMISSION, model.YEAR, rule=E2_AnnualEmissionProduction_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E3_EmissionPenaltyByTechAndEmission = Constraint(model.REGION, model.TECHNOLOGY, model.EMISSION, model.YEAR, rule=E3_EmissionPenaltyByTechAndEmission_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E4_EmissionsPenaltyByTechnology = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule=E4_EmissionsPenaltyByTechnology_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E5_DiscountedEmissionsPenaltyByTechnology_constraint = Constraint(model.REGION, model.TECHNOLOGY, model.YEAR, rule = E5_DiscountedEmissionsPenaltyByTechnology_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E6_EmissionsAccounting1 = Constraint(model.REGION, model.EMISSION, model.YEAR, rule=E6_EmissionsAccounting1_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E7_EmissionsAccounting2 = Constraint(model.REGION, model.EMISSION, rule=E7_EmissionsAccounting2_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E8_AnnualEmissionsLimit_constraint = Constraint(model.REGION, model.EMISSION, model.YEAR, rule= E8_AnnualEmissionsLimit_rule)
# 31-Oct-2022: Added equation from documentation & go-by.

model.E9_ModelPeriodEmissionsLimit_constraint = Constraint(model.REGION, model.EMISSION, rule= E9_ModelPeriodEmissionsLimit_rule)
# 31-Oct-2022: Added equation from documentation & go-by.


# # Solving the Model
# 
# The next cell solves an instance of the model using the solver of the user's choice. You may change the `SolverFactory` to the available solver of your choice

# In[ ]:


instance = model.create_instance()
opt = SolverFactory('cbc') # Choose solver to be used
final_result = opt.solve(instance, tee=True).write()


# # Visualizing Results
# 
# The next cell will produce graphs for some of the key variables to illustrate the model results

# In[ ]:


from pandas.core import series
def Visualizer(instance):
    #print([key[1] for key in instance.TotalCapacityAnnual])
    #print([value(instance.TotalCapacityAnnual[key]) for key in instance.TotalCapacityAnnual])
    #instance.RateOfActivity.pprint()

    bar_colors = ['chocolate','darkturquoise', 'grey', 'green', 'brown', 'lightcoral']
    var_bars = [key[1] for key in instance.TotalCapacityAnnual]
    var_values = [value(instance.TotalCapacityAnnual[key]) for key in instance.TotalCapacityAnnual]

    dem_values = [value(instance.Demand[key]) for key in instance.Demand if key[2] == 'demHEAT']
    gas_stor_values = [value(instance.StorageLevelSeasonStart[key]) for key in instance.StorageLevelSeasonStart if key[1] == 'storGAS']

    x_seasons = [key[2] for key in instance.StorageLevelSeasonStart]
    x_timeslices = Process_Data(TIMESLICE_df, component="set")

    rate_act = {}
    for k in instance.RateOfActivity.keys():
      if k[3] == 1:
        rate_act[(k[1], k[2])]  = value(instance.RateOfActivity[k])  / len(x_timeslices)
       



    df = pd.DataFrame({"Technologies" : var_bars, "Capacity" : var_values, "Color" : ['blue','green', 'red', 'yellow', 'grey', 'pink']})
    
    my_figure = make_subplots(rows=2, cols=2, subplot_titles=("Total Capacities", "Heat Demand Over the Year", "Energy Generated by Technology", "Gas Storage Level at Start of Each Month"), shared_xaxes=False)
    
    my_figure.add_trace(go.Bar(y=var_values, x=var_bars, marker=dict(color=bar_colors, coloraxis="coloraxis"), name="Annual Capacities", xaxis="x1", yaxis="y1"), row=1, col=1)
    my_figure.add_trace(go.Scatter(x=x_timeslices, y=dem_values, name="Heat Demand",xaxis="x2", yaxis="y2"), row=1, col=2)


    techs = Process_Data(TECHNOLOGY_df,component="set") # Getting list of technologies in the model
    no_change_techs = ["distGAS", "tCOMP", 'tEXTRACT1'] # list of technologies not to be changed by students
    for item in no_change_techs:
      if item in techs:
        techs.remove(item)

    for t in techs:
      rates_y = []
      for k in rate_act.keys(): 
        if t == k[-1]:
          rates_y.append(value(rate_act[k]))
      my_figure.add_trace(go.Scatter(x=x_timeslices, y=rates_y, name=f'{"Energy Generated by "+t}',xaxis="x3", yaxis="y3"), row=2, col=1)
    
    my_figure.add_trace(go.Scatter(x=x_seasons, y=gas_stor_values, name="Gas Storage",xaxis="x4", yaxis="y4", marker=dict(color='teal')), row=2, col=2)

    # Set axes titles
    my_figure.update_xaxes(title_text="Technologies", row=1, col=1)
    my_figure.update_xaxes(title_text="Timeslices (Weeks)", row=1, col=2)
    my_figure.update_xaxes(title_text="Timeslices (Weeks)", row=2, col=1)
    my_figure.update_xaxes(title_text="Months", row=2, col=2)

    my_figure.update_yaxes(title_text="Total Capacity (GW)", row=1, col=1)
    my_figure.update_yaxes(title_text="Total Demand (GWh / Week)", row=1, col=2)
    my_figure.update_yaxes(title_text="Energy Generated (MWh / Week)", row=2, col=1)
    my_figure.update_yaxes(title_text="Storage Levels (GWh)", row=2, col=2)

    my_figure.update_layout(title_text="OSeMOSYS Results", showlegend=True)
    
    
    my_figure.show()



Visualizer(instance)


# # Exercise
# 

# ## For the Instructor
# 
# Choose what the students can change in the model
# 
# * Variable costs, minimum storage charge, capital costs
# * Which technologies will be affected 
# 
# Change the flags to `False` to turn the option off, or leave them as `True` to have students access that parameter

# In[ ]:


VOM_FLAG = False  # Variable cost flag
CC_FLAG  = False  # Capital Cost flag
SMC_FLAG = False # Minimum storage charge flag
Stor_Levels = True # Change storage level Start and Finish

#------------------------------------------------------------------------------------------------#

technologies = Process_Data(TECHNOLOGY_df,component="set") # Getting list of technologies in the model
storage_units = Process_Data(STORAGE_df, component="set") # Getting list of storage facilities in the model

no_change_techs = ["distGAS", "tCOMP", 'tEXTRACT1'] # list of technologies not to be changed by students
for item in no_change_techs:
    if item in technologies:
        technologies.remove(item)

# Creating a dictionary for the instructor to turn on / off which units the students have the liberty to change
instructionary = dict(zip(technologies, np.full((1,len(technologies)), True)[0])) # Dictionary of technologies for which the students should have access (default = True for all)
for key, val in zip(storage_units, np.full((1,len(storage_units)), True)[0]):
    instructionary[key] = val 


# ## For the Students
# 
# Set new values for:
# 
# * Variable costs (VOM)
# * Capital costs
# * Minimum storage charge

# In[ ]:


# Change Variable Costs (VOM)
if VOM_FLAG is True:
    instance.VariableCost.pprint()
    for k in instance.VariableCost:
        if k[1] in instructionary.keys() and k[2] == 1:
            instance.VariableCost[k] = float(input("Set a value for Variable Cost for " + k[1] + " "))
    print("----" * 100)
    instance.VariableCost.pprint()

print("###" * 100)

# Change Capital Costs
if CC_FLAG is True:
    instance.CapitalCost.pprint()
    for k in instance.CapitalCost:
        if k[1] in instructionary.keys():
            instance.CapitalCost[k] = float(input("Set a value for Capital Cost for " + k[1] + " "))
    print("----" * 100)
    instance.CapitalCost.pprint()

print("###" * 100)

if SMC_FLAG is True:
    storage_switch = input("Would you like to turn storage off? ")
    if storage_switch in ["Yes", "yes"]:
        for k in instance.MinStorageCharge:
            if k[1] in instructionary.keys():
                instance.MinStorageCharge[k] = 1
                print("Storage for " + k[1] +  " is turned off")
    else:
        for k in instance.MinStorageCharge:
            if k[1] in instructionary.keys():
                instance.MinStorageCharge[k] = 0

    print("----" * 100)
    #instance.MinStorageCharge.pprint()

print("###" * 100)

if Stor_Levels is True:
  instance.StorageLevelStart.pprint()
  start_level = float(input("Set a new storage level for the START of the year (in GWh): "))
  instance.StorageLevelFinish.pprint()
  finish_level = float(input("Set a new storage level for the END of the year (in GWh): "))
  for k in instance.StorageLevelStart:
    if k[1] in instructionary.keys():
      instance.StorageLevelStart[k] = start_level
  for j in instance.StorageLevelFinish:
    if j[1] in instructionary.keys():
      instance.StorageLevelFinish[k] = finish_level
  print("----" * 100)
  instance.StorageLevelStart.pprint()
  instance.StorageLevelFinish.pprint()


print("###" * 100)


# -------------------------------------------------------------
# 
# # Solve the model again with altered values
# 
# -------------------------------------------------------------

# In[ ]:


changed_results = opt.solve(instance, tee=True).write()

