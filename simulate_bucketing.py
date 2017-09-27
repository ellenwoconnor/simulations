from collections import defaultdict
from scipy import stats
import hashlib
import random
import string
import time
import pickle
import csv

## Questions:
## (1) Does hashing lead to users being assigned to the same condition across experiments? (not really)
## (2) Is the split even across partitions? (yes)

def save_to_csv(filename, results):
  """Writes a list of dictionaries to csv. Assumes all dictionaries are equal in length."""
  with open(filename, 'w') as csvfile:
    fieldnames = results[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
      writer.writerow(row)


class Simulator:
  def __init__(self, n_shoppers, n_partitions, uniform_partitions=True):
    # example shopper: { '1': { 'experiments': { 'sdfs': 'control' }, 'cohorts': {'control': 1}}
    self.shoppers = {str(shopper_id): { 'experiments': {}, 'cohorts': {}} for shopper_id in range(1, n_shoppers + 1)}
    self.partitions = {str(partition): 1.0/n_partitions for partition in range(1, n_partitions + 1)}
    if not uniform_partitions:
      self.adjust_probabilities()

    # Keep a running total of the counts for each specific shopper segment
    # example experiment: { '1': { 'control': 10, 'treatment': 10 }, ... }
    self.experiments = {}


  def adjust_probabilities(self):
    """Shifts around partition probabilities, e.g.: 
      { p1: .2, p2: .2 } -> { p1: .1, p2: .3 }
    """
    partition_1, probability_1 = self.partitions.popitem()
    partition_2, probability_2 = self.partitions.popitem()

    adjusted_probability = min(probability_1, probability_2)/2.0
    self.partitions[partition_1] = probability_1 - adjusted_probability
    self.partitions[partition_2] = probability_2 + adjusted_probability


  def generate_shoppers(self):
    """Generates partitioned fake shoppers"""
    partition_choices = []

    for partition in self.partitions: 
      partition_choices.extend(partition * (int(self.partitions[partition] * 100)))

    for shopper in self.shoppers:
      shopper_partition = random.choice(partition_choices)
      self.shoppers[shopper]['partition'] = shopper_partition


  def hash_bin(self, string_list):
    """Return a hash of a list of strings"""
    hasher = hashlib.md5()
    for string in string_list:
      hasher.update(string)

    hash_id = int(hasher.hexdigest(), 16)

    return hash_id


  def generate_experiment_name(self, n=8):
    """Generate a random n-length experiment ID"""
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


  def bucket_shoppers(self, experiment_name):
    """Assign each shopper a bucket for some experiment.
    Update cohort counts for shoppers and partitions.
    """
    self.experiments[experiment_name] = { partition: {} for partition in self.partitions }

    for shopper in self.shoppers:
      shopper_partition = self.shoppers[shopper]['partition']
      hash_id = self.hash_bin([shopper, experiment_name])
      bucket = 'control' if (hash_id % 100) < 50 else 'treatment'

      self.shoppers[shopper]['experiments'][experiment_name] = bucket
      if bucket in self.shoppers[shopper]['cohorts']:
        self.shoppers[shopper]['cohorts'][bucket] += 1
      else:
        self.shoppers[shopper]['cohorts'][bucket] = 1

      if bucket in self.experiments[experiment_name][shopper_partition]:
        self.experiments[experiment_name][shopper_partition][bucket] += 1
      else:
        self.experiments[experiment_name][shopper_partition][bucket] = 1


  def analyze_user_correlations(self):
    """Tests whether shoppers are assigned evenly to conditions"""
    results = []
    deltas = []
    x2_stats = []
    p_vals = []
    print 'Analyzing results'
    for shopper in self.shoppers:
      treatment_counts = self.shoppers[shopper]['cohorts']['treatment']
      control_counts = self.shoppers[shopper]['cohorts']['control']

      delta = abs(treatment_counts - control_counts)
      x2, p_val = stats.chisquare([treatment_counts, control_counts])
      deltas.append(delta)
      x2_stats.append(x2)
      p_vals.append(p_val)
      results.append({ 'shopper': shopper, 'delta': delta, 'p': p_val, 'x2': x2 })

    print 'Summary of deltas', stats.describe(deltas)
    print 'Summary of x2', stats.describe(x2_stats)
    print 'Summary of p', stats.describe(p_vals)

    return results


  def analyze_partition_splits(self):
    splits = []
    for experiment in self.experiments:
      x2, p_val = stats.chisquare(self.experiments[experiment]['1']['treatment'], self.experiments[experiment]['1']['treatment'])
      splits.append({ 'x2': x2, 'p': p_val })

    return splits


  def pickle_simulations(self, n_simulations):
    now = time.strftime("%x")
    shoppers_file = '{}_{}_shoppers.p'.format(now, n_simulations)
    experiments_file = '{}_{}_experiments.p'.format(now, n_simulations)
    print 'Pickling shoppers'
    pickle.dump(self.shoppers, open(shoppers_file, 'w'), protocol=pickle.HIGHEST_PROTOCOL)
    print 'Pickling experiments'
    pickle.dump(self.experiments, open(experiments_file, 'w'), protocol=pickle.HIGHEST_PROTOCOL)


  ## TODO 
  # Write shoppers to csv instead of pickle?
  # Analyze partitions


  def simulate(self, n_simulations):
    self.generate_shoppers()
    for n in range(1, n_simulations + 1):
      print 'Simulation', n
      self.bucket_shoppers(self.generate_experiment_name())

    # TODO - FIX me
    return self.analyze_user_correlations()

