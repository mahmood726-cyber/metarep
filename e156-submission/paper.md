Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

MetaRep: Most Significant Cochrane Meta-Analyses Predict Only 32% Replication Probability When Heterogeneity Is Accounted For

What is the probability that a new clinical trial will replicate a significant Cochrane meta-analysis conclusion when between-study heterogeneity is properly accounted for? We analysed 398 Cochrane meta-analyses from the Pairwise70 dataset using restricted maximum likelihood estimation, focusing on 183 reviews with statistically significant pooled effects. MetaRep computes replication probability from the predictive distribution of a new study, incorporating both sampling error and between-study variance tau-squared into a single heterogeneity-aware power formula. Among significant meta-analyses, the median replication probability was 31.8 percent (IQR 16.0 to 63.6 percent), with 65.6 percent having replication probability below 50 percent. The primary driver was between-study heterogeneity rather than inadequate sample size, with median I-squared of 26.1 percent. Even meta-analyses deemed definitive by conventional standards predict roughly a one-in-three chance that the next appropriately sized trial will produce a significant confirmatory result. These estimates may not generalise beyond Cochrane reviews and are limited by the assumption of normally distributed between-study heterogeneity.

Outside Notes

Type: methods
Primary estimand: Replication probability (heterogeneity-aware predictive power)
App: MetaRep v1.0
Data: Pairwise70 dataset: 398 Cochrane reviews, 183 with significant effects
Code: https://github.com/mahmood726-cyber/metarep
Version: 1.0
Certainty: moderate
Validation: DRAFT

References

1. Valentine JC, Pigott TD, Rothstein HR. How many studies do you need? A primer on statistical power for meta-analysis. J Educ Behav Stat. 2010;35(2):215-247.
2. Jackson D, Turner R. Power analysis for random-effects meta-analysis. Res Synth Methods. 2017;8(3):290-302.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
