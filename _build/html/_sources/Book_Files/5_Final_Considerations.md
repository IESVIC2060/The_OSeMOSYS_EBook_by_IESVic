# 5 Final Considerations and Laying the Way Forward

# 5.1 Conclusions

This wiki summarizes the work developed at the Institute for Integrated Energy Systems at the University of Victoria to build an energy model for the province of British Columbia using the Python scripting language and the Pyomo software package for optimizatiion. In a series of 4 chapters we have walked through the purpose of the project, the reasoning behind the choice of Pyomo over MathProg for creating energy models and described the model implementation. Further we have explored a few tools that can help programmers and engineers debug their optimization models, by taking full advantage of Pyomo's powerful functionalities in conjunction with any available solver, from free software (such as GLPK) to industry leading solvers like CPLEX.

# 5.2 Recommendations

OSeMOSYS models will usually be robust, which increases running time for the solvers, and can make the debugging process take even more time. Debugging, in fact was the most time consuming component of this project.

To reduce debugging time and increase the chances of your model working in its initial tests, we recommend a modularization of the program to be carried-out. This process is as simple as dividing the model into its subcomponents (sets, parameters, variables, objectives and constraints) and creating separate files for handling different aspects of the model (objective implementation, constraints implementation, data processing, etc.). This modular approach was incorporated into our model at the end, so you can look at this repository's code to see how we went about modularizing our model. 

# 5.3 Further studying resources

