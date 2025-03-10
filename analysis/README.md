## Analysis features
### Systematic uncertainties calculation
- Systematic uncertainty calculation on a given variable can be done via this python script:
```ruby
python systematic_studies.py configs/systematics/config_LHC24_pp_pass1.yml --do_systematics
```

### Pull plot plotting
- Plot the pull distribution below the invariant mass fit using the output of the fit library:
```ruby
python invariant_mass.py configs/inv_mass_plots/config_upsilon_PbPb.yml --do_pull_plot
```
