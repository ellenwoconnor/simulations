pvals<-c()

getMVBinomialData <- function(n, effect1, effect2) {
  f1_labels<-c(rep('A', n/2), rep('B', n/2))
  f2_labels<-c(rep('X', n/4), rep('Y', n/4), rep('X', n/4), rep('Y', n/4))
  results<-c(rbinom(n/4, 1, .08), rbinom(n/4, 1, .08+effect2), rbinom(n/4, 1, .08+effect2), rbinom(n/4, 1, .08+effect1+effect2))
  data<-cbind(f1_labels, f2_labels, results) 
  return(data.frame(data))
}

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

simulate<-function(n, simulations, effect1, effect2) {
  f1_regression<-c()
  f2_regression<-c()
  f1_chi<-c()
  f2_chi<-c()

  for(i in 0:simulations) {
    data<-getMVBinomialData(n, effect1, effect2)
    regression <- glm(results ~ f2_labels * f1_labels, data=data, family=binomial)
    f1_regression <- append(f1_regression, summary(regression)$coefficients[,4][3])
    f2_regression <- append(f2_regression, summary(regression)$coefficients[,4][2])
    f1_contingency <- xtabs(~f1_labels+results, data)
    f2_contingency <- xtabs(~f1_labels+results, data)
    chi_f1<-chisq.test(f1_contingency)
    chi_f2<-chisq.test(f2_contingency)
    f1_chi<-append(f1_chi, chi_f1$p.value)
    f2_chi<-append(f2_chi, chi_f2$p.value)
  }

  all_pvals<-data.frame(cbind(f1_regression, f2_regression, f1_chi, f2_chi))
  return(all_pvals)
}

getPower<-function(lower, upper, simulations, effect1, effect2) {
  all_means<-data.frame()
  for(n in seq(lower, upper, by=100)) {
    pvals<-simulate(n, simulations, effect1, effect2)
    means<-sapply(pvals, mean)
    means$n<-n
    all<-data.frame(rbind(all_means, means))
  }
  return(all)
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

simulateX2<-function(n, simulations, effect1, effect2) {
  f1<-c()
  f2<-c()
  for(i in 0:simulations) {
    data<-getMVBinomialData(n, effect1, effect2)
    data$results<-as.numeric(data$results)
    chi_f1<-chisq.test(subset(data, f1_labels == 'A')$results, subset(data, f1_labels == 'B')$results)
    chi_f2<-chisq.test(subset(data, f2_labels == 'X')$results, subset(data, f2_labels == 'Y')$results)
    message(chi_f1$p.value, chi_f2$p.value)
    f1<-append(f1, chi_f1$p.value)
    f2<-append(f2, chi_f2$p.value)
  }
  return(data.frame(cbind(f1, f2)))
}