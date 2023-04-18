# IESVic Pyomo for OSeMOSYS:

from __future__ import division
from pyomo.environ import *
from pyomo.core import *

##################################################################################################################################################

def ObjectiveFunction_rule(instance):
#    return sum(instance.TotalDiscountedCost[r,y] for r in instance.REGION for y in instance.YEAR)
    return sum(instance.ModelPeriodCostByRegion[r] for r in instance.REGION)

# def ObjectiveFunction_rule(instance):
#     result1 = sum(
#         (
#             (
#                 (
#                     sum(instance.NewCapacity[r,t,yy]
#                     for yy in instance.YEAR if y - yy < instance.OperationalLife[r,t] 
#                     and y -yy >= 0)
#                     + instance.ResidualCapacity[r,t,y]
#                 )
#                 * instance.FixedCost[r,t,y] + sum(instance.RateOfActivity[r,l,t,m,y] 
#                 * instance.YearSplit[l,y] * instance.VariableCost[r,t,m,y]
#                 for m in instance.MODE_OF_OPERATION for l in instance.TIMESLICE)
#             )
#             / ((1 + instance.DiscountRate[r])**(y - min(instance.YEAR) + 0.5))
#             + instance.CapitalCost[r,t,y] * instance.NewCapacity[r,t,y] / 
#             ((1 + instance.DiscountRate[r])**(y - min(instance.YEAR)))
#             + instance.DiscountedTechnologyEmissionsPenalty[r,t,y] 
#             - instance.DiscountedSalvageValue[r,t,y]
#         )
#     for r in instance.REGION for t in instance.TECHNOLOGY for y in instance.YEAR)

#     result2 = sum(
#         instance.CapitalCostStorage[r,s,y] * instance.NewStorageCapacity[r,s,y]
#         / ((1 + instance.DiscountRate[r])**(y - min(instance.YEAR)))
#         - instance.SalvageValueStorage[r,s,y]
#         / ((1 + instance.DiscountRate[r])**(max(instance.YEAR) - min(instance.YEAR) + 1))
#     for r in instance.REGION for s in instance.STORAGE for y in instance.YEAR)

#     return result1 + result2
