from __future__ import division
import sys
from pyomo.environ import *
from pyomo.core import *
from pyomo.util.infeasible import log_infeasible_constraints
from pyomo.opt import SolverFactory

##################################################################################################
'Rate of Demand - Equations'

def EQ_SpecifiedDemand_rule(model, r, l, f, y):
    result1 = model.SpecifiedAnnualDemand[r, f, y] * model.SpecifiedDemandProfile[r, f, l, y] / model.YearSplit[l, y]
    result2 = model.RateOfDemand[r, l, f, y]
    return result1 == result2
# SpecifiedAnnualDemand[r,f,y]*SpecifiedDemandProfile[r,f,l,y] / YearSplit[l,y]=RateOfDemand[r,l,f,y];

#def Demand_rule(model, r, f, y):
#    result1 = sum(model.Demand[r, l, f, y] for l in model.TIMESLICE)
#    result2 = model.DemandAnnual[r, f, y]
#    return result1 == result2
'31-Oct-2022: An element from Kevin Palmer-Wilsons model; verify if needed.'
'# 04-Nov-2022: Turning off this rule; as it is not used elsewhere.'

##################################################################################################
'Capacity Adequacy A - Equations'

def CAa1_TotalNewCapacity_rule(model, r, t, y):
    result1 = model.AccumulatedNewCapacity [r, t, y] 
    result2 = sum(model.NewCapacity [r, t, yy]
                for yy in model.YEAR if y - yy < model.OperationalLife[r, t] and y - yy >= 0)
    return result1 == result2
# AccumulatedNewCapacity[r,t,y] = sum{yy in YEAR: y-yy < OperationalLife[r,t] && y-yy>=0} NewCapacity[r,t,yy];

def CAa2_TotalAnnualCapacity_rule(model, r, t, y):
    result1 = model.AccumulatedNewCapacity[r, t, y] + model.ResidualCapacity[r, t, y]
    result2 = model.TotalCapacityAnnual[r, t, y]
    return result1 == result2
# AccumulatedNewCapacity[r,t,y]+ ResidualCapacity[r,t,y] = TotalCapacityAnnual[r,t,y];

def CAa3_TotalActivityOfEachTechnology_rule(model, r, t, l, y):
    result1 = sum(model.RateOfActivity[r, l, t, m, y] for m in model.MODE_OF_OPERATION)
    result2 = model.RateOfTotalActivity[r, t, l, y]
    return result1 == result2
# sum{m in MODE_OF_OPERATION} RateOfActivity[r,l,t,m,y] = RateOfTotalActivity[r,t,l,y];

def CAa4_ConstraintCapacity_rule(model, r, l, t, y):
    result1 = model.RateOfTotalActivity[r, t, l, y]
    result2 = model.TotalCapacityAnnual[r, t, y] * model.CapacityFactor[r, t, l, y] * model.CapacityToActivityUnit[r, t]
    return result1 <= result2
# RateOfTotalActivity[r,t,l,y] <= TotalCapacityAnnual[r,t,y] * CapacityFactor[r,t,l,y]*CapacityToActivityUnit[r,t];

def CAa5_TotalNewCapacity_rule(model, r, t, y):
    if model.CapacityOfOneTechnologyUnit[r, t, y] != 0:
        result1 = model.CapacityOfOneTechnologyUnit[r,t,y] * model.NumberOfNewTechnologyUnits[r,t,y]
        result2 = model.NewCapacity[r,t,y]
        return result1 == result2
    
    else:
        return Constraint.Skip
# 31-Oct-2022: Verified equation against documentation & go-by. It will not match the go-by exactly because all the equations in this code are written using 'result1' &/or 'result2'.
# Equation used from go-by was TotalNewCapacity_2_rule
# CapacityOfOneTechnologyUnit[r,t,y]<>0}: CapacityOfOneTechnologyUnit[r,t,y]*NumberOfNewTechnologyUnits[r,t,y] = NewCapacity[r,t,y];

##################################################################################################
'Capacity Adequacy B - Equations'

