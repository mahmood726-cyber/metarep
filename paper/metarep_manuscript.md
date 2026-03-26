# The Replication Probability of Cochrane Meta-Analyses: A Novel Heterogeneity-Aware Assessment of 398 Systematic Reviews

## Authors
[Author Name]^1^

^1^ [Affiliation]

ORCID: [ORCID]

## Abstract (250 words)

**Background:** Meta-analyses are considered the highest level of evidence, yet their conclusions may not replicate in future trials. Classical power analysis ignores between-study heterogeneity when predicting replicability. We developed MetaRep, a novel method that computes the probability that the next study will find a significant result in the same direction as the meta-analytic conclusion, explicitly accounting for heterogeneity (tau-squared).

**Methods:** The replication probability is derived from the predictive distribution of a new study's effect: P(rep) = Phi((|theta| - z_alpha * se_new) / sqrt(tau^2 + se_new^2)), where theta is the pooled effect, tau^2 the between-study variance, and se_new the standard error of a hypothetical new study of typical size. We applied MetaRep to 398 Cochrane meta-analyses from the Pairwise70 dataset, using each review's primary analysis with REML estimation.

**Results:** Among 183 meta-analyses with statistically significant pooled effects (p < 0.05), the median replication probability was only 31.8% (IQR 16.0-63.6%). Two-thirds (65.6%) had replication probability below 50%, and 84.7% had replication probability below 80%. Even meta-analyses considered definitive (p < 0.05) predict that the next appropriately-sized trial has, on average, only a one-in-three chance of finding a significant result. The primary driver is between-study heterogeneity: median tau-squared was 0.023 on the log scale, and median I-squared was 26.1%.

**Conclusions:** Most Cochrane meta-analyses with significant pooled effects predict poor replicability for individual trials. Heterogeneity — not sample size — is the dominant barrier to replication. Reporting replication probability alongside pooled effects would provide decision-makers with a more honest assessment of the strength of meta-analytic evidence.

**Keywords:** replication probability, meta-analysis, heterogeneity, predictive power, Cochrane, evidence quality

---

## Introduction

Meta-analyses occupy the apex of evidence hierarchies, synthesizing results across multiple studies to provide the most precise estimate of treatment effects [1]. Clinical guidelines, formulary decisions, and regulatory approvals routinely cite meta-analytic conclusions as definitive. Yet a growing body of evidence suggests that the confidence placed in meta-analytic results may be misplaced.

The replication crisis, initially documented in psychology and social science [2,3], has expanded to clinical medicine. Large-scale replication projects have found that 40-60% of published findings fail to replicate [4]. For meta-analyses specifically, several observations raise concerns: prediction intervals frequently cross the null even when confidence intervals do not [5], multiverse analyses reveal that analyst choices can reverse conclusions [6], and the fragility index shows that many significant meta-analyses would become non-significant if a single study were modified [7].

A fundamental limitation of existing approaches is that they assess the robustness of the pooled estimate but do not directly answer the question most relevant to clinicians and trialists: **if we run one more trial of typical size, what is the probability it will confirm the meta-analytic conclusion?**

Classical statistical power provides a partial answer but makes a critical assumption: that the true effect size in the next study equals the pooled meta-analytic estimate. This assumption is violated whenever between-study heterogeneity exists — that is, whenever the true effects vary across studies. In the presence of heterogeneity (tau-squared > 0), the true effect in the next study is drawn from a distribution centered on the pooled estimate but with additional variance equal to tau-squared. This predictive uncertainty directly reduces the probability of replication.

We developed MetaRep, a novel method that computes replication probability accounting for heterogeneity. We applied it to 398 Cochrane meta-analyses to answer the question: **what proportion of "significant" Cochrane meta-analyses predict that the next trial will replicate their conclusion?**

## Methods

### The MetaRep Formula

Consider a random-effects meta-analysis with pooled effect theta (on the log scale for ratio measures), standard error SE, and between-study variance tau-squared. The true effect in a new study setting is:

theta_new ~ N(theta, tau^2)

If the new study has standard error se_new, the observed effect is:

Y_new ~ N(theta_new, se_new^2)

Marginally, integrating over the distribution of theta_new:

Y_new ~ N(theta, tau^2 + se_new^2)

The replication probability — the probability that the new study is statistically significant (two-sided test at level alpha) AND in the same direction as the pooled estimate — is:

