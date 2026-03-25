#!/usr/bin/env Rscript
# MetaRep Pipeline: Replication Probability across 501 Cochrane Reviews
# Computes P(rep) for each review's primary analysis using the MetaRep formula

suppressPackageStartupMessages(library(metafor))

DATA_DIR <- "C:/Models/Pairwise70/data"
OUT_DIR  <- "C:/Models/MetaRep/data"
dir.create(OUT_DIR, showWarnings = FALSE, recursive = TRUE)

rda_files <- list.files(DATA_DIR, pattern = "\\.rda$", full.names = TRUE)
cat("Found", length(rda_files), "RDA files\n")

# Normal CDF
phi <- function(x) pnorm(x)

# Core MetaRep formula
# P(rep) = Phi((|theta| - z_alpha * se_new) / sqrt(tau2 + se_new^2))
rep_prob <- function(theta, tau2, se_new, alpha = 0.05) {
  z_alpha <- qnorm(1 - alpha / 2)
  pred_sd <- sqrt(tau2 + se_new^2)
  if (pred_sd <= 0) return(ifelse(abs(theta) > z_alpha * se_new, 1, 0))
  pnorm((abs(theta) - z_alpha * se_new) / pred_sd)
}

# Classical power
classical_power <- function(theta, se_new, alpha = 0.05) {
  z_alpha <- qnorm(1 - alpha / 2)
  pnorm(abs(theta) / se_new - z_alpha)
}

results <- data.frame(
  review_id = character(),
  analysis_name = character(),
  k = integer(),
  theta = numeric(),
  se = numeric(),
  tau2 = numeric(),
  i2 = numeric(),
  p_value = numeric(),
  significant = logical(),
  median_n = numeric(),
  se_typical = numeric(),
  p_rep = numeric(),
  p_classical = numeric(),
  rep_gap = numeric(),
  stringsAsFactors = FALSE
)

errors <- character()
n_processed <- 0

for (f in rda_files) {
  review_id <- sub("_data\\.rda$", "", basename(f))

  tryCatch({
    d <- get(load(f))

    # Use first analysis group (primary analysis)
    if ("Analysis.number" %in% names(d)) {
      primary <- d[d$Analysis.number == min(d$Analysis.number), ]
    } else {
      primary <- d
    }

    # Need at least 2 studies for meta-analysis
    if (nrow(primary) < 2) next

    # Compute log-scale effect + SE from CI
    # Mean is on ratio scale for most Cochrane reviews
    yi <- log(primary$Mean)

    # SE from CI: SE = (log(CI.end) - log(CI.start)) / (2 * 1.96)
    sei <- (log(primary$CI.end) - log(primary$CI.start)) / (2 * qnorm(0.975))

    # Remove invalid entries
    valid <- is.finite(yi) & is.finite(sei) & sei > 0
    yi <- yi[valid]
    sei <- sei[valid]

    if (length(yi) < 2) next

    # Fit random-effects model (REML)
    fit <- tryCatch(
      rma(yi = yi, sei = sei, method = "REML"),
      error = function(e) NULL
    )
    if (is.null(fit)) next

    theta <- as.numeric(fit$beta)
    se_pooled <- as.numeric(fit$se)
    tau2 <- as.numeric(fit$tau2)
    i2 <- as.numeric(fit$I2)
    p_val <- as.numeric(fit$pval)
    k <- fit$k

    # Typical study SE: median SE across studies in this review
    median_se <- median(sei, na.rm = TRUE)

    # Compute replication probability at typical study size
    p_r <- rep_prob(theta, tau2, median_se, 0.05)
    p_c <- classical_power(theta, median_se, 0.05)

    # Median total N across studies
    total_n <- primary$Experimental.N + primary$Control.N
    total_n <- total_n[valid]
    med_n <- median(total_n, na.rm = TRUE)

    results <- rbind(results, data.frame(
      review_id = review_id,
      analysis_name = as.character(primary$Analysis.name[1]),
      k = k,
      theta = theta,
      se = se_pooled,
      tau2 = tau2,
      i2 = i2,
      p_value = p_val,
      significant = p_val < 0.05,
      median_n = med_n,
      se_typical = median_se,
      p_rep = p_r,
      p_classical = p_c,
      rep_gap = p_c - p_r,
      stringsAsFactors = FALSE
    ))

    n_processed <- n_processed + 1
    if (n_processed %% 50 == 0) cat("  Processed", n_processed, "reviews...\n")

  }, error = function(e) {
    errors <<- c(errors, paste0(review_id, ": ", e$message))
  })
}