def CAb1_PlannedMaintenance_rule(model, r, t, y):
    result1 = (
        sum(
            model.RateOfTotalActivity[r, t, l, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
    )
    result2 = (
        sum(
            model.TotalCapacityAnnual[r, t, y]
            * model.CapacityFactor[r, t, l, y]
            * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        * model.AvailabilityFactor[r, t, y]
        * model.CapacityToActivityUnit[r, t]
    )

    return result1 <= result2
# 31-Oct-2022: Updated equation as per documentation & go-by
# sum{l in TIMESLICE} RateOfTotalActivity[r,t,l,y]*YearSplit[l,y] <= sum{l in TIMESLICE} 
# (TotalCapacityAnnual[r,t,y]*CapacityFactor[r,t,l,y]*YearSplit[l,y])* AvailabilityFactor[r,t,y]*CapacityToActivityUnit[r,t];

def CAb1_PlannedMaintenance_Negative_rule(model, r,t,y):
    result1 = (
        sum(
            model.RateOfTotalActivity[r, t, l, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
    )
    result2 = (-1) * (
        sum(
            model.TotalCapacityAnnual[r, t, y]
            * model.CapacityFactor[r, t, l, y]
            * model.YearSplit[l, y]
            for l in model.TIMESLICE
        )
        * model.AvailabilityFactor[r, t, y]
        * model.CapacityToActivityUnit[r, t]
    )

    return result1 >= result2
# 31-Oct-2022: Updated equation as per documentation, go-by, & Kevin Palmer-Wilson's code.

##################################################################################################
'Energy Balance A - Equations'

def EBa1_RateOfFuelProduction1_rule(model, r, l, f, t, m, y):
    if model.OutputActivityRatio[r, t, f, m, y] != 0: 
        result1 = model.RateOfProductionByTechnologyByMode[r, l, t, m, f, y]
        result2 = model.RateOfActivity[r, l, t, m, y] * model.OutputActivityRatio[r, t, f, m, y] 
        return result1 == result2
    else:
        return  model.RateOfProductionByTechnologyByMode[r, l, t, m, f, y] == 0
# RateOfActivity[r,l,t,m,y]*OutputActivityRatio[r,t,f,m,y]  = RateOfProductionByTechnologyByMode[r,l,t,m,f,y];

def EBa2_RateOfFuelProduction2_rule(model, r, l, f, t, y):
    result1 = model.RateOfProductionByTechnology[r, l, t, f, y]
    result2 = sum(model.RateOfProductionByTechnologyByMode[r, l, t, m, f, y] 
                for m in model.MODE_OF_OPERATION)
    return result1 == result2
# sum{m in MODE_OF_OPERATION: OutputActivityRatio[r,t,f,m,y] <>0} RateOfProductionByTechnologyByMode[r,l,t,m,f,y] = RateOfProductionByTechnology[r,l,t,f,y];

def EBa3_RateOfFuelProduction3_rule(model, r, l, f, y):
    result1 = model.RateOfProduction[r, l, f, y]
    result2 = sum(model.RateOfProductionByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY)
    return result1 == result2
# sum{t in TECHNOLOGY} RateOfProductionByTechnology[r,l,t,f,y]  =  RateOfProduction[r,l,f,y];

def EBa4_RateOfFuelUse1_rule(model, r, l, f, t, m, y):
#    if(model.InputActivityRatio[r, t, f, m, y] != 0):
        result1 = model.RateOfActivity[r, l, t, m, y] * model.InputActivityRatio[r, t, f, m, y] 
        result2 = model.RateOfUseByTechnologyByMode [r, l, t, m, f, y]
        return result1 == result2
#    else:
#        return Constraint.Skip    
# RateOfActivity[r,l,t,m,y]*InputActivityRatio[r,t,f,m,y]  = RateOfUseByTechnologyByMode[r,l,t,m,f,y];
'04-Nov-2022: Go-by & equation do not have if-else statements'
'04-Nov-2022: May need to turn it off'

def EBa5_RateOfFuelUse2_rule(model, r, l, f, t, y):
    result1 = model.RateOfUseByTechnology [r, l, t, f, y]
    result2 = sum(model.RateOfUseByTechnologyByMode [r, l, t, m, f, y] 
                for m in model.MODE_OF_OPERATION if model.InputActivityRatio [r, t, f, m, y] != 0)
    return result1 == result2
# sum{m in MODE_OF_OPERATION: InputActivityRatio[r,t,f,m,y]<>0} RateOfUseByTechnologyByMode[r,l,t,m,f,y] = RateOfUseByTechnology[r,l,t,f,y];

def EBa6_RateOfFuelUse3_rule(model, r, l, f, y):
    result1 = sum(model.RateOfUseByTechnology[r, l, t, f, y] for t in model.TECHNOLOGY)
    result2 = model.RateOfUse[r, l, f, y]
    return result1 == result2
# sum{t in TECHNOLOGY} RateOfUseByTechnology[r,l,t,f,y]  = RateOfUse[r,l,f,y];

def EBa7_EnergyBalanceEachTS1_rule(model, r, l, f, y):
    result1 = model.RateOfProduction[r, l, f, y] * model.YearSplit[l, y]
    result2 = model.Production[r, l, f, y]
    return result1 == result2
# RateOfProduction[r,l,f,y]*YearSplit[l,y] = Production[r,l,f,y];

def EBa8_EnergyBalanceEachTS2_rule(model, r, l, f, y):
	result1 = model.RateOfUse[r, l, f, y] * model.YearSplit[l, y]
	result2 = model.Use[r, l, f, y]
	return result1 == result2
# RateOfUse[r,l,f,y]*YearSplit[l,y] = Use[r,l,f,y];

def EBa9_EnergyBalanceEachTS3_rule(model, r, l, f, y):
    result1 = model.RateOfDemand[r, l, f, y] * model.YearSplit[l, y]
    result2 = model.Demand[r, l, f, y]
    return result1 == result2
# RateOfDemand[r,l,f,y]*YearSplit[l,y] = Demand[r,l,f,y];

def EBa10_EnergyBalanceEachTS4_rule(model, r, rr, l, f, y):
    result1 = model.Trade[r, rr, l, f, y]
    result2 = -model.Trade[rr, r, l, f, y]
    return result1 == result2
# Trade[r,rr,l,f,y] = -Trade[rr,r,l,f,y];
'Check if there is a better implementation of this equation - the go-by seems slightly different.'
'Perhaps there are some implementation issues.'

def EBa11_EnergyBalanceEachTS5_rule(model, r, l, f, y):
	result1 = model.Production[r, l, f, y] 
	result2 = model.Demand[r, l, f, y] + model.Use[r, l, f, y] + sum(model.Trade[r, rr, l, f, y] * model.TradeRoute[r, rr, f, y]
                                                                       for rr in model.REGION)
	return result1 >= result2
# Production[r,l,f,y] >= Demand[r,l,f,y] + Use[r,l,f,y] + sum{rr in REGION} Trade[r,rr,l,f,y]*TradeRoute[r,rr,f,y];

##################################################################################################
'Energy Balance B - Equations'

def EBb1_EnergyBalanceEachYear1_rule(model, r , f , y):
    result1 = sum(model.Production[r, l, f, y] for l in model.TIMESLICE)
    result2 = model.ProductionAnnual[r, f, y]
    return result1 == result2
# sum{l in TIMESLICE} Production[r,l,f,y] = ProductionAnnual[r,f,y];

def EBb2_EnergyBalanceEachYear2_rule(model, r, f, y): 
    result1 = sum(model.Use[r, l, f, y] 
                for l in model.TIMESLICE)
    result2 = model.UseAnnual[r, f, y]
    return result1 == result2
# sum{l in TIMESLICE} Use[r,l,f,y] = UseAnnual[r,f,y];

def EBb3_EnergyBalanceEachYear3_rule(model, r, rr, f , y):
    result1 = sum(model.Trade[r,rr,l,f,y] 
                for l in model.TIMESLICE)
    result2 = model.TradeAnnual[r,rr,f,y]
    return result1 == result2
# sum{l in TIMESLICE} Trade[r,rr,l,f,y] = TradeAnnual[r,rr,f,y];

def EBb4_EnergyBalanceEachYear4_rule(model, r, f, y):
    result1 = model.ProductionAnnual[r, f, y]
    result2 = model.UseAnnual[r,f,y] + sum( 
                model.TradeAnnual[r, rr, f, y] * model.TradeRoute[r, rr, f, y] 
                for rr in model.REGION) + model.AccumulatedAnnualDemand[r, f, y]
    return result1 >= result2
# ProductionAnnual[r,f,y] >= UseAnnual[r,f,y] + sum{rr in REGION} TradeAnnual[r,rr,f,y]*TradeRoute[r,rr,f,y] + AccumulatedAnnualDemand[r,f,y];

##################################################################################################
'Accounting Technology Production/Use'

def Acc1_FuelProductionByTechnology_rule(model, r, l, t, f, y):
    result1 = model.RateOfProductionByTechnology[r, l, t, f, y] * model.YearSplit[l, y] 
    result2 = model.ProductionByTechnology[r, l, t, f, y]
    return result1 == result2
# RateOfProductionByTechnology[r,l,t,f,y] * YearSplit[l,y] = ProductionByTechnology[r,l,t,f,y];

def Acc2_FuelUseByTechnology_rule(model, r, l, t, f, y):
    result1 = model.RateOfUseByTechnology[r, l, t, f, y] * model.YearSplit [l, y] 
    result2 = model.UseByTechnology [r, l, t, f, y]
    return result1 == result2
# RateOfUseByTechnology[r,l,t,f,y] * YearSplit[l,y] = UseByTechnology[r,l,t,f,y];

def Acc3_AverageAnnualRateOfActivity_rule(model, r, t, m, y): 
    result1 = sum(model.RateOfActivity[r, l, t, m, y] * model.YearSplit [l, y] for l in model.TIMESLICE)
    result2 = model.TotalAnnualTechnologyActivityByMode [r, t, m, y]
    return result1 == result2
# sum{l in TIMESLICE} RateOfActivity[r,l,t,m,y]*YearSplit[l,y] = TotalAnnualTechnologyActivityByMode[r,t,m,y];

def Acc4_ModelPeriodCostByRegion_rule(model, r):
    result1 = sum(model.TotalDiscountedCost[r, y] for y in model.YEAR)
    result2 = model.ModelPeriodCostByRegion[r]
    return result1 == result2
# sum{y in YEAR}TotalDiscountedCost[r,y] = ModelPeriodCostByRegion[r];

##################################################################################################
'Storage Equations'

def S1_RateofStorageCharge_rule(model, r, s, ls, ld, lh, y, t, m):
    if model.TechnologyToStorage[r,t,s,m] > 0:
        result1 = sum(
                model.RateOfActivity[r, l, t, m, y]
                * model.TechnologyToStorage[r, t, s, m]
                * model.Conversionls[l, ls]
                * model.Conversionld[l, ld]
                * model.Conversionlh[l, lh]
                for m in model.MODE_OF_OPERATION
                for l in model.TIMESLICE
                for t in model.TECHNOLOGY
            )
        result2 = model.RateOfStorageCharge[r, s, ls, ld, lh, y]
        return result1 == result2    
    else:
        return Constraint.Skip
# sum{t in TECHNOLOGY, m in MODE_OF_OPERATION, l in TIMESLICE:TechnologyToStorage[r,t,s,m]>0} RateOfActivity[r,l,t,m,y] * 
# TechnologyToStorage[r,t,s,m] * Conversionls[l,ls] * Conversionld[l,ld] * Conversionlh[l,lh] = RateOfStorageCharge[r,s,ls,ld,lh,y];

def S2_RateOfStorageDischarge_rule(model, r, s, ls, ld, lh, y, t, m):
    if model.TechnologyFromStorage[r, t, s, m] > 0:
        result1 = sum(
                model.RateOfActivity[r, l, t, m, y]
                * model.TechnologyFromStorage[r, t, s, m]
                * model.Conversionls[l, ls]
                * model.Conversionld[l, ld]
                * model.Conversionlh[l, lh]
                for m in model.MODE_OF_OPERATION
                for l in model.TIMESLICE
                for t in model.TECHNOLOGY
            )
        result2 = model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
        return result1 == result2
    else:
        return Constraint.Skip
#	sum{t in TECHNOLOGY, m in MODE_OF_OPERATION, l in TIMESLICE:TechnologyFromStorage[r,t,s,m]>0} RateOfActivity[r,l,t,m,y] * 
# TechnologyFromStorage[r,t,s,m] * Conversionls[l,ls] * Conversionld[l,ld] * Conversionlh[l,lh] = RateOfStorageDischarge[r,s,ls,ld,lh,y];

def S3_NetChargeWithinYear_rule(model, r, s, ls, ld, lh, y):
    result1 = sum(
            (
                model.RateOfStorageCharge[r, s, ls, ld, lh, y]
                - model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
            )
            * model.YearSplit[l, y]
            * model.Conversionls[l, ls]
            * model.Conversionld[l, ld]
            * model.Conversionlh[l, lh]
            for l in model.TIMESLICE if model.Conversionls[l,ls] > 0 and model.Conversionld[l,ld] > 0 and model.Conversionlh[l,lh] > 0
        )
    result2 = model.NetChargeWithinYear[r, s, ls, ld, lh, y]
    return result1 == result2
   
# sum{l in TIMESLICE:Conversionls[l,ls]>0&&Conversionld[l,ld]>0&&Conversionlh[l,lh]>0}  (RateOfStorageCharge[r,s,ls,ld,lh,y] - 
# RateOfStorageDischarge[r,s,ls,ld,lh,y]) * YearSplit[l,y] * Conversionls[l,ls] * Conversionld[l,ld] * Conversionlh[l,lh] = 
# NetChargeWithinYear[r,s,ls,ld,lh,y];

def S4_NetChargeWithinDay_rule(model, r, s, ls, ld, lh, y):
    result1 = (model.RateOfStorageCharge[r, s, ls, ld, lh, y] - model.RateOfStorageDischarge[r, s, ls, ld, lh, y]) * model.DaySplit[lh, y]
    result2 = model.NetChargeWithinDay[r, s, ls, ld, lh, y]
    return result1 == result2

# s.t. S4_NetChargeWithinDay{r in REGION, s in STORAGE, ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET, y in YEAR}: 
#	(RateOfStorageCharge[r,s,ls,ld,lh,y] - RateOfStorageDischarge[r,s,ls,ld,lh,y]) * DaySplit[lh,y] = NetChargeWithinDay[r,s,ls,ld,lh,y];

def S5_S6_StorageLevelYearStart_rule(model, r, s, y):
    if y == min(model.YEAR):
        result1 = model.StorageLevelStart[r, s] 
        result2 = model.StorageLevelYearStart[r, s, y]
        return result1 == result2
    else:
        result1 = model.StorageLevelYearStart[r, s, y - 1] + sum(
                model.NetChargeWithinYear[r, s, ls, ld, lh, y - 1]
                for ls in model.SEASON
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
        result2 = model.StorageLevelYearStart[r, s, y]
        return result1 == result2        
# if y = min{yy in YEAR} min(yy) then StorageLevelStart[r,s] else StorageLevelYearStart[r,s,y-1] 
# + sum{ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET} NetChargeWithinYear[r,s,ls,ld,lh,y-1] = StorageLevelYearStart[r,s,y];

def S7_S8_StorageLevelYearFinish_rule(model, r, s, y):
    if y < max(model.YEAR):
        result1 = model.StorageLevelYearStart[r, s, y + 1]
        result2 = model.StorageLevelYearFinish[r, s, y]
        return result1 == result2
    else:
        result1 = model.StorageLevelYearStart[r, s, y] + sum(
                model.NetChargeWithinYear[r, s, ls, ld, lh, y]
                for ls in model.SEASON
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
        result2 = model.StorageLevelYearFinish[r, s, y]
        return result1 == result2       
# if y < max{yy in YEAR} max(yy) then StorageLevelYearStart[r,s,y+1]
# else StorageLevelYearStart[r,s,y] + sum{ls in SEASON, ld in DAYTYPE, lh in DAILYTIMEBRACKET} NetChargeWithinYear[r,s,ls,ld,lh,y] 
# = StorageLevelYearFinish[r,s,y];

def S9_S10_StorageLevelSeasonStart_rule(model, r, s, ls, y):
    if ls == min(model.SEASON):
        result1 = model.StorageLevelYearStart[r, s, y]
        result2 = model.StorageLevelSeasonStart[r, s, ls, y]
        return result1 == result2
    else:
        result1 = model.StorageLevelSeasonStart[r, s, ls - 1, y] + sum(
                model.NetChargeWithinYear[r, s, ls - 1, ld, lh, y]
                for ld in model.DAYTYPE
                for lh in model.DAILYTIMEBRACKET
            )
        result2 = model.StorageLevelSeasonStart[r, s, ls, y]
        return result1 == result2

#  if ls = min{lsls in SEASON} min(lsls) then StorageLevelYearStart[r,s,y] 
#	else StorageLevelSeasonStart[r,s,ls-1,y] + sum{ld in DAYTYPE, lh in DAILYTIMEBRACKET} NetChargeWithinYear[r,s,ls-1,ld,lh,y] 
#	= StorageLevelSeasonStart[r,s,ls,y];

def S11_S12_StorageLevelDayTypeStart_rule(model, r, s, ls, ld, y):
    if ld == min(model.DAYTYPE):
        result1 = model.StorageLevelSeasonStart[r, s, ls, y]
        result2 = model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        return result1 == result2     
    else:
        result1 = model.StorageLevelDayTypeStart[r, s, ls, ld - 1, y] + sum(
                model.NetChargeWithinDay[r, s, ls, ld - 1, lh, y]
                for lh in model.DAILYTIMEBRACKET
            )
        result2 = model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        return result1 == result2     

# if ld = min{ldld in DAYTYPE} min(ldld) then StorageLevelSeasonStart[r,s,ls,y] 
#	else StorageLevelDayTypeStart[r,s,ls,ld-1,y] + sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld-1,lh,y] * DaysInDayType[ls,ld-1,y]
#	= StorageLevelDayTypeStart[r,s,ls,ld,y];

def S13_S14_S15_StorageLevelDayTypeFinish_rule(model, r, s, ls, ld, y):
    if ld == max(model.DAYTYPE):
        if ls == max(model.SEASON):
            result1 = model.StorageLevelYearFinish[r, s, y]
            result2 = model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            return result1 == result2
        else:
            result1 = model.StorageLevelSeasonStart[r, s, ls + 1, y]
            result2 = model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            return result1 == result2        
    else:
        result1 = model.StorageLevelDayTypeFinish[r, s, ls, ld + 1, y] - sum(
                model.NetChargeWithinDay[r, s, ls, ld + 1, lh, y]
                for lh in model.DAILYTIMEBRACKET
            ) * model.DaysInDayType[ls, ld + 1, y]
        result2 = model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
        return result1 == result2
	
# if ls = max{lsls in SEASON} max(lsls) && ld = max{ldld in DAYTYPE} max(ldld) then StorageLevelYearFinish[r,s,y] 
#	else if ld = max{ldld in DAYTYPE} max(ldld) then StorageLevelSeasonStart[r,s,ls+1,y]
#	else StorageLevelDayTypeFinish[r,s,ls,ld+1,y] - sum{lh in DAILYTIMEBRACKET} NetChargeWithinDay[r,s,ls,ld+1,lh,y] * DaysInDayType[ls,ld+1,y]
#	= StorageLevelDayTypeFinish[r,s,ls,ld,y];

##################################################################################################
'Storage Constraints - Equations'

def SC1_LowerLimit_1TimeBracket1InstanceOfDayType1week_rule(model, r, s, ls, ld, lh, y):
    result1 = (
        0 <= (
            model.StorageLevelDayTypeStart[r, s, ls, ld, y] 
            + sum(
                model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh > 0)
            )
        )
        - model.StorageLowerLimit[r, s, y]
    )
    return result1
# 0 <= (StorageLevelDayTypeStart[r,s,ls,ld,y]+sum{lhlh in DAILYTIMEBRACKET:lh-lhlh>0} NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageLowerLimit[r,s,y];

def SC1_UpperLimit_1TimeBracket1InstanceOfDayType1week_rule(model, r, s, ls, ld, lh, y):
    result1 = (
        model.StorageLevelDayTypeStart[r, s, ls, ld, y]
        + sum(
            model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
            for lhlh in model.DAILYTIMEBRACKET
            if (lh - lhlh >0)
        )
    ) - model.StorageUpperLimit[r, s, y] <= 0
    return result1
# (StorageLevelDayTypeStart[r,s,ls,ld,y]+sum{lhlh in DAILYTIMEBRACKET:lh-lhlh>0} NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageUpperLimit[r,s,y] <= 0;

def SC2_LowerLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        result1 = (
            0
            <= (
                model.StorageLevelDayTypeStart[r, s, ls, ld, y]
                - sum(
                    model.NetChargeWithinDay[r, s, ls, ld - 1, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh < 0)
                )
            )
            - model.StorageLowerLimit[r, s, y]
        )
        return result1
    else:
        return Constraint.Skip
# 0 <= if ld > min{ldld in DAYTYPE} min(ldld) then (StorageLevelDayTypeStart[r,s,ls,ld,y]-sum{lhlh in DAILYTIMEBRACKET:lh-lhlh<0} 
# NetChargeWithinDay[r,s,ls,ld-1,lhlh,y])-StorageLowerLimit[r,s,y];	

def SC2_UpperLimit_EndDailyTimeBracketLastInstanceOfDayType1Week_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        result1 = (
            model.StorageLevelDayTypeStart[r, s, ls, ld, y]
            - sum(
                model.NetChargeWithinDay[r, s, ls, ld - 1, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh < 0)
            )
        ) - model.StorageUpperLimit[r, s, y] <= 0
        return result1
    else:
        return Constraint.Skip
# if ld > min{ldld in DAYTYPE} min(ldld) then (StorageLevelDayTypeStart[r,s,ls,ld,y]-sum{lhlh in DAILYTIMEBRACKET:lh-lhlh<0} 
# NetChargeWithinDay[r,s,ls,ld-1,lhlh,y])-StorageUpperLimit[r,s,y] <= 0;

def SC3_LowerLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_rule(model, r, s, ls, ld, lh, y):
    result1 = (
        0
        <= (
            model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
            - sum(
                model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                for lhlh in model.DAILYTIMEBRACKET
                if (lh - lhlh < 0)
            )
        )
        - model.StorageLowerLimit[r, s, y]
    )
    return result1
# 0 <= (StorageLevelDayTypeFinish[r,s,ls,ld,y] - sum{lhlh in DAILYTIMEBRACKET:lh-lhlh<0} NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageLowerLimit[r,s,y];

def SC3_UpperLimit_EndDailyTimeBracketLastInstanceOfDayTypeLastWeek_rule(model, r, s, ls, ld, lh, y):
    result1 = (
        model.StorageLevelDayTypeFinish[r, s, ls, ld, y]
        - sum(
            model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
            for lhlh in model.DAILYTIMEBRACKET
            if (lh - lhlh < 0)
        )
    ) - model.StorageUpperLimit[r, s, y] <= 0
    return result1
# (StorageLevelDayTypeFinish[r,s,ls,ld,y] - sum{lhlh in DAILYTIMEBRACKET:lh-lhlh<0} NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageUpperLimit[r,s,y] <= 0;

def SC4_LowerLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        result1 = (
            0
            <= (
                model.StorageLevelDayTypeFinish[r, s, ls, ld - 1, y]
                + sum(
                    model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh > 0)
                )
            )
            - model.StorageLowerLimit[r, s, y]
        )
        return result1
    else:
        return Constraint.Skip
# 0 <= if ld > min{ldld in DAYTYPE} min(ldld) then (StorageLevelDayTypeFinish[r,s,ls,ld-1,y]+sum{lhlh in DAILYTIMEBRACKET:lh-lhlh>0} 
# NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageLowerLimit[r,s,y];

def SC4_UpperLimit_1TimeBracket1InstanceOfDayTypeLastweek_rule(model, r, s, ls, ld, lh, y):
    if ld > min(model.DAYTYPE):
        result1 = (
            0
            >= (
                model.StorageLevelDayTypeFinish[r, s, ls, ld - 1, y]
                + sum(
                    model.NetChargeWithinDay[r, s, ls, ld, lhlh, y]
                    for lhlh in model.DAILYTIMEBRACKET
                    if (lh - lhlh > 0)
                )
            )
            - model.StorageUpperLimit[r, s, y]
        )
        return result1
    else:
        return Constraint.Skip
# if ld > min{ldld in DAYTYPE} min(ldld) then (StorageLevelDayTypeFinish[r,s,ls,ld-1,y]+sum{lhlh in DAILYTIMEBRACKET:lh-lhlh>0} 
# NetChargeWithinDay[r,s,ls,ld,lhlh,y])-StorageUpperLimit[r,s,y] <= 0;

def SC5_MaxCharge_rule(model, r, s, ls, ld, lh, y):
    result1 = model.RateOfStorageCharge[r, s, ls, ld, lh, y]
    result2 = model.StorageMaxChargeRate[r, s]
    return result1 <= result2
# RateOfStorageCharge[r,s,ls,ld,lh,y] <= StorageMaxChargeRate[r,s];

def SC6_MaxDischarge_rule(model, r, s, ls, ld, lh, y):
    result1 = model.RateOfStorageDischarge[r, s, ls, ld, lh, y]
    result2 = model.StorageMaxDischargeRate[r, s]
    return result1 <= result2
# RateOfStorageDischarge[r,s,ls,ld,lh,y] <= StorageMaxDischargeRate[r,s];

'Adding storage level finish'
def TEMP_StorageLevelFinish_rule(model, r, s, y):
    if y == max(model.YEAR):
        result1 = model.StorageLevelFinish[r, s]
        result2 = model.StorageLevelYearFinish[r, s, y]
        return result1 <= result2
    else:
        return Constraint.Skip

##################################################################################################
'Storage Investments - Equations'

def SI1_StorageUpperLimit_rule(model, r, s, y):
    result1 = model.AccumulatedNewStorageCapacity[r, s, y] + model.ResidualStorageCapacity[r, s, y]
    result2 = model.StorageUpperLimit[r, s, y]
    return result1 == result2
# 24-Oct-2022: Added from Pyomo Go-By

def SI2_StorageLowerLimit_rule(model, r, s, y):
    result1 = model.MinStorageCharge[r, s, y] * model.StorageUpperLimit[r, s, y]
    result2 = model.StorageLowerLimit[r, s, y]
    return result1 == result2
# 24-Oct-2022: Added from Pyomo Go-By

def SI3_TotalNewStorage_rule(model, r, s, y):
    result1 = sum(
            model.NewStorageCapacity[r, s, yy]
            for yy in model.YEAR
            if ((y - yy < model.OperationalLifeStorage[r, s]) and (y - yy >= 0))
        )
    result2 = model.AccumulatedNewStorageCapacity[r, s, y]
    return result1 == result2
# 24-Oct-2022: Added from Pyomo Go-By

def SI4_UndiscountedCapitalInvestmentStorage_rule(model, r, s, y):
    result1 = model.CapitalCostStorage[r, s, y] * model.NewStorageCapacity[r, s, y]
    result2 = model.CapitalInvestmentStorage[r, s, y]
    return result1 == result2
# 24-Oct-2022: Added from Pyomo Go-By

def SI5_DiscountingCapitalInvestmentStorage_rule(model, r, s, y):
    result1 = model.CapitalInvestmentStorage[r, s, y] / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR)))
    result2 = model.DiscountedCapitalInvestmentStorage[r, s, y]
    return result1 == result2
# 24-Oct-2022: Added from Pyomo Go-By

def SI6_SI7_SI8_SalvageValueStorageAtEndOfPeriod_rule(model, r, s, y):
    if (model.DepreciationMethod[r] == 1 and ((y + model.OperationalLifeStorage[r, s] - 1) > max(model.YEAR)) and model.DiscountRate[r] > 0):
        result1 = model.CapitalInvestmentStorage[r, s, y] * (1 - (((1 + model.DiscountRate[r]) ** (max(model.YEAR) - y + 1) - 1)
                / (
                    (1 + model.DiscountRate[r]) ** model.OperationalLifeStorage[r, s]
                    - 1
                )
            )
        )
        result2 = model.SalvageValueStorage[r, s, y]
        return result1 == result2
# DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]>0}: CapitalInvestmentStorage[r,s,y]*(1-(((1+DiscountRate[r])^(max{yy in YEAR} max(yy) - 
# y+1)-1)/((1+DiscountRate[r])^OperationalLifeStorage[r,s]-1))) = SalvageValueStorage[r,s,y];
    elif (model.DepreciationMethod[r] == 1 and ((y + model.OperationalLifeStorage[r, s] - 1) > max(model.YEAR)) and model.DiscountRate[r] == 0) or (model.DepreciationMethod[r] == 2 and (y + model.OperationalLifeStorage[r, s] - 1) > (max(model.YEAR))):
        result1 = model.CapitalInvestmentStorage[r, s, y] * (1 - (max(model.YEAR) - y + 1) / model.OperationalLifeStorage[r, s])
        result2 = model.SalvageValueStorage[r, s, y]
        return result1 == result2
# (DepreciationMethod[r]=1 && (y+OperationalLifeStorage[r,s]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]=0) || (DepreciationMethod[r]=2 && (y+OperationalLifeStorage[r,s]-1) > 
# (max{yy in YEAR} max(yy)))}: CapitalInvestmentStorage[r,s,y]*(1-(max{yy in YEAR} max(yy) - y+1)/OperationalLifeStorage[r,s]) = SalvageValueStorage[r,s,y];
    elif (y + model.OperationalLifeStorage[r,s] - 1 <= max(model.YEAR)):
        return model.SalvageValueStorage[r, s, y] == 0
    else:
        return Constraint.Skip
'Review this equation again - it was a combination of the go-by & documentation; there were major differences in the original KPW implementation'

def SI9_SalvageValueStorageDiscountedToStartYear_rule(model, r, s, y):
    result1 = model.SalvageValueStorage[r, s, y] / ((1 + model.DiscountRate[r]) ** (max(model.YEAR) - min(model.YEAR) + 1))
    result2 = model.DiscountedSalvageValueStorage[r, s, y]
    return result1 == result2 
# SalvageValueStorage[r,s,y]/((1+DiscountRate[r])^(max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)+1)) = DiscountedSalvageValueStorage[r,s,y];

def SI10_TotalDiscountedCostByStorage_rule(model, r, s, y):
    result1 = model.DiscountedCapitalInvestmentStorage[r, s, y] - model.DiscountedSalvageValueStorage[r, s, y]
    result2 = model.TotalDiscountedStorageCost[r, s, y]
    return result1 == result2
# DiscountedCapitalInvestmentStorage[r,s,y]-DiscountedSalvageValueStorage[r,s,y] = TotalDiscountedStorageCost[r,s,y];

##################################################################################################
'Capital Costs - Equations'

def CC1_UndiscountedCapitalInvestment_rule(model, r, t, y):
    result1 =  model.CapitalCost[r, t, y] * model.NewCapacity[r, t, y]
    result2 = model.CapitalInvestment[r, t, y]
    return result1 == result2
# CapitalCost[r,t,y] * NewCapacity[r,t,y] = CapitalInvestment[r,t,y];

def CC2_DiscountedCapitalInvestment_rule(model, r, t, y):
    result1 = model.CapitalInvestment[r, t, y] / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR)))
    result2 = model.DiscountedCapitalInvestment[r, t, y]
    return result1 == result2
# CapitalInvestment[r,t,y]/((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy))) = DiscountedCapitalInvestment[r,t,y];

##################################################################################################
'Salvage Value - Equations'

def SV1_SV2_SV3_SalvageValueAtEndOfPeriod_rule(model, r, t, y):
    if (model.DepreciationMethod[r] == 1 and ((y + model.OperationalLife[r, t] - 1) > max(model.YEAR)) and model.DiscountRate[r] > 0):
        result1 = model.CapitalCost[r, t, y] * model.NewCapacity[r, t, y] * (1 - (
            ((1 + model.DiscountRate[r]) ** (max(model.YEAR) - y + 1) - 1) / 
            ((1 + model.DiscountRate[r]) ** model.OperationalLife[r, t] - 1)
            )
        )
        result2 = model.SalvageValue[r, t, y]
        return result1 == result2
# DepreciationMethod[r]=1 && (y + OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]>0}: 
# SalvageValue[r,t,y] = CapitalCost[r,t,y]*NewCapacity[r,t,y]*(1-(((1+DiscountRate[r])^(max{yy in YEAR} max(yy) - y+1)-1)/((1+DiscountRate[r])^OperationalLife[r,t]-1)));
    elif (model.DepreciationMethod[r] == 1 and ((y + model.OperationalLife[r,t] - 1) > max(model.YEAR)) and model.DiscountRate[r] == 0 or (model.DepreciationMethod[r] == 2 and (y + model.OperationalLife[r,t] -1) > max(model.YEAR))):
        result1 = model.CapitalCost[r, t, y] * model.NewCapacity[r, t, y] * (1 - (max(model.YEAR) - y + 1) / model.OperationalLife[r, t])
        result2 = model.SalvageValueStorage[r,t,y]
        return result1 == result2
