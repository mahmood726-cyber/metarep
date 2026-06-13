# Quick inspector for one Pairwise70 RDA file. Pass the path as the first
# argument, or set PAIRWISE70_DATA_DIR to the directory holding the .rda files.
.args <- commandArgs(trailingOnly = TRUE)
.f <- if (length(.args) >= 1) {
  .args[1]
} else {
  file.path(Sys.getenv("PAIRWISE70_DATA_DIR", unset = "data/pairwise70"),
            "CD000028_pub4_data.rda")
}
d <- get(load(.f))
cat("Class:", class(d), "\n")
cat("Cols:", paste(names(d), collapse=", "), "\n")
cat("Rows:", nrow(d), "\n")
cat("Mean:", head(d$Mean, 5), "\n")
cat("CI.start:", head(d$CI.start, 5), "\n")
cat("CI.end:", head(d$CI.end, 5), "\n")
