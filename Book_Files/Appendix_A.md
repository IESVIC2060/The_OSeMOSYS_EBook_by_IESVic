# Appendix A: A Brief Insight Into the AMPL Modeling Language

## A.1 What is AMPL?

AMPL is a programming language for mathematical programming. It was designed and implemented in 1985 by Robert Fourer, David M. Gay, and Brian W. Kernighan, who are the authors of the [AMPL book](https://ampl.com/resources/the-ampl-book/chapter-downloads/). A mathematical programming problem is an optimization problem tackled through an algorithmic manner, which is better described through mathematical terms that are interpreted by the computer through the use of languages such as AMPL.

The problems that require the employment of AMPL usually arise from the abstraction of a real world situation, for which a model is formulated, such that its whole can be broken apart into variables, sets, parameters, constraints and the objectives, or goals of the engineering team. These problems expect real world data, most often from past iterations of the problem, or from similar occurances in different scenarios, that is then incorporated into the model and passed down to a `solver`, which produces the relevant results. The results can then be analyzed to better inform the engineers on how to refine theproblem definition to achieve the desired outcome.


## A.2 AMPL and Pyomo

As we have seen in chapter 2, Pyomo provides the same capabilities as AMPL, as such, the data files used for Pyomo models are structured in the same format as for AMPL models. Now, we shall see how these data files are written so they can be properly interpreted by the solver.

## A.3 How to Write an AMPL data file

In linear programming and mathematical programming, in general, data is represented in matrix form. In AMPL data is also represented in this way.

In a similar fashion to a Pyomo script, when creating an AMPL data file the user should declare the model's sets and parameters prefaced by the command `set` and `param`, respectively. The difference between the Pyomo and the data files, however, is that in the data file, the sets and parameters are accompained by their respective values. After declaring a set, or a parameter, the data values are to be written in a matrix-like arrangement that is similar to how they would be written mathematically.

Typically, sets are one-dimensional vectors and parameters are multidimensional matrices, of the third, fourth, or even higher orders. Let us now see some examples of declaring sets and parameters in a data file and how they are interpreted by the solver.

### Example 1: set declarations:

When declaring a set in AMPL, it can assume many different form, but the central idea behind their purpose is the sam: __they will be used to index a model parameter__, that is, they are to be understood as labels for lines and columns of a parameter matrix that will later be constructed. 

![](../Images/AMPL%20Set%20Declaration%20Example.jpg)

![](../Images/AMPL%20Parameter%20Declaration%20Example.jpg)

One important keyword in AMPL data files is the `default` command, which specifies a default value to be used by the solver for missing data points inside a given parameter. These missing data points can be explicitly marked by a the "." character to be replaced by the default value once the model is created and solved.

![](../Images/AMPL%20Default%20Keyword%20Example.jpg)

### Example 2: multidimensional parameters:

When declaring parameters, it is important that the respective indexing sets are correctly declared within the model file (in Pyomo), but that is not necessary within data files, since the solver will deduce that any missing set will have the default value in its position. For multidimensional parameters (parameters indexed by more than one set), however, the sets must always be specified in order to construct a full matrix for that parameter. To declare a multidimensional parameter we use the square brackets ([*,*]) notation, as in the example below.

![](../Images/AMPL%20Multidimensional%20Parameter%20Declaration%20Example.jpg)

This same notation can be used for as many dimensions as the parameter requires and it follows the same pattern: `param B: = [fixed_index, *] variable_index value`, where the asterisk will represenst a variable set for that declaration, while the other values within the brackets are fixed indexes for that declaration; the values that follow the closing bracket will replace the asterisks, or will represent the value to be input into the matrix by the solver, if the variable sets for that iteration have already replaced the asterisks.

## A.4 References

1. [Mathematical Programming With AMPL | Brian Kernighan and Lex Fridman](https://www.youtube.com/watch?v=gGQBpTtsRVw&list=TLPQMTYwNTIwMjIoQEz8T5s7TA&)

2. [Initializing Abstract Models with Data Command Files - Pyomo](https://link.springer.com/chapter/10.1007/978-1-4614-3226-5_6)