[1] [Model-based Optimization: Principles and Trends - AMPL](https://ampl.com/MEETINGS/TALKS/2018_08_Lille_Tutorial1.pdf)

[2] [Tutorial for Operations Research: Modelling in GNU MathProg](https://dtk.tankonyvtar.hu/xmlui/bitstream/handle/123456789/13112/tutorial_for_operations.pdf?sequence=1&isAllowed=y)

[3] [Energy, Poverty and Development](https://iiasa.ac.at/web/home/research/Flagship-Projects/Global-Energy-Assessment/GEA_Chapter2_development_hires.pdf)

[4] [The World’s Energy Problem]( https://ourworldindata.org/worlds-energy-problem)

[5] [GNU Linear Programming Kit, Part 1: Introduction to Linear Optimization: ](http://www.osemosys.org/uploads/1/8/5/0/18504136/ceron_-_2006_-_the_gnu_linear_programming_kit_part_1_-_introduction_to_linear_optimization.pdf)

[6] [Modelling Elements of Smart Grids – Enhancing the OSeMOSYS (Open Source Energy Modelling System) Code](https://pdf.sciencedirectassets.com/271090/1-s2.0-S0360544212X00100/1-s2.0-S0360544212006299/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEP7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJGMEQCIEHHW7w685OCY%2B%2FBmj6KOtarX4uWE4AtVOw%2FASct3PACAiAOdNRKUwERN0hM0fhO8oRYPNnVUySvNJJYzpGqi1HJdCqDBAjX%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAQaDDA1OTAwMzU0Njg2NSIMAoGX%2FBtIuxSNEIBXKtcD4AoEqM8zdLNJmOz%2FJ2Pa074AnEwn3HxSz1LPvYyk4rxK6NUZAPTEfesy17Do%2BVy8HdaLVGJw6Y%2FEvI78GIsNx7Qw%2F5Siye7Itj9iw6ZpSeVXUuNV6AKyeFtgIZgoQaevcyIk%2BJfJPlED2O8eF4bjZJHndLeZMSpt8OJe1UQgPJ1%2F%2B%2BFQKm%2BqKVLPP4ol3PY%2F2zqOQ3nUUG4jnoxpIkTSsfresDrTilPdxeZefPsXgLYmxX2SzyTbe1M5ugCc54muM9R%2FZ413s4Em7qKlscCP%2BtARGAl4MGlr0pz2lZcQR91vF2KC022uY8IqxgfLvJSP5KmUFxct3U4xuuxvc24MaKk9kdjxZDoGX7J4aB2za4EVdIgjxH9E4Cx%2BEAiYXkO%2BlyHXHN4gS2Ps%2Fjy1ghLEW616fB1ZFZdRzWieLt8AMDsDOAahzujTLKjmgu%2BayfxN5V6H3TGx4%2F5sdcdt40P8uIb%2Bhmdoc7N%2FfmShgv%2FxM3X8MmHvFUnZZKcJ3iE1fKa9CJiF0HMxVi7sMRPyAP0ZXw6G18l1muaWI2DIMIm7EARECy2GwgYw0zx6xj1JjYRkTqYynvKHPkIPMYKs3IdNR7gdD4UCpd0MmT1g5iL4lAYIrle34SxoMKSOyI0GOqYBqzAJCmezK9MSZPw9kT%2BVwpA%2F6bOqXCc8w7WHCziRgehFZqN1oTTVAtG%2F68Y3Kzz7T6d%2B2wtAh5xQa%2BobfJhNxrY7BA0vvySIm%2FJfTdVx5i%2BLtrMXYU0A3ftzygUaWgtbiv9Y9w2NAEuzEOcuAvcEIbVulpeOk8kRqaoymOOs2LWq5pgk0gTLOJv%2FZ6br4e1gKhvEL4HtBoLWApw%2FQ%2BLTc85JGdZrXA%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20211209T144141Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYRKINSYHI%2F20211209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=0c8733a76e7f206ab9fdac65039196969b267e4c1b5405bf9c02be3051f342eb&hash=fc07cbf85d1aae6b022f1e0322025f36ea6a600055aed84d8f11e93f7a3c8cf2&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0360544212006299&tid=spdf-517e9359-0e65-498b-9f88-96d493ea12eb&sid=620708ee2d609842f359c1558c01a7e84c9egxrqa&type=client)

[7] [OSeMOSYS: The Open Source Energy Modeling System An introduction to its ethos, structure and development](https://pdf.sciencedirectassets.com/271097/1-s2.0-S0301421510X00167/1-s2.0-S0301421511004897/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEP7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSJIMEYCIQCGGjmlVJRRoDGzg3f9%2B9q1PqiCSwVFOwsgUQmI39EZXwIhAOG3BBvpewgT6dhYVo5C6VO9YwlkN1ooBcddunMtWBx3KoMECNf%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQBBoMMDU5MDAzNTQ2ODY1Igy69%2F2yY6m49tug%2BVUq1wN3bOY4LYHx7kknzYLzpz6TNPk%2BTXo5fVp1jI8jJ1OJz%2B3qHMHxR2rL1iEDDNxnuZTjHwgflAi1kwgFDe%2B3lawNTx0gzCMok35M32SVR5mMXJpz%2BRoqPIFfxNYl5TZPlLBW4g9ZTLuxsVTF6NgV5vjumxvIYmX2TUAnKoZpBMjw1W86Wm%2BkPcee1otNbKx3aB3nZvMTnVgv9zOPWySQazx2Rx7R%2BNWJArJQgkPb4BbE7J6rOUkqSZlNKguweFoxiwRqbzg%2BUoX43F6wADmeNwgFtTDr%2BzDVro3Cg6urlX17jRuEExdJq91Z57zzSIClRSiVKV5srs%2FHDfB1w0G6IC29dOwbls4Gz1PKQ8o0Ipav01mAPwqbXwhXILIyT5WrSq1UOA40UL5ijunGBSskRsJ6EQipAFnq9aCXIYwp%2BVF4iboLVLjikqaue3nIafvhhKqfzxVQswHmWh%2FDAM2qhHtpIku6lNrEPfb3AM3g7yX8evkdvnCBUzP7I4SznBZ2FEjxs%2BUHcmMBfhmpvY3FTp2l5xRf%2F59EmPnvHJOAX%2FZ%2Bi0Xvp3ENlzP3BaDLVbJOaeNPYFjc5Otp85G88IjgC9Hva%2FEPp0CKrWHyzn811cbA%2BWkH8B6qG9Qwho%2FIjQY6pAHNcXNMBIwYHRm%2FSrwS8Z4VGXLgcZDTHp45A8JoFMAajjxZSkBGNw5jnK1Zi6aMC%2Bnp%2F7EElxh76IaPdT2%2F8Cih%2B3Pw2UAwrvI40VEoHKPaediRlDIEGndhzJQ5l7zxu0b5Jsk6bZ4Vjaf9ZwjaDPYDwiZCKhsZqUYPytunAaMCfo9pzm0uVYmQ0mCOjaChnXCWvmRUmOHEsFhN7HhGDrteaLr93Q%3D%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20211209T144215Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTY4OAYGPEA%2F20211209%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=931ec264c46bd922e7df68dee00ae2d885f4e6bbba55c62c370c64a99ea95700&hash=24a4e26858be80ad47b5725a7428cb7ec6c435b6997084afd7afa1532edfd3d1&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S0301421511004897&tid=spdf-88d89345-ecb8-41ea-8d7a-f0b18d4cb95d&sid=620708ee2d609842f359c1558c01a7e84c9egxrqa&type=client)

[8] [Pyomo Forum - Google Groups](https://groups.google.com/g/pyomo-forum)

[9] [OSeMOSYS Forum - Google Groups](https://groups.google.com/g/osemosys)

[10] [Energy Systems Modeling Book](https://link.springer.com/book/10.1007/978-981-13-6221-7)
