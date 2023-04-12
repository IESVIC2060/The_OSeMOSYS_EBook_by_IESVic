# 3 The OSeMOSYS Model in Pyomo

# 3.1 Motivation: why model the energy system of British Columbia?

Remember in chapter 1 of this Wiki we said that energy system modelling is an important step for the economical and social development of different regions of the world. This concept is, terefore, applicable to Canada's province of British Columbia.

British Columbia is home to over 232,000 [indigenous people](https://www2.gov.bc.ca/gov/content/governments/indigenous-people), of which 67% are first nations, living on- and off-reserves. Furthermore, BC is home to over 470 [dairy farms](https://bcdairy.ca/dairy-farming-in-bc/) that sustain 12,500+ jobs in the province. These localized communities are, ultematelly, the major beneficients of a careful and thoughtful plan that leads BC towards the future of energy production and distribution.

The modelling process for an energy system as complex as British Columbia's can help us understand the needs of the different regions of the province and how, for example, climate change can effect the energy consumption throughout the province in contrast with how the energy industry is able to supply that energy. Capacity expansion planning of the enrgy systems of BC can mitigate the impacts of climate change, while leading the way towards a renewable energy matrix in the province and the modelling process lies at the heart of this endevour.


# 3.2 Basics of the model: sets, parameters, variables and lp formulation

As we discussed in chapter 2 of this wiki, the core of the modelling process for energy systems lies in mathematically describing the problem at hand and, to achieve this, we resort to linear programming. As the ccentral topic in optimization engineering and operations research, linear programming translates mathematical formulations into computer programs.

A linear program for our energy model, for example, is described mathematically as a series of constraints, one (or more) objective, and a series of decision variables indexed by sets and accompained by the model parameters that, as discussed in the previous chapter, together for the model equations. Typically, a linear program formulation will be written in the way described in chapter 2: an objective function is to be maximized, or minimized, under a series of constraints, while the decision variables obey their limiting sets.

A more detailed explanation on LP formulations is given in section 4.2.1 in chapter 4 of this wiki. What follows is a series of example lp formulations for our OSeMOSYS model and their equivalent representation in Pyomo. Bare in mind that the full description of the OSeMOSYS model is a combination of descriptions for the objective function, its constraints and the variable bounds for the problem. With these examples we hope to help you get more familiar with the OSeMOSYS model by giving a mathematical description of what you see in code to shorten the gap between theory and practice.

> minimize: OSeMOSYS Objective Function

> subject to:

>(...)

> EBb4 Energy Balance Each Year: 

![](https://github.com/IESVIC2060/Storage-Master/blob/Working_Branch/Wiki/Images/EBb4%20lp.jpg)

> Pyomo: 

```
def EBb4_EnergyBalanceEachYear4_rule(model, r, f, y):
    result1 = sum(
        model.RateOfActivity[r,l,t,m,y] * model.OutputActivityRatio[r,t,f,m,y] * 
        model.YearSplit[l,y] 
        
        for m in model.MODE_OF_OPERATION 
        for t in model.TECHNOLOGY 
        for l in model.TIMESLICE 
        if model.OutputActivityRatio[r,t,f,m,y] != 0
    )
    
    result2 = sum(
        model.RateOfActivity[r, l, t, m, y] * 
        model.InputActivityRatio[r, t, f, m, y] * 
        model.YearSplit[l, y] 
        
        for m in model.MODE_OF_OPERATION 
        for t in model.TECHNOLOGY 
        for l in model.TIMESLICE 
        if model.InputActivityRatio[r, t, f, m, y] != 0
    ) + sum(
        model.Trade[r,rr,l,f,y] * model.TradeRoute[r,rr,f,y] 
        
        for l in model.TIMESLICE 
        for rr in model.REGION
    ) + model.AccumulatedAnnualDemand[r,f,y]

    return result1 >= result2
```
> (...)

> Nonstorage Constraint:

![](https://github.com/IESVIC2060/Storage-Master/blob/Working_Branch/Wiki/Images/NonStorageConstraint%20lp.jpg)

> Pyomo:

```
def NonStorageConstraint_rule(model,r,l,t,m,y): 
    if sum(model.TechnologyStorage[r,t,s,m] for s in model.STORAGE) == 0:
        return model.RateOfActivity[r,l,t,m,y] >= 0
    else:
        return Constraint.Skip
```

> (...)

> SC2 Upper Limit:

![](https://github.com/IESVIC2060/Storage-Master/blob/Working_Branch/Wiki/Images/SC2%20Upper%20Limit%20lp.jpg)

> Pyomo:

```
def SC2_UpperLimit_rule(model, r, s, l, y):
    result = sum(
        model.NewStorageCapacity[r,s,yy] + model.ResidualStorageCapacity[r,s,y] 
        for yy in model.YEAR 
        if y-yy <= model.OperationalLifeStorage[r,s] and y - yy >= 0
    )
    
    return model.StorageLevelTSStart[r,s,l,y] <= result 
```

Note that in the images, the constraints and variable bounds / set indices are separated by the dashed line.

# 3.3 Model translation from GNU MathProg to Pyomo

As we have previously mentioned in this wiki, OSeMOSYS supports three main implementations for its energy models: GNU MathProg, Python, GAMS. The approaches in these languages, mainly MathProg and Pyomo, are similar, in that they seek to divide the system into its separate components (sets and parameters) and establish an objective to be obtained under defined constraints.

The key differences in constructing an energy model using MathProg and Python (Pyomo) are presented in the following table:

|Language Capability |Pyomo  | GNU MathProg|
--- | --- | ---|
|Mathematically represents model components (sets, parameters, constraints, objective and variables)|Yes|Yes|
|Supports real world data as input to mathematical model|Yes|Yes|
|Has access to programming libraries for data processing and performing complex mathematical operations|Yes|No|
|Can hold model data within model file|Yes|Yes|
|Capable of evoking a linear solver from within the model file|Yes|No|

As we can see, the appeal for Pyomo resides in its extra capabilities over MathProg, especially in the data magement, data processing and reusability aspects. Additionally, as seen in Chapter 2 of this wiki, Pyomo allows you to create abstract models, which can receive data after the model has been created, a functionallity that is not available in MathProg.

The recommended approach to translate a model from MathProg to Pyomo is to copy the code from MathProg to a Python script in sections (building blocks), that is, first translate the model sets, parameters, and variables, then the model functions (objective and constraints). This will allow the programmer to concentrate in the differences in syntax between both languages and verify that the section of code has been correctly interpreted by Pyomo. Furthermore, this can facilitate the debugging step of the implementation, since Pyomo also offers debugging capabilities from within the script, such as access to model duals and slack values, which could be applied to the different parts of the code, then to the final version of the entire model for redundance. 

After migrating a model from MathProg to Pyomo, one can easily verify the implementation is correct by running both programs through the same solver, GLPK, or CPLEX, for example, and compare the results. If the mathematical formulation (LP format) is preserved between implementations and the outputs are within a small marginal difference, then the Pyomo (translated) model will have been fully and correctly created. Here, we see two example model formulations, in MathProg and in Pyomo.

```
# MATHPROG IMPLEMENTATION:
# A TRANSPORTATION PROBLEM
#
# This problem finds a least cost shipping schedule that meets
# requirements at markets and supplies at factories.
#
# References:
# Dantzig G B, "Linear Programming and Extensions."
# Princeton University Press, Princeton, New Jersey, 1963,
# Chapter 3-3.

set I;
/* canning plants */
set J;
/* markets */
param a{i in I};
/* capacity of plant i in cases */
param b{j in J};
/* demand at market j in cases */
param d{i in I, j in J};
/* distance in thousands of miles */
param f;
/* freight in dollars per case per thousand miles */
param c{i in I, j in J} := f * d[i,j] / 1000;
/* transport cost in thousands of dollars per case */
var x{i in I, j in J} >= 0;
/* shipment quantities in cases */
minimize cost: sum{i in I, j in J} c[i,j] * x[i,j];
/* total transportation costs in thousands of dollars */
s.t. supply{i in I}: sum{j in J} x[i,j] <= a[i];
/* observe supply limit at plant i */
s.t. demand{j in J}: sum{i in I} x[i,j] >= b[j];
/* satisfy demand at market j */
```

```
# PYOMO IMPLEMENTATION
from __future__ import division
from pyomo.environ import *
from pyomo.core import *
from pyomo.opt import SolverFactory

model = AbstractModel(name="Example") # Example model

# Model sets
model.I = Set() # Canning plants
model.J = Set() # Markets

# Model Parameters
model.a = Param(model.I) # Capacity of each plant
model.b = Param(model.J) # Market demands
model.d = Param(model.I, model.J) # Distance in thousand of miles
model.f = Param() # Freight in dollars per case per thousand miles
model.c = Param(model.I, model.J, initialize= model.f * model.d / 1000) # Transport
cost in thousands of dollars

# Model Variables
model.x = Var(model.I, model.J, bounds=(0, None)) # Shipment quantities in cases

# Objective Function
def Objective_cost(model):
return sum(model.c[i,j] * model.x[i,j] for i in model.I for j in model.J)
model.Cost = Objective(rule= Objective_cost, sense=minimize) # Total cost

# Model Constraints
def Supply_const(model, i):
result1 = sum(model.x[i,j] for j in model.J)
return result1 <= model.a[i]

model.supply = Constraint(model.I, rule=Supply_const) # Supply limits

def Demand_const(model, j):
result1 = sum(x[i,j] for i in model.I)
return result1 >= model.b[j]

model.demand = Constraint(model.J, rule=Demand_const)

# Solving the model
instance = model.create_instance()

opt = SolverFactory('glpk') # Choose solver to be used

final_result = opt.solve(instance, tee=True)
```

# 3.4 How to run the model

The Pyomo model of OSeMOSYS can be run from within a Python IDE of your choice, such as [Visual Studio Code](https://code.visualstudio.com/), [PyCharm](https://www.jetbrains.com/pycharm/), or the  [Spyder IDE](https://www.spyder-ide.org/), but it can also run directly from the command line when you have Anaconda added to your path variables and an [environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) in which you installed Pyomo.

If running the model from within an IDE, the portion of the main code, `pyomo-osemosys.py`, labeled `# Solver` must be included (it is commented out by default). To include the solver into the main code, simply uncomment the portion of the code below the label (multi-line comments in Python are indicated by triple quotation marks). In this case, you have two main ways in which you can run the code: through an AMPL data file as an input parameter, or through data processing using Pandas dataframes.

To use an AMPL data file within the code, the model instance must be created from the data file of your choice in the following way: `instance = model.create_instance(my_data_file)`. This is the default approach adopted by the team for running the code within an IDE. The second approach is to use Pandas dataframes, which are created from Excel spreadsheets. For this approach to work as expected, uncomment the sections of the code labeled `# Dataframes` and `# Data processing`, as well as the `# Solver`, then remove the data file argument from the instance creation on the `# Splver` section.

In order to run the code from the command line (or terminal), follow these steps:

1. Activate the Anaconda environment where Pyomo is installed

2. Change the directory to where you have the main model file. If you cloned this repository, that will be the folder with the same name as this repository

3. Type the following command on your prompt: `pyomo solve --solver=my_solver pyomo-osemosys.py my_data_file.dat`, where:

* `my_solver` is the solver of your choice (GLPK, CPLEX, Gurobi, etc)

* `pyomo-osemosys.py` is the model file

* `my_data_file.dat` is the model data file (or path to the data file) in AMPL data format.

If solving the model with GLPK linear solver, the following arguments might be useful:

* `--summary`, displays a summary of the solution on screen

* `--wlp my_lp_file.lp`, writes the model problem in LP format to a separate file

# 3.5 References

1. [Agriculture in Canada - The Canadian Encyclopedia](https://www.thecanadianencyclopedia.ca/en/article/agriculture-in-canada)

2. [Energy Efficiency in British Columbia](https://www2.gov.bc.ca/gov/content/industry/electricity-alternative-energy/energy-efficiency-conservation)

3. [Energy Systems Modelling: Principles and Applications - H. Farzaneh](https://www.researchgate.net/publication/329905179_Energy_Systems_Modeling_Principles_and_Applications)

4. [First People's Map of British Columbia](https://maps.fpcc.ca/)

5. [Energy System Models - Science Drect](https://www.sciencedirect.com/topics/engineering/energy-system-models)

6. [Linear programming formulation examples - J. E. Beasley](http://people.brunel.ac.uk/~mastjjb/jeb/or/lpmore.html)