# (DepreciationMethod[r]=1 && (y + OperationalLife[r,t]-1) > (max{yy in YEAR} max(yy)) && DiscountRate[r]=0) || (DepreciationMethod[r]=2 && (y + OperationalLife[r,t]-1) > 
# (max{yy in YEAR} max(yy)))}: SalvageValue[r,t,y] = CapitalCost[r,t,y]*NewCapacity[r,t,y]*(1-(max{yy in YEAR} max(yy) - y+1)/OperationalLife[r,t]);
    elif (y + model.OperationalLife[r,t] - 1) <= max(model.YEAR):
        return model.SalvageValue[r,t,y] == 0
# (y + OperationalLife[r,t]-1) <= (max{yy in YEAR} max(yy))}: SalvageValue[r,t,y] = 0;
    else:
        return Constraint.Skip

def SV4_SalvageValueDiscountedToStartYear_rule(model, r, t, y):
    result1 = model.SalvageValue[r, t, y] / (
        (1 + model.DiscountRate[r]) ** (1 + max(model.YEAR) - min(model.YEAR))
    )
    result2 = model.DiscountedSalvageValue[r, t, y]
    return result1 == result2
# DiscountedSalvageValue[r,t,y] = SalvageValue[r,t,y]/((1+DiscountRate[r])^(1+max{yy in YEAR} max(yy)-min{yy in YEAR} min(yy)));

