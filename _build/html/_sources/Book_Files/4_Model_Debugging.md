# 4 Model Debugging

# 4.1 Motivation: how to debug linear programs

When dealing with linear programs we will almost always be looking into optimization problems (maximization and minimization). Solutions to these types of problems will conventionally follow the [simplex method](https://mathworld.wolfram.com/SimplexMethod.html), first described by american mathematician George Dantzig in 1947, which consists of an algebraic procedure with underlying geometric concepts that describe and solve linear problems by simplifying them to their corner-point feasible soltions (CPF solutions). This problem description allow us to solve simple problems by hand and relies on sofisticated software packages, capable of applying the method to more complex scenarios (higher geometric dimensions)

Beyound the simplex method which is the standard choice of commercial solvers, the software engineer needs different tools to help diagnose potential problems in the solution, or sources of infeasibility to the program. Linear programming theory hints to an useful tool that can be viewed as a verification method for the original problem solution, the [dual problem](https://mathworld.wolfram.com/DualityTheorem.html). "The constraint values of the primal problem are related to the variables of the dual problem. These variables are known as shadow prices" [1]. Furthermore, the strong duality theorem states that the value of the objective function is equal between the primal and the dual and can be used to get the shadow proces of constraints from the primal. The shadow price (or slack value) of a constraint is, according to the strong duality theorem, the variation to the objective function value when the right-hand side of that constraint is increased by the unit value [1].

# 4.2 Tools for debugging

## 4.2.1 Problem LP formulation


Linear problem definitions are often written as an optimization problem of the form:

```
minimize F(x,y) 

Subject to:

C1(x,y) <= a

C2(x,y) <= b

C3(x,y) <= c
```

where F(x,y) is the objective function, a, b and c are constants and C1(x,y), C2(x,y) and C3(x,y) are constraint functions. In programming, an LP formulation (linear program formulation) is a file of the format `.lp` that is written in a naturally algebraic formulation that can be interpreted by the linear solver (CPLEX, for example) and then solved. For more information on LP files and how they are created and used by CPLEX, read more [here](http://lpsolve.sourceforge.net/5.0/CPLEX-format.htm). An exampole LP file is shown below

```

\* Problem:example_lp_problem: Windor Glass co. [2] *\

min

F_x_y: 3 x + 5 y + const

s.t

C1_x_y: x <= 4

C2_x_y: 2 y <= 12

C3_x_y: 3 x + 2 y <= 18

C_const: const = 1.0

bounds

0 <= x <= +inf

0 <= y <= +inf

end
```

The `const` and the `C_const` terms are the constant term and its governing constraint, respectively. Linear solvers will usually add the `const` term to the lp formulation in order to minimize computation time and prevent over-using the computional capabilities of the machine it is running on, so when talking about linear problem formulations, this constant term is not normally present, but for software formulations it is an important addition.

Although a LP file is a way to write a linear program formulation and pass it to the solver to get a solution, we can also retrieve this information from the solver and use it for debugging purposes. In MathProg we can get this file from GLPK by adding the command `--wlp my_lp_file.lp` when prompting GLPK to solve the model from the command line. This command will output the lp formulation of the model into the `my_lp_file.lp` file in a similar syntax to the example above.

To get the LP file from a Pyomo model, we can prompt Python to write the file from inside the script. This can be done in the following way: 

```
filename = os.path.join(my_path, 'Log-files/pyomo_model.lp')
instance.write(filename, io_options={'symbolic_solver_labels': True})
```

The lines above will make use of the `os` Python library to write the LP formulation into the `pyomo_model.lp` file. First the empty file is created and assigned to the variable `filename`, then the model instance is written into the file by Pyomo using `instance.write()`.

## 4.2.2 Extracting model components

In the last section we explored linear program formulations and how to create files that contain the algebraic description of linear problems. We have seen that these files can be given to linear solvers, such as GLPK and solved by these solvers in the same way as a Pyomo or a MathProg model file; further we have discussed how we can ask for this file from the solver either through the command line, or from the Python script using Pyomo in combination with Python libraries for operating system manipulation.

We will now discuss and explore Pyomo functionalities that can help on the debugging process. Pyomo can be used to print other bits of model information into separate files and increase the number of available resources for debugging.

### 4.2.2.1 Printing the model

Pyomo provides us with utility functions to help us assess the state of our model. Some of these utilities can have the model output to the screen with variable, set and parameter values.

In order to output the model information to the screen, or to a separate file, we can use one of the following approaches in code:

1. Use the `display` method: `model.display()` / `instance.display()`

2. Use the `pprint()` method:  `model.pprint()` / `instance.pprint()`

The main difference between the `display()` and the `pprint()` methods is that `display()` serves as a helper function to display a quick summary of the model components, such as the number of variables and constraints in the model and the values of each component with their domains (if applicable) component size (greater than 1 if we have a vector component, for example); `pprint()` on the other hand will display all the available information from the model, or from a specific component if appended to that component (`my_parameter.pprint()`, for example prints the information from `my_´parameter` only).

A typical output from the `display()` method would look like this:

```

>>> model.disply()

Model name

Variables:

    Variable x : Size=1 Domain=Reals

    Value=1.0

    Variable y : Size=1 Domain=Reals

    Value=3.0

Objectives:

    Objective o : Size=1

    Value=4.0

Constraints:

    None
```


### 4.2.2.2 Printing variable values

In the same way we can print a model summary using the `pprint()` and `display()` methods, we can extract variable values and additional information by employing the `pprint()` method. There are two main ways to extract information from variables and output them to the screen, or to a file:

1.  Extracting from a single variable: `model.variavble_x.pprint()`

2. Extracting from all model variables: 

```
variable_log = open("./Log-files/Variables.log", "w")
for v in instance.component_data_objects(Var):
    print(str(v), v.value, file=variable_log)
```

In the second example we see that we can output information from model components into separate files by assigning the file path to a python variable, `variable_log`, and put it inside the `print()` statement together with the `value` method from Pyomo.

### 4.2.2.3 Print selected results

Another useful tool that has been developed for use in this project is the **Selected Results** file. This file contains some outputs from the model that can help us catch discrepancies between different implemntations of the same problem (like Pyomo versus MathProg, for example), or verify that the order of magnitude of the results is as expected. The access to such file can greatly decrease debugging time, allowing the programmer to rapidly identify the issue to be tackled.

To create this file, simply select what results you would wish to see and have them be printed out to a separate file. Some functions and components of the model that you might wish to check are:

* The model's objective function

* The problem bounding constraints: these are the constraints that constitute the solution space oof the model. A small change to these constraints will have a noticible impact to your objective function's output

* The model summary from your solver of choice

* Any constraint you suspect is causing issues to the expected result

# 4.3 Taking advantage of solver information

We have previously eluded to the possibility of utilizing solvers to extract additional information about the problem and the solution process, such as LP formulation, duals and slack values. In this section let us look into how we can use solvers and Pyomo to interact with solvers in order to obtain such information.

## 4.3.1 CPLEX files

The IBM CPLEX solver comes with its own [optimization studio](https://www.ibm.com/products/ilog-cplex-optimization-studio) upon installation which allows the programmer to explore the optimization model using an intuitive GUI and obtain extra information about the problem's solution. It is possible, however to access the same information by navigating CPLEX through the command line to create the relevant files we wish to study.

To run CPLEX from your command line, simply navigate to your model's folder on the command line and call CPLEX: 

```
cd my_model_path
cplex
```
After running the `cplex` command you should be greeted with the optimization studio's welcome message indicating you are now inside the solver.

In order to access the suplemental files that CPLEX cabn provide, we will first need to have the LP formulation of our problem in a `.lp` file. Then we want to have CPLEX read that problem foormulation by running thr following command: `CPLEX> read my_Problem.lp`

CPLEX will output the time spent by the solver to read that problem, which should now be loaded into the solver's memory. We can now proceed to have CPLEX produce any files we may wish. The main files we would look into and that CPLEX can produce are:

* Duals file (DUA): contains values from the problem's dual

* Solutions file (SOL): contains information about the problem's primal's solution

* Conflicting constraints file (CLP): contains information about conflicting constraints and their bounds

CPLEX allows the user to navigate in a step-by-step manner, guiding them to write the correct file each time. With the problem's LP already on the solver's memory, the process for writing any of the cited files is:

```
write my_file_name
>>> File type options:
alp          LP format problem with generic names and bound annotations
ann          Model annotations
bas          INSERT format basis file
clp          Conflict file
dpe          Binary format for dual-perturbed problem
dua          MPS format of explicit dual of problem
emb          MPS format of (embedded) network
flt          Solution pool filters
lp           LP format problem file
min          DIMACS min-cost network-flow format of (embedded) network
mps          MPS format problem file
mst          MIP start file
net          CPLEX network format of (embedded) network
ord          Integer priority order file
ppe          Binary format for primal-perturbed problem
pre          Binary format for presolved problem
prm          Non-default parameter settings
rlp          LP format problem with generic names
rew          MPS format problem with generic names
sav          Binary matrix and basis file
sol          Solution file
``` 

After getting the file type optins from CPLEX, simply select the option you want. The new file should be created in your working directory from the command line and it will comply with CPLEX's syntax for that [file format](https://www.ibm.com/docs/en/icos/20.1.0?topic=cplex-other-file-formats).

## 4.3.2 Pyomo suffixes

A suffix is solver functionality for declaring extra model data, typically in the form of solution information [4]. Pyomo allows the programmer to have access to this information through the `Suffix` component class.

As we have seen in chapter 2 of this tutorial series, Pyomo borrows many of its concepts and syntax from AMPL, suffixes are no different in this matter, as the functionality is adapted from AMPL's implementation of it as well. 

In its essence, a suffix is allowing a two-way communication between the model and the solver as the model is being solved. This way, we are able to:

* Import extra information about model solutions into Pyomo (such as duals and slack values, for example)

* Export extra information to a solver to aid in model solution (such as variable branching priority information, for example)

* Advanced component manipulation for later use in other algorithms [4].

Since suffixes allow us to communicate with the solver by both giving and extracting information from it, we need to know how to implement this functionality inside Python. To do so, we need to pass to the Suffix class a communication **direction** and, if we wish, a **datatype** to be carried through this communication process.

From Pyomo's documentation we will see the following directions and datatypes to be used by the suffixes:

1. Direction:

* `LOCAL` - suffix data stays local to the modeling framework and will not be imported or exported by a solver plugin (default)
    
* `IMPORT` - suffix data will be imported from the solver by its respective solver plugin

* `EXPORT` - suffix data will be exported to a solver by its respective solver plugin

* `IMPORT_EXPORT` - suffix data flows in both directions between the model and the solver or algorithm
 
2. Datatype:

* `FLOAT` - the suffix stores floating point data (default)

* `INT` - the suffix stores integer data

* `None` - the suffix stores any type of data

A typical suffix declaration can look as any of the following:

```
# Export integer data
model.priority = pyo.Suffix(direction=pyo.Suffix.EXPORT, datatype=pyo.Suffix.INT)

# Export and import floating point data
model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)

# Store floating point data
model.junk = pyo.Suffix()
```

From the code snippet above, we see that Pyomo can use the `Suffix` functionality to give us model duals, information about model integer and float variables, as well as floating point values for later use in debugging, or other applications. 

When working with `Abstract Models` in Pyomo, we can also create suffixes in a similar way to that of creating `Constraints`, with a component `rule` to work with variables, for example [4]: 

```
def foo_rule(m):
    return ((model.x[i], 3.0*i) for i in model.I)
model.foo = pyo.Suffix(rule=foo_rule)
-----------------------------------------------------------------------------------
>>> # instantiate the model
>>> inst = model.create_instance()
>>> for i in inst.I:
...     print((i, inst.foo[inst.x[i]]))
(1, 3.0)
(2, 6.0)
(3, 9.0)
(4, 12.0)
```
## 4.3.3 Pyomo slack values

As we have seen, it is possible to extract, amoung other things, information about the dual problem of the model using Pyomo suffixes. More than knowledge about duals, we might wish to know more about specific model components to help us debug the algorithm. A useful part of a model that can be used to debug the script and give the programmer further insight into the solution space of the program are the so called constraint **shadow prices**, or **slack values**.

Luckly, Pyomo stores these slack values for every model constraint, after the model is constructed, inside the `component_objects()` method of the model instance. Using this method we can directly access the components of our model (Sets, Parameters, Variables, Constranits and Objective Function). In order to get the slack values from our model constraints, we will simply specify `Constraint` as our component of interest to the method and then iterate through each constraint to extract the value. This is illustrated by the following code excerpt:

```
for c in instance.component_objects(Constraint, active=True):
    for index in c:
        print(c[index], " || ", c[index].lslack(), " || ", c[index].uslack(), file=dual_logfile)
```

# 4.4 Interpreting model duals for debugging

We have seen how to extract information about model duals using a solver like CPLEX to generate a duals file for us. Now let us explore how to take advantage of these files to help us in debugging our models so we can achieve the result we expect and get a better insight into our linear program formulation.

In the case of our project with OSeMOSYS, we had an original implementation in Mathprog that we wished to recreate using Pyomo, so we knew what the goal value for the model's objective function was, effectively making the dual program files a short cut into understanding how the new Pyomo model was behaving. 

With access to the dual files it is possble to simply compare them and see if any values differ, if so, indicating an implementation problem occuring under that constraint, or variable. Differet values for the objective function indicate an evident implementation problem, but how different they are will indicate how loose, or how strict the solution space is. The dual files will then indicate, together with the slack values which constraints exactly are shifting the model's solution space away fromthe expected objective value result. 
 
# 4.5 References

[1] [J.M. Garrido; Sensitivity - CS4491 Introduction to Computational Models in Python; Kennesaw State University; 2015](http://ksuweb.kennesaw.edu/~jgarrido/CS4491_notes/Sensitivity_rep.pdf)

[2] [F.S. Hillier, G.J. Lieberman; Introduction to Operations Research; 9th ed.; Chapter 4: Solving Linear Programming Problems: The Simplex Method](https://archive.org/details/introductiontoop0000hill_g8z1)

[3] [Working with Pyomo Models](https://pyomo.readthedocs.io/en/stable/working_models.html)

[4] [Pyomo Suffixes](https://pyomo.readthedocs.io/en/stable/pyomo_modeling_components/Suffixes.html)

[5] [Production Model Sensitivity Analysis](https://jckantor.github.io/ND-Pyomo-Cookbook/02.02-Production-Model-Sensitivity-Analysis.html)

[6] [Pyomo Cookbook](https://jckantor.github.io/ND-Pyomo-Cookbook/)