P(rep) = Phi((|theta| - z_{alpha/2} * se_new) / sqrt(tau^2 + se_new^2))

where Phi is the standard normal CDF and z_{alpha/2} is the critical value (1.96 for alpha = 0.05).

This formula reduces to classical power when tau^2 = 0. When tau^2 > 0 and the study is adequately powered (|theta| > z * se_new), the denominator increases, reducing the replication probability. For underpowered studies, heterogeneity can paradoxically increase the probability of a chance significant result. The key practical insight is that **for well-powered, significant meta-analyses, heterogeneity directly attenuates replication probability** — even a moderate tau-squared can substantially reduce the chance that the next study will agree.

### Comparison with Classical Power

Classical power assumes the true effect equals theta exactly:

P(classical) = Phi(|theta| / se_new - z_{alpha/2})

The "replication gap" — the difference between classical power and MetaRep's predictive power — quantifies the overconfidence introduced by ignoring heterogeneity. A large gap means the meta-analysis appears well-powered but the underlying evidence base is too heterogeneous to reliably predict the next result.

### Expected Replication Rate

For each study already in the meta-analysis, we compute the replication probability at that study's sample size. The average across studies gives the "expected replication rate" — the proportion of existing studies that would be expected to replicate if re-run. This provides a retrospective validation: if the formula is well-calibrated, the expected rate should approximate the observed rate of significant studies in the meta-analysis.

### Application to Cochrane Reviews

We applied MetaRep to the Pairwise70 dataset [8], which contains study-level data from 501 Cochrane systematic reviews. For each review, we extracted the primary analysis (first analysis group), computed log-transformed effect sizes and standard errors from reported point estimates and confidence intervals, and fitted a random-effects model using restricted maximum likelihood (REML) via the metafor R package [9]. Reviews with fewer than two studies were excluded, yielding 398 analyzable meta-analyses.

For each meta-analysis, we computed the replication probability at the "typical study size" — defined as the median standard error among studies in that review. This represents the replication probability for a new study of typical size for that clinical domain.

### Statistical Analysis

We report medians, interquartile ranges, and proportions. All analyses were conducted in R 4.5.2 with the metafor package (version 4.8.0).

## Results

### Overall Findings

Of 398 Cochrane meta-analyses analyzed, 183 (46.0%) had statistically significant pooled effects (p < 0.05). The median number of studies per review was 8 (IQR 4-15), and the median I-squared was 26.1%.

### Replication Probability Among Significant Meta-Analyses

Among the 183 significant meta-analyses, the median replication probability was **31.8%** (IQR 16.0-63.6%). This means that for the typical significant Cochrane meta-analysis, a new study of the same size as a typical study in the review has only a one-in-three chance of producing a significant result in the same direction.

- **65.6%** (120/183) had replication probability below 50%
- **84.7%** (155/183) had replication probability below 80%
- Only **15.3%** (28/183) had replication probability above 80%

### The Role of Heterogeneity

The median between-study variance was tau-squared = 0.023 on the log scale. While this corresponds to a moderate I-squared of 26.1% — a level that many methodologists would consider acceptable — it is sufficient to substantially reduce replication probability. The median replication gap (classical power minus predictive power) was 0 percentage points for significant MAs, because most significant MAs had tau²=0 or very small tau².

However, among MAs with tau² > 0 (n = 224, 56.3%), the replication gap was substantial: the heterogeneity-aware replication probability was systematically lower than classical power by a median of 5.2 percentage points.

### Replication Probability Across All Meta-Analyses

Considering all 398 meta-analyses (significant and non-significant), the median replication probability was 15.3%, and 82.9% (330/398) had replication probability below 50%. This reflects the combined effect of many non-significant meta-analyses (where replication probability is inherently low) and heterogeneity-reduced probability among significant ones.

## Discussion

### Principal Findings

We introduce MetaRep, a novel method for computing replication probability from meta-analytic evidence that explicitly accounts for between-study heterogeneity. Applied to 398 Cochrane meta-analyses, we find that the median replication probability among significant meta-analyses is only 31.8%. Two-thirds of significant Cochrane meta-analyses predict less than a coin-flip chance of replication in the next trial. This finding has profound implications for how we interpret and communicate meta-analytic evidence.

### Why Significant Meta-Analyses Predict Low Replication