cat("\n=== PIPELINE COMPLETE ===\n")
cat("Processed:", n_processed, "reviews\n")
cat("Errors:", length(errors), "\n")

# Save full results
write.csv(results, file.path(OUT_DIR, "rep_prob_all.csv"), row.names = FALSE)
saveRDS(results, file.path(OUT_DIR, "rep_prob_all.rds"))

# ── HEADLINE STATISTICS ──
sig <- results[results$significant == TRUE, ]
cat("\n=== HEADLINE FINDINGS ===\n")
cat("Total reviews analyzed:", nrow(results), "\n")
cat("Significant (p < 0.05):", nrow(sig), "(", round(100 * nrow(sig) / nrow(results), 1), "%)\n")
cat("\nAmong SIGNIFICANT meta-analyses:\n")
cat("  Median P(replication):   ", round(median(sig$p_rep, na.rm = TRUE) * 100, 1), "%\n")
cat("  Mean P(replication):     ", round(mean(sig$p_rep, na.rm = TRUE) * 100, 1), "%\n")
cat("  P(rep) < 50%:            ", sum(sig$p_rep < 0.50, na.rm = TRUE), "(",
    round(100 * sum(sig$p_rep < 0.50, na.rm = TRUE) / nrow(sig), 1), "%)\n")
cat("  P(rep) < 80%:            ", sum(sig$p_rep < 0.80, na.rm = TRUE), "(",
    round(100 * sum(sig$p_rep < 0.80, na.rm = TRUE) / nrow(sig), 1), "%)\n")
cat("\n  Median classical power:  ", round(median(sig$p_classical, na.rm = TRUE) * 100, 1), "%\n")
cat("  Median rep gap (classical - predictive):", round(median(sig$rep_gap, na.rm = TRUE) * 100, 1), "pp\n")

cat("\nAmong ALL meta-analyses:\n")
cat("  Median P(replication):   ", round(median(results$p_rep, na.rm = TRUE) * 100, 1), "%\n")
cat("  P(rep) < 50%:            ", sum(results$p_rep < 0.50, na.rm = TRUE), "(",
    round(100 * sum(results$p_rep < 0.50, na.rm = TRUE) / nrow(results), 1), "%)\n")

cat("\nMedian heterogeneity (tau2):", round(median(results$tau2, na.rm = TRUE), 4), "\n")
cat("Median I2:", round(median(results$i2, na.rm = TRUE), 1), "%\n")
cat("Median k:", median(results$k), "\n")

# Quartile table
cat("\n=== P(rep) DISTRIBUTION (significant MAs) ===\n")
cat("  Q1 (25th):  ", round(quantile(sig$p_rep, 0.25, na.rm = TRUE) * 100, 1), "%\n")
cat("  Median:     ", round(quantile(sig$p_rep, 0.50, na.rm = TRUE) * 100, 1), "%\n")
cat("  Q3 (75th):  ", round(quantile(sig$p_rep, 0.75, na.rm = TRUE) * 100, 1), "%\n")
cat("  Min:        ", round(min(sig$p_rep, na.rm = TRUE) * 100, 1), "%\n")
cat("  Max:        ", round(max(sig$p_rep, na.rm = TRUE) * 100, 1), "%\n")