##################################################################################################
'Operating Costs - Equations'

def OC1_OperatingCostsVariable_rule(model, r, t, y):
    result1 = sum(model.TotalAnnualTechnologyActivityByMode[r, t, m, y] * model.VariableCost[r, t, m, y]
                for m in model.MODE_OF_OPERATION)
    result2 = model.AnnualVariableOperatingCost[r, t, y]
    return result1 == result2
# sum{m in MODE_OF_OPERATION} TotalAnnualTechnologyActivityByMode[r,t,m,y]*VariableCost[r,t,m,y] = AnnualVariableOperatingCost[r,t,y];

def OC2_OperatingCostsFixedAnnual_rule(model, r, t, y):
    result1 = model.TotalCapacityAnnual[r, t, y] * model.FixedCost[r, t, y]
    result2 = model.AnnualFixedOperatingCost[r, t, y]
    return result1 == result2
# TotalCapacityAnnual[r,t,y]*FixedCost[r,t,y] = AnnualFixedOperatingCost[r,t,y];

def OC3_OperatingCostsTotalAnnual_rule(model, r, t, y):
    result1 = model.AnnualFixedOperatingCost[r, t, y] + model.AnnualVariableOperatingCost[r, t, y]
    result2 = model.OperatingCost[r, t, y]
    return result1 == result2
