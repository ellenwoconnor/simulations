from collections import defaultdict
import hashlib
import random

## Questions:
## (1) Does hashing lead to users being assigned to the same condition across experiments?
## (2) Is the split even across partitions?

class Simulation:
  def __init__(self, n_shoppers, n_partitions, uniform_partitions=True):
    self.shoppers = {str(shopper_id): {'experiments': {}} for shopper_id in range(1, n_shoppers + 1)}
    self.partitions = {str(partition): 1.0/n_partitions for partition in range(1, n_partitions + 1)}
    self.experiments = {}
    if not uniform_partitions:
      self.adjust_probabilities()

  def adjust_probabilities(self):
    # Shift around partition probabilities
    partition_1, probability_1 = self.partitions.popitem()
    partition_2, probability_2 = self.partitions.popitem()

    adjusted_probability = min(probability_1, probability_2)/2.0
    self.partitions[partition_1] = probability_1 - adjusted_probability
    self.partitions[partition_2] = probability_2 + adjusted_probability

  def generate_shoppers(self):
    """
    Generates fake shoppers with some n-membered partition
    Can assign shoppers to partitions at random or in sequential blocks
    """

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

  def generate_experiment_name(self, n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

  def bucket_shoppers(self):
    experiment_name = self.generate_experiment_name(7)
    self.experiments[experiment_name] = {}
    buckets_by_partition = { partition: {} for partition in self.partitions }

    for shopper in self.shoppers:
      shopper_partition = self.shoppers[shopper]['partition']
      hash_id = self.hash_bin([shopper, experiment_name])
      bucket = 'control' if (hash_id % 100) < 50 else 'treatment'
      self.shoppers[shopper]['experiments'][experiment_name] = bucket

      if bucket in self.experiments[experiment_name]:
        self.experiments[experiment_name][bucket].add(shopper)
      else:
        self.experiments[experiment_name][bucket] = set([shopper])

      if bucket in buckets_by_partition[shopper_partition]:
        buckets_by_partition[shopper_partition][bucket] += 1
      else:
        buckets_by_partition[shopper_partition][bucket] = 1

    return buckets_by_partition
