import os
import pandas as pd
from pprint import pprint
import itertools
import argparse
import time
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

class Apriroi_Algorithm():
    '''
    This class implements the Apriori algorithm for frequent itemset generation and
    confidence based rule generation. The minimum support and confidence values are
    defined by the user.

    @Author: Naren Surampudi
    '''

    def __init__(self):
        self.DEFAULT_DATA = "test_data.csv"   # Default dataset to use.
        self.MIN_SUPPORT = 2   # Default minimum support for above dataset.
        self.MIN_CONFIDENCE = 0.5   # Default minimum confidence for above dataset.

    def freq_itemset_gen(self, freq_prev_set, groceries_list, set_len, min_support):
        '''
        This function generates the frequent itemsets present in a set of transactions by
        evaluating against the minimum support value defined by the user.

        @type freq_prev_set: dictionary
        @param freq_prev_set: The subsets of to-be generated frequent itemsets.
        @type groceries_list: list
        @param groceries_list: The dataset being operated upon.
        @type set_len: int
        @param set_len: Length of current set.
        @type min_support: int
        @param min_support: Minimum support defined by the user.
        '''
        new_itemset = {}
        print("Generating frequent itemsets for order " + str(set_len) + "...")
        # This nested for loop snippet here generates all the possible itemsets
        # possible from the previous generation of frequent itemsets. Newly
        # generaterd itemsets are assigned a value of zero.
        for item in freq_prev_set:
            for sec_item in freq_prev_set:
                if item != sec_item:
                    if set_len == 2:
                        new_tuple = tuple(set([item]).union(set([sec_item])))
                        new_itemset_keys = new_itemset.keys()
                        flag = 0
                        for itemset_key in new_itemset_keys:
                            if sorted(new_tuple) == sorted(tuple(itemset_key)):
                                flag = 1
                                break
                        if flag == 0:
                            if len(new_tuple) == set_len:
                                new_itemset[new_tuple] = 0
                        #if sorted(new_tuple) not in sorted(tuple(new_itemset.keys())) and len(new_tuple) == set_len:
                            #new_itemset[new_tuple] = 0
                    else:
                        new_itemset_keys = new_itemset.keys()
                        flag = 0
                        new_tuple = tuple(set(list(item)).union(set(list(sec_item))))
                        for itemset_key in new_itemset_keys:
                            if sorted(new_tuple) == sorted(tuple(itemset_key)):
                                flag = 1
                                break
                        if flag == 0:
                            if len(new_tuple) == set_len:
                                new_itemset[new_tuple] = 0
                        #if sorted(new_tuple) not in sorted(tuple(new_itemset.keys())) and len(new_tuple) == set_len:
                            #new_itemset[new_tuple] = 0
        # Counting of itemsets taking place here.
        for g_list in groceries_list:
            for new_key in new_itemset.keys():
                if set(g_list).intersection(set(new_key)) == set(new_key):
                    new_itemset[new_key] = new_itemset[new_key] + 1

        freq_new_set = {}
        non_freq_itemset = {}
        # Frequent itemsets generated according by evaluating against user defined
        # minimum support.
        for new_key in new_itemset.keys():
            if new_itemset[new_key] >= min_support:
                freq_new_set[new_key] = new_itemset[new_key]
            else:
                non_freq_itemset[new_key] = new_itemset[new_key]

        return freq_new_set

    def maximal_itemset_gen(self, freq_itemsets, max_len):
        '''
        This function generates the maximal frequent itemsets from the generated frequent
        itemsets

        @type freq_itemsets: dictionary
        @param freq_itemsets: The complete set of frequent itemsets.
        @type max_len: int
        @param max_len: The maximum length of a transaction in the dataset.
        '''
        maximal_itemsets = {}

        max_freq_transaction = int(max(freq_itemsets.keys()))
        min_freq_transaction = int(min(freq_itemsets.keys()))
        # Candidate itemsets will only be generated if the longest frequent transaction
        # is smaller than the largest transaction in the database. Transactions whose
        # length is more than 2 will be considered.
        if max_freq_transaction < max_len:
            for transaction_len in range(2, max_freq_transaction):
                if transaction_len + 1 <= max_freq_transaction:
                    current_level = freq_itemsets[str(transaction_len)].keys()
                    next_level = freq_itemsets[str(transaction_len + 1)].keys()
                    for itemset in current_level:
                        # Flag to check itemset in current level is possible subset
                        # in next level
                        flag = 0
                        for n_itemset in next_level:
                            if set(list(itemset)).issubset(set(list(n_itemset))):
                                flag = 1
                                break
                        if flag == 0:
                            maximal_itemsets[itemset] = freq_itemsets[str(transaction_len)][itemset]

        for itemset in freq_itemsets[str(max_freq_transaction)]:
            maximal_itemsets[itemset] = freq_itemsets[str(max_freq_transaction)][itemset]

        return maximal_itemsets

    def closed_freq_itemset_gen(self, freq_itemsets, max_len):
        '''
        This function generates the closed frequent itemsets from the generated frequent
        itemsets

        @type freq_itemsets: dictionary
        @param freq_itemsets: The complete set of frequent itemsets.
        @type max_len: int
        @param max_len: The maximum length of a transaction in the dataset.
        '''
        closed_freq_itemsets = {}

        max_freq_transaction = int(max(freq_itemsets.keys()))
        min_freq_transaction = int(min(freq_itemsets.keys()))
        # Candidate itemsets will only be generated if the longest frequent transaction
        # is smaller than the largest transaction in the database. Transactions whose
        # length is more than 2 will be considered.
        if max_freq_transaction < max_len:
            for transaction_len in range(2, max_freq_transaction):
                if transaction_len + 1 <= max_freq_transaction:
                    current_level = freq_itemsets[str(transaction_len)].keys()
                    next_level = freq_itemsets[str(transaction_len + 1)].keys()
                    for itemset in current_level:
                        flag = 0
                        for n_itemset in next_level:
                            if freq_itemsets[str(transaction_len)][itemset] < freq_itemsets[str(transaction_len + 1)][n_itemset]:
                                flag = 1
                                break
                        if flag == 0:
                            closed_freq_itemsets[itemset] = freq_itemsets[str(transaction_len)][itemset]

        return closed_freq_itemsets

    def rule_generation(self, freq_itemsets, min_confidence, closed_freq_itemsets):
        '''
        This function generates association rules from the generated frequent itemsets by
        evaluating against the minimum confidence value defined by the user.

        @type freq_itemsets: dictionary
        @param freq_itemsets: The complete set of frequent itemsets.
        @type min_confidence: int
        @param min_confidence: Minimum confidence defined by the user.
        '''
        association_rules = {}
        redundant_rules = {}
        closed_freq_keys = closed_freq_itemsets.keys()
        max_key = int(max(freq_itemsets.keys()))

        for key in freq_itemsets.keys():
            for itemset in freq_itemsets[key]:
                set_len = len(itemset)
                if int(key) > 1:
                    for consequent_len in range(1, set_len):
                        # Getting all possible combinations of the itemsets-consequents
                        itemset_subsets = set(itertools.combinations(set(list(itemset)), (set_len - consequent_len)))
                        consequents = set(itertools.combinations(set(list(itemset)), consequent_len))
                        for itemset_subset in itemset_subsets:
                            for consequent in consequents:
                                # Check if the pairs occur in the database.
                                set_union = set(list(itemset_subset)).union(set(list(consequent)))
                                if set_union == set(list(itemset)) and len(set_union) == len(itemset):
                                    if len(itemset_subset) == 1:
                                        itemset_subset = itemset_subset[0]
                                        sub_key = 1
                                    else:
                                        sub_key = len(itemset_subset)
                                    confidence = freq_itemsets[key][itemset] / freq_itemsets[str(sub_key)][itemset_subset]
                                    if confidence >= min_confidence:
                                        if len(consequent) == 1:
                                            consequent = consequent[0]
                                        flag = 0
                                        for closed_itemset in closed_freq_keys:
                                            if set(list(itemset_subset)).issubset(set(list(closed_itemset))):
                                                if len(closed_itemset) == 1:
                                                    closed_itemset = closed_itemset[0]
                                                    closed_sub_key = 1
                                                else:
                                                    closed_sub_key = len(closed_itemset)
                                                if freq_itemsets[str(sub_key)][itemset_subset] == freq_itemsets[str(closed_sub_key)][closed_itemset]:
                                                    flag = 1
                                                    break
                                        if flag == 0:
                                            association_rules[tuple([itemset_subset, consequent])] = confidence
                                        else:
                                            redundant_rules[tuple([itemset_subset, consequent])] = confidence

        return [association_rules, redundant_rules]

    def max_length(self, some_list):
        '''
        This function returns the maximum length of an item present within another item.

        @type some_list: list
        @param some_list: Any list.
        '''
        max_len = 0
        for single_list in some_list:
            if max_len < len(single_list):
                max_len = len(single_list)

        return max_len