# AnnualFixedOperatingCost[r,t,y]+AnnualVariableOperatingCost[r,t,y] = OperatingCost[r,t,y];

def OC4_DiscountedOperatingCostsTotalAnnual_rule(model, r, t, y):
    result1 = model.OperatingCost[r, t, y] / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR) + 0.5))
    result2 = model.DiscountedOperatingCost[r, t, y]
    return result1 == result2
# OperatingCost[r,t,y]/((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy)+0.5)) = DiscountedOperatingCost[r,t,y];

##################################################################################################
'Total Discounted Costs - Equations'

def TDC1_TotalDiscountedCostByTechnology_rule(model, r, t, y):
    result1 = model.DiscountedOperatingCost[r, t, y] + model.DiscountedCapitalInvestment[r, t, y] + model.DiscountedTechnologyEmissionsPenalty[r, t, y] - model.DiscountedSalvageValue[r, t, y]
    result2 = model.TotalDiscountedCostByTechnology[r, t, y]
    return result1 == result2
# DiscountedOperatingCost[r,t,y]+DiscountedCapitalInvestment[r,t,y]+DiscountedTechnologyEmissionsPenalty[r,t,y]-DiscountedSalvageValue[r,t,y] = TotalDiscountedCostByTechnology[r,t,y];

def TDC2_TotalDiscountedCost_rule(model, r, y):
    result1 = sum(model.TotalDiscountedCostByTechnology[r, t, y] for t in model.TECHNOLOGY) + sum(model.TotalDiscountedStorageCost[r, s, y] for s in model.STORAGE)
    result2 = model.TotalDiscountedCost[r, y]
    return result1 == result2
# sum{t in TECHNOLOGY} TotalDiscountedCostByTechnology[r,t,y]+sum{s in STORAGE} TotalDiscountedStorageCost[r,s,y] = TotalDiscountedCost[r,y];

##################################################################################################
'Total Capacity Constraints'

def TCC1_TotalAnnualMaxCapacityConstraint_rule(model, r, t, y):
    result1 = model.TotalCapacityAnnual[r, t, y]
    result2 = model.TotalAnnualMaxCapacity[r, t, y]
    return result1 <= result2
# TotalCapacityAnnual[r,t,y] <= TotalAnnualMaxCapacity[r,t,y];

