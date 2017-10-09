getBinomialData <- function(n, baseline, effect) {
  labels<-c(rep('A', n/2), rep('B', n/2))
  results<-c(rbinom(n/2, 1, baseline), rbinom(n/2, 1, baseline+effect))
  data<-cbind(labels, results)
  return(data.frame(data))
}

simulateX2<-function(n, simulations, baseline, effect) {
  p_vals<-c()
  for(i in 0:simulations) {
    data<-getBinomialData(n, baseline, effect)
    message(table(data))
    chi<-chisq.test(table(data))
    message(chi$p.value)
    p_vals<-append(p_vals, chi$p.value)
  }
  return(p_vals)
}

getPower<-function(lower, upper, simulations, baseline, effect) {
  means<-c()
  sample_sizes<-c()
  for(n in seq(lower, upper, by=100)) {
    pvals<-simulateX2(n, simulations, baseline, effect)
    means<-append(means, mean(pvals))
    sample_sizes<-append(sample_sizes, n)
  }
  return(data.frame(cbind(means, sample_sizes)))
}

simulateLM<-function(n, simulations, effect1, effect2) {
  f1<-c()
  f2<-c()
  for(i in 0:simulations) {
    data<-getMVBinomialData(n, effect1, effect2)
    message('Actual', summary(data$results))
    fit<-lm(as.numeric(results) ~ f2_labels * f1_labels, data=data)
    p_vals<-summary(fit)$coefficients[,4]
    cat(p_vals)
    f1<-append(f1, p_vals[2])
    f2<-append(f2, p_vals[3])
    cat(f1)
  }
  return(data.frame(cbind(f1, f2)))
}

# simulateMVX2<-function(n, simulations, effect1, effect2) {
#   f1<-c()
#   f2<-c()
#   for(i in 0:simulations) {
#     data<-getMVBinomialData(n, effect1, effect2)
#     data$results<-as.numeric(data$results)
#     chi_f1<-chisq.test(subset(data, f1_labels == 'A')$results, subset(data, f1_labels == 'B')$results)
#     chi_f2<-chisq.test(subset(data, f2_labels == 'X')$results, subset(data, f2_labels == 'Y')$results)
#     message(chi_f1$p.value, chi_f2$p.value)
#     f1<-append(f1, chi_f1$p.value)
#     f2<-append(f2, chi_f2$p.value)
#   }
#   return(data.frame(cbind(f1, f2)))
# }


isDetectable <- function(pvals, threshold) {
  significant_effects <- 0
  required_successes <- length(pvals) * threshold
  for (i in 0:length(pvals)) {
    if(i<.05) {
      significant_effects <- significant_effects + 1
    }
  }
  return(significant_effects >= required_successes)
}

require(ggplot2)