if __name__ == "__main__":
    apriori = Apriroi_Algorithm()

    parser = argparse.ArgumentParser(description='take input')
    parser.add_argument('data_path', help='path of file to process', default=apriori.DEFAULT_DATA, type=str)
    parser.add_argument('min_support', help='minimum support', default=apriori.MIN_SUPPORT, type=int)
    parser.add_argument('min_confidence', help='minimum confidence', default=apriori.MIN_CONFIDENCE, type=float)
    args = parser.parse_args()
    data_file = vars(args)['data_path']

    groceries_data = pd.read_csv(data_file, sep='delimiter', header=None, engine='python')

    temp_list = groceries_data[0].tolist()
    groceries_list = []

    for g_list in temp_list:
        groceries_list.append(g_list.split(','))

    transactions = len(groceries_list)
    max_len = apriori.max_length(groceries_list)

    single_itemset = {}

    single_itemset_keys = single_itemset.keys()

    for g_list in groceries_list:
        for grocery in g_list:
            if grocery != '':
                if grocery in single_itemset_keys:
                    single_itemset[grocery] = single_itemset[grocery] + 1
                else:
                    single_itemset[grocery] = 1

    min_support = vars(args)['min_support']
    min_confidence = vars(args)['min_confidence']

    print("Minimum support: " + str(min_support))
    print("Minimum confidence: " + str(min_confidence))

    freq_single_set = {}

    pool = ThreadPool(processes=cpu_count())

    try:
        start = time.clock()

        print("Generating frequent itemsets for order 1...")

        for single_key in single_itemset.keys():
            if single_itemset[single_key] >= min_support:
                freq_single_set[single_key] = single_itemset[single_key]

        freq_itemsets = {}

        freq_itemsets['1'] = freq_single_set

        for i in range(2, max_len + 1):
            prev_freq_set = freq_itemsets[str(i - 1)]
            temp_set = (pool.apply_async(apriori.freq_itemset_gen, (prev_freq_set, groceries_list, i, min_support))).get()
            if temp_set == {}:
                break
            else:
                freq_itemsets[str(i)] = temp_set

        end = time.clock()
        freq_gen_time = end - start

        print("\nFrequent itemsets with support:")
        pprint(freq_itemsets)

        file_name = 'Freq_Items_sup(' + str(min_support) + ").csv"
        col_names = ['Frequent Itemset', 'Support']
        freq_itemsets_df = pd.DataFrame(columns=col_names)

        for transaction_len in freq_itemsets.keys():
            for itemset in freq_itemsets[transaction_len].keys():
                data_line = [itemset, str(freq_itemsets[transaction_len][itemset])]
                freq_itemsets_df.loc[len(freq_itemsets_df)] = data_line

        freq_itemsets_df.to_csv(file_name, index=False, encoding='utf-8')

    except:
        print("\nError occured during frequent itemsets generation. Try running again.")
        freq_gen_time = 0

    try:
        start = time.clock()

        maximal_itemsets = (pool.apply_async(apriori.maximal_itemset_gen, (freq_itemsets, max_len))).get()

        end = time.clock()
        max_gen_time = end - start

        print("\nMaximal itemsets with support:")
        pprint(maximal_itemsets)
    except:
        print("\nError occured during maximal itemsets generation. Try running again.")
        max_gen_time = 0

    try:
        start = time.clock()

        closed_freq_itemsets = (pool.apply_async(apriori.closed_freq_itemset_gen, (freq_itemsets, max_len))).get()

        end = time.clock()
        closed_gen_time = end - start

        print("\nClosed frequent itemsets with support:")
        pprint(closed_freq_itemsets)
    except:
        print("\nError occured during closed frequent itemsets generation. Try running again.")
        closed_gen_time = 0

    try:
        start = time.clock()

        rules = (pool.apply_async(apriori.rule_generation, (freq_itemsets, min_confidence, closed_freq_itemsets))).get()
        association_rules = rules[0]
        redundant_rules = rules[1]

        end = time.clock()
        rule_gen_time = end - start

        print("\nGenerated association rules:")
        pprint(association_rules)
        print("\nRedundant rules:")
        pprint(redundant_rules)

        file_name = 'Assn_Rules_sup(' + str(min_support) + ")_conf(" + str(min_confidence) + ").csv"
        col_names = ['LHS', 'LHS itemset count', '--->', 'RHS', 'RHS itemset count', 'Confidence']
        assn_rules_df = pd.DataFrame(columns=col_names)

        for itemsets in association_rules.keys():
            LHS = itemsets[0]
            if isinstance(LHS, str):
                LHS_count = freq_itemsets['1'][LHS]
            else:
                LHS_count = freq_itemsets[str(len(LHS))][LHS]
            RHS = itemsets[1]
            if isinstance(RHS, str):
                RHS_count = freq_itemsets['1'][RHS]
            else:
                RHS_count = freq_itemsets[str(len(RHS))][RHS]
            confidence = association_rules[itemsets]
            data_list = [LHS, LHS_count, '--->', RHS, RHS_count, confidence]
            assn_rules_df.loc[len(assn_rules_df)] = data_list

        assn_rules_df.to_csv(file_name, index=False, encoding='utf-8')

    except Exception as e:
        print("\nError occured during association rules generation. Try running again.")
        rule_gen_time = 0
        print(e)

    print("\nTimings:")
    print("Frequent itemsets generation: " + str(freq_gen_time))
    print("Maximal itemsets generation: " + str(max_gen_time))
    print("Closed frequent itemsets generation: " + str(closed_gen_time))
    print("Association rules generation: " + str(rule_gen_time))