def TCC2_TotalAnnualMinCapacityConstraint_rule(model, r, t, y):
    if model.TotalAnnualMinCapacity[r, t, y] > 0:
        result1 = model.TotalCapacityAnnual[r, t, y]
        result2 = model.TotalAnnualMinCapacity[r, t, y]
        return result1 >= result2
    else:
        return Constraint.Skip
# TotalAnnualMinCapacity[r,t,y]>0}: TotalCapacityAnnual[r,t,y] >= TotalAnnualMinCapacity[r,t,y];

##################################################################################################
'New Capacity Constraints - Equations'

def NCC1_TotalAnnualMaxNewCapacityConstraint_rule(model, r,t,y):
    result1 = model.NewCapacity[r, t, y]
    result2 = model.TotalAnnualMaxCapacityInvestment[r, t, y]
    return result1 <= result2
# NewCapacity[r,t,y] <= TotalAnnualMaxCapacityInvestment[r,t,y];

def NCC2_TotalAnnualMinNewCapacityConstraint_rule(model, r, t, y):
    if model.TotalAnnualMinCapacityInvestment[r,t,y] > 0:
        result1 = model.NewCapacity[r, t, y]
        result2 = model.TotalAnnualMinCapacityInvestment[r, t, y]
        return result1 >= result2
    return Constraint.Skip
# TotalAnnualMinCapacityInvestment[r,t,y]>0}: NewCapacity[r,t,y] >= TotalAnnualMinCapacityInvestment[r,t,y];

##################################################################################################
'Annual Activity Constraints - Equations'

def AAC1_TotalAnnualTechnologyActivity_rule(model, r, t, y):
    result1 = sum(model.RateOfTotalActivity[r, t, l, y] * model.YearSplit[l, y]
            for l in model.TIMESLICE)
    result2 = model.TotalTechnologyAnnualActivity[r, t, y]
    return result1 == result2
# sum{l in TIMESLICE} RateOfTotalActivity[r,t,l,y]*YearSplit[l,y] = TotalTechnologyAnnualActivity[r,t,y];

def AAC2_TotalAnnualTechnologyActivityUpperLimit_rule(model, r,t,y):
    result1 = model.TotalTechnologyAnnualActivity[r, t, y]
    result2 = model.TotalTechnologyAnnualActivityUpperLimit[r, t, y]
    return result1 <= result2
# TotalTechnologyAnnualActivity[r,t,y] <= TotalTechnologyAnnualActivityUpperLimit[r,t,y] ;

def AAC3_TotalAnnualTechnologyActivityLowerLimit_rule(model, r,t,y):
    result1 = model.TotalTechnologyAnnualActivity[r, t, y]
    result2 = model.TotalTechnologyAnnualActivityLowerLimit[r, t, y]
    return result1 >= result2
# TotalTechnologyAnnualActivityLowerLimit[r,t,y]>0}: TotalTechnologyAnnualActivity[r,t,y] >= TotalTechnologyAnnualActivityLowerLimit[r,t,y] ;

##################################################################################################
'Total Activity Constraints - Equations'

def TAC1_TotalModelHorizonTechnologyActivity_rule(model, r, t):
    result1 = sum(model.TotalTechnologyAnnualActivity[r, t, y] for y in model.YEAR)
    result2 = model.TotalTechnologyModelPeriodActivity[r, t]
    return result1 == result2
# sum{y in YEAR} TotalTechnologyAnnualActivity[r,t,y] = TotalTechnologyModelPeriodActivity[r,t];

def TAC2_TotalModelHorizonTechnologyActivityUpperLimit_rule(model,r,t):
    if model.TotalTechnologyModelPeriodActivityUpperLimit[r, t] > 0:
        result1 = model.TotalTechnologyModelPeriodActivity[r, t]
        result2 = model.TotalTechnologyModelPeriodActivityUpperLimit[r, t]
        return result1 <= result2
    else:
        return Constraint.Skip
# TotalTechnologyModelPeriodActivityUpperLimit[r,t]>0}: TotalTechnologyModelPeriodActivity[r,t] <= TotalTechnologyModelPeriodActivityUpperLimit[r,t];
' Check with Cristiano to make sure these Constraint.Skip statements make sense'

def TAC3_TotalModelHorizenTechnologyActivityLowerLimit_rule(model, r, t):
    if model.TotalTechnologyModelPeriodActivityLowerLimit[r, t] > 0:
        result1 = model.TotalTechnologyModelPeriodActivity[r, t]
        result2 = model.TotalTechnologyModelPeriodActivityLowerLimit[r, t]
        return result1 >= result2
    else:
        return Constraint.Skip    
# TotalTechnologyModelPeriodActivityLowerLimit[r,t]>0}: TotalTechnologyModelPeriodActivity[r,t] >= TotalTechnologyModelPeriodActivityLowerLimit[r,t];
' Check with Cristiano to make sure these Constraint.Skip statements make sense'

##################################################################################################
'Reserve Margin Constraints - Equations'

def RM1_ReserveMargin_TechnologiesIncluded_rule(model, r, l, y):
    result1 = sum(
            (
                model.TotalCapacityAnnual[r, t, y]
                * model.ReserveMarginTagTechnology[r, t, y]
                * model.CapacityToActivityUnit[r, t]
            )
            for t in model.TECHNOLOGY
        )
    result2 = model.TotalCapacityInReserveMargin[r, y]
    return result1 == result2
# sum {t in TECHNOLOGY} TotalCapacityAnnual[r,t,y] * ReserveMarginTagTechnology[r,t,y] * CapacityToActivityUnit[r,t]	 = 	TotalCapacityInReserveMargin[r,y];

def RM2_ReserveMargin_FuelsIncluded_rule(model, r, l, y):
    result1 = sum(
            (model.RateOfProduction[r, l, f, y] * model.ReserveMarginTagFuel[r, f, y])
            for f in model.FUEL
        )
    result2 = model.DemandNeedingReserveMargin[r, l, y]
    return result1 == result2
# sum {f in FUEL} RateOfProduction[r,l,f,y] * ReserveMarginTagFuel[r,f,y] = DemandNeedingReserveMargin[r,l,y];

def RM3_ReserveMargin_Constraint_rule(model, r,l,y):
    result1 = model.DemandNeedingReserveMargin[r, l, y] * model.ReserveMargin[r, y]
    result2 = model.TotalCapacityInReserveMargin[r, y]
    #if (type(result1) == int or type(result2) == int):
    #    if result1 <= result2:
    #        return Constraint.Feasible
    #    else:
    #        return Constraint.Infeasible
    #else:
    return result1 <= result2
# DemandNeedingReserveMargin[r,l,y] * ReserveMargin[r,y]<= TotalCapacityInReserveMargin[r,y];

##################################################################################################
'RE Production Target - Equations'

def RE1_FuelProductionByTechnologyAnnual_rule(model, r, t, f, y):
    result1 = sum(model.ProductionByTechnology[r, l, t, f, y] for l in model.TIMESLICE)
    result2 = model.ProductionByTechnologyAnnual[r, t, f, y]
    return result1 == result2
# sum{l in TIMESLICE} ProductionByTechnology[r,l,t,f,y] = ProductionByTechnologyAnnual[r,t,f,y];