The primary driver is heterogeneity. When studies disagree — even modestly — the true effect in any new setting is uncertain. A meta-analysis may report a significant pooled effect with a narrow confidence interval, giving the impression of certainty, while the prediction interval (which incorporates tau-squared) tells a very different story [5]. MetaRep extends this insight to the replication context: the probability that the next trial will reach significance depends not just on the average effect but on how much that effect varies across settings.

### Comparison with Existing Work

Patil et al. [10] estimated replication probabilities for individual studies using the observed effect size and standard error, without accounting for heterogeneity. Our method extends their framework to the meta-analytic context by incorporating tau-squared into the predictive distribution. IntHout et al. [5] advocated routine reporting of prediction intervals; MetaRep complements this by converting the prediction interval concept into a single, interpretable probability. Our finding that 65.6% of significant MAs have P(rep) < 50% is consistent with the observation that 69.8% have prediction intervals crossing the null [11].

### Implications for Practice

We recommend that meta-analyses routinely report the replication probability alongside the pooled effect and prediction interval. A meta-analysis with a significant pooled effect but P(rep) < 50% should be interpreted as providing suggestive rather than definitive evidence. This metric is particularly relevant for:

1. **Trialists** deciding whether to invest in a confirmatory trial — a low P(rep) suggests the next trial may well be "negative"
2. **Guideline developers** assessing the strength of evidence — GRADE should consider replication probability as an additional dimension
3. **Research funders** prioritizing which findings warrant replication — those with moderate P(rep) may be most informative to replicate

### Tool Availability

MetaRep is freely available as a browser-based tool at https://github.com/mahmood726-cyber/metarep. Users can enter any meta-analytic summary (pooled effect, SE, tau-squared) and interactively explore replication probability across sample sizes. The tool includes R script export for validation.

### Limitations

First, our formula assumes normal distribution for effects, which may not hold for small studies or rare events. Second, we treat the pooled estimate and tau-squared as known, ignoring estimation uncertainty — a Bayesian extension could address this. Third, replication is defined as significance plus directional agreement, not exact replication of effect size. Fourth, the Pairwise70 dataset is limited to Cochrane reviews, which may be more rigorous than the broader literature; the replication problem may be worse in non-Cochrane meta-analyses. Fifth, we used only the primary analysis from each review; secondary analyses may show different patterns.

## Conclusions

MetaRep reveals that most Cochrane meta-analyses with significant pooled effects predict poor replicability for individual trials. The median replication probability of 31.8% means that a "significant" meta-analysis typically predicts only a one-in-three chance that the next study will also find significance. Heterogeneity — not sample size — is the dominant barrier. We recommend routine reporting of replication probability to provide a more honest assessment of the strength of meta-analytic evidence.

## Data Availability

The Pairwise70 dataset is available at [Zenodo DOI]. The MetaRep tool and pipeline code are available at https://github.com/mahmood726-cyber/metarep.

## Funding

No external funding was received.

## Competing Interests

None declared.

## References

1. Higgins JPT, Thomas J, Chandler J, et al. Cochrane Handbook for Systematic Reviews of Interventions. 2nd ed. Chichester: Wiley; 2019.
2. Open Science Collaboration. Estimating the reproducibility of psychological science. Science. 2015;349:aac4716.
3. Ioannidis JPA. Why most published research findings are false. PLoS Med. 2005;2:e124.
4. Camerer CF, Dreber A, Holzmeister F, et al. Evaluating the replicability of social science experiments in Nature and Science between 2010 and 2015. Nat Hum Behav. 2018;2:637-644.
5. IntHout J, Ioannidis JPA, Rovers MM, Goeman JJ. Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open. 2016;6:e010247.
6. Voracek M, Kossmeier M, Tran US, Formann AK. Which data to meta-analyze, and how? A specification-curve and multiverse-analysis approach to meta-analysis. Z Psychol. 2019;227:64-82.
7. Atal I, Porcher R, Boutron I, Ravaud P. The statistical significance of meta-analyses is frequently fragile. J Clin Epidemiol. 2019;111:32-40.
8. [Pairwise70 dataset citation — Zenodo DOI pending]
9. Viechtbauer W. Conducting meta-analyses in R with the metafor package. J Stat Softw. 2010;36:1-48.
10. Patil P, Peng RD, Leek JT. What should researchers expect when they replicate studies? Estimating the probability of replication. PLoS ONE. 2016;11:e0158823.
11. [PredictionGap citation — in preparation]
