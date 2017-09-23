from collections import defaultdict
import hashlib
import random

class BucketSimulation:
  def __init__(self, n_shoppers, n_types):
    self.n_shoppers = n_shoppers
    self.n_types = n_types

  def generate_shoppers(self, random_partition=True):
    """
    Generates fake shoppers with some n-membered partition
    Can assign shoppers to partitions at random or in sequential blocks
    """
    shoppers = {}
    shopper_types = range(1, self.n_types + 1)
    current_type = min(shopper_types)

    for shopper_id in range(1, self.n_shoppers + 1):
      if random_partition or (current_type + 1) > max(shopper_types): # leftovers if not evenly divisible
        shopper_type = random.randrange(1, self.n_types + 1)
      else: 
        if shopper_id > (self.n_shoppers / self.n_types) * current_type: # At a partition boundary
          current_type += 1    
        shopper_type = current_type

      shoppers[shopper_id] = { 'partition': shopper_type }

    return shoppers

  def hash_bin(self, string_list):
    """Return a condition using base-16 hash of a list of strings"""
    hasher = hashlib.md5()
    for string in string_list:
      hasher.update(string)

    hash_id = int(hasher.hexdigest(), 16)

    return hash_id

  def bucket_users(self, experiment_name, percent_control=50, percent_treatment=50):
    for shopper in shoppers:
      hash_id = self.hash_bin([shopper, experiment_name])
      bucket = 'control' if (hash_id % 100) < 50 else 'treatment'
      shoppers[shopper][experiment_name] = self.hash_bin([shopper, experiment_name])

    return shoppers

if __name__ == "__main__":
  s = BucketSimulation(10000, 5)
  s.generate_shoppers()