def RE2_TechIncluded_rule(model, r, y):
	result1 = sum(model.ProductionByTechnologyAnnual[r, t, f, y] * model.RETagTechnology[r, t, y]
			    for t in model.TECHNOLOGY for f in model.FUEL)
	result2 = model.TotalREProductionAnnual[r, y]
	return result1 == result2
# sum{t in TECHNOLOGY, f in FUEL} ProductionByTechnologyAnnual[r,t,f,y]*RETagTechnology[r,t,y] = TotalREProductionAnnual[r,y];

def RE3_FuelIncluded_rule(model, r, y):
	result1 = sum(model.RateOfProduction[r, l, f, y] * model.RETagFuel[r, f, y] * model.YearSplit[l, y]
			    for f in model.FUEL for l in model.TIMESLICE)
	result2 = model.RETotalProductionOfTargetFuelAnnual[r, y]
	return result1 == result2
# sum{l in TIMESLICE, f in FUEL} RateOfProduction[r,l,f,y]*YearSplit[l,y]*RETagFuel[r,f,y] = RETotalProductionOfTargetFuelAnnual[r,y]; 

def RE4_EnergyConstraint_rule(model, r, y):
    result1 = model.REMinProductionTarget[r, y] * model.RETotalProductionOfTargetFuelAnnual[r, y]
    result2 = model.TotalREProductionAnnual[r, y]
    # if (type(result1) == int or type(result2) == int):
    #     if result1 <= result2:
    #         return Constraint.Feasible
    #     else:
    #         return Constraint.Infeasible
    # else:
    return result1 <= result2
# REMinProductionTarget[r,y]*RETotalProductionOfTargetFuelAnnual[r,y] <= TotalREProductionAnnual[r,y];

def RE5_FuelUseByTechnologyAnnual_rule(model, r, t, f, y):
	result1 = sum(model.RateOfUseByTechnology[r, l, t, f, y] * model.YearSplit[l, y]
			    for l in model.TIMESLICE)
	result2 = model.UseByTechnologyAnnual[r, t, f, y]
	return result1 == result2
# sum{l in TIMESLICE} RateOfUseByTechnology[r,l,t,f,y]*YearSplit[l,y] = UseByTechnologyAnnual[r,t,f,y];

##################################################################################################
'Emissions Accounting - Equations'

def E1_AnnualEmissionProductionByMode_rule(model, r, t, e, m, y):
    if model.EmissionActivityRatio[r, t, e, m, y] != 0:
        result1 = model.EmissionActivityRatio[r, t, e, m, y] * model.TotalAnnualTechnologyActivityByMode[r, t, m, y]
        result2 = model.AnnualTechnologyEmissionByMode[r, t, e, m, y]
        return result1 == result2
    else:
        return model.AnnualTechnologyEmissionByMode[r, t, e, m, y] == 0
# EmissionActivityRatio[r,t,e,m,y]*TotalAnnualTechnologyActivityByMode[r,t,m,y]=AnnualTechnologyEmissionByMode[r,t,e,m,y];

def E2_AnnualEmissionProduction_rule(model, r, t, e, y):
    result1 = sum(
            model.AnnualTechnologyEmissionByMode[r, t, e, m, y]
            for m in model.MODE_OF_OPERATION
        )
    result2 = model.AnnualTechnologyEmission[r, t, e, y]
    return result1 == result2
# sum{m in MODE_OF_OPERATION} AnnualTechnologyEmissionByMode[r,t,e,m,y] = AnnualTechnologyEmission[r,t,e,y];

def E3_EmissionPenaltyByTechAndEmission_rule(model, r, t, e, y):
    result1 = model.AnnualTechnologyEmission[r, t, e, y] * model.EmissionsPenalty[r, e, y]
    result2 = model.AnnualTechnologyEmissionPenaltyByEmission[r, t, e, y]
    return result1 == result2
# AnnualTechnologyEmission[r,t,e,y]*EmissionsPenalty[r,e,y] = AnnualTechnologyEmissionPenaltyByEmission[r,t,e,y];

def E4_EmissionsPenaltyByTechnology_rule(model, r, t, y):
    result1 = sum(
            model.AnnualTechnologyEmissionPenaltyByEmission[r, t, e, y]
            for e in model.EMISSION
        )
    result2 = model.AnnualTechnologyEmissionsPenalty[r, t, y]
    return result1 == result2
# sum{e in EMISSION} AnnualTechnologyEmissionPenaltyByEmission[r,t,e,y] = AnnualTechnologyEmissionsPenalty[r,t,y];

def E5_DiscountedEmissionsPenaltyByTechnology_rule(model, r, t, y):
    result1 = model.AnnualTechnologyEmissionsPenalty[r, t, y] / ((1 + model.DiscountRate[r]) ** (y - min(model.YEAR) + 0.5))
    result2 = model.DiscountedTechnologyEmissionsPenalty[r, t, y]
    return result1 == result2
# AnnualTechnologyEmissionsPenalty[r,t,y]/((1+DiscountRate[r])^(y-min{yy in YEAR} min(yy)+0.5)) = DiscountedTechnologyEmissionsPenalty[r,t,y];

def E6_EmissionsAccounting1_rule(model, r, e, y):
    result1 = sum(model.AnnualTechnologyEmission[r, t, e, y] for t in model.TECHNOLOGY)
    result2 = model.AnnualEmissions[r, e, y]
    return result1 == result2
# sum{t in TECHNOLOGY} AnnualTechnologyEmission[r,t,e,y] = AnnualEmissions[r,e,y];    

def E7_EmissionsAccounting2_rule(model, r, e):
    result1 = sum(model.AnnualEmissions[r, e, y] for y in model.YEAR)
    result2 = model.ModelPeriodEmissions[r, e] - model.ModelPeriodExogenousEmission[r, e]
    return result1 == result2
# sum{y in YEAR} AnnualEmissions[r,e,y] = ModelPeriodEmissions[r,e]- ModelPeriodExogenousEmission[r,e];

def E8_AnnualEmissionsLimit_rule(model, r,e,y):
    result1 = model.AnnualEmissions[r, e, y] + model.AnnualExogenousEmission[r, e, y]
    result2 = model.AnnualEmissionLimit[r, e, y]
    return result1 <= result2
# AnnualEmissions[r,e,y]+AnnualExogenousEmission[r,e,y] <= AnnualEmissionLimit[r,e,y];

def E9_ModelPeriodEmissionsLimit_rule(model, r,e):
    result1 = model.ModelPeriodEmissions[r, e]
    result2 = model.ModelPeriodEmissionLimit[r, e]
    return result1 <= result2
# ModelPeriodEmissions[r,e] <= ModelPeriodEmissionLimit[r,e];
'''
 05-Oct-2022 meeting with Cristiano: Constraint.Feasible & Constraint.Infeasible were used for 1-item constraint blocks that the solver seemed to 
 struggle to process ("error with code"), even though there was no coding error. The workaround is to force feed the solver feasibility / infeasibility
 in these cases using Constraint.Feasible et al. For SC5_MaxCharge_rule, it is not 1-item constraint block as there will be multiple timeslices, 
 regions, technologies, seasons, daytypes, years, etc.
 '''