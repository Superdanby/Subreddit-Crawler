from numba import jit
from PIL import Image
from pathlib import Path
import argparse
# import cProfile
import csv
import imagehash
import json
import numpy as np
# import time


class Data:
    bits = None
    data_list = None  # [image_path, hash_value, disjoint_set]
    difference = None
    hash_np = None  # hhash
    hash_size = 64
    similarity = 0.8

    def __init__(self, hash_size=None, similarity=None):
        if hash_size is not None:
            self.hash_size = hash_size
        if similarity is not None:
            self.similarity = similarity
        self.clear()

    def add_csv(self, csvfile: str=None, recompute=False):
        """Load data from the csvfile: [str(image_path), str(hash with hash_size=hash_size)]
        csvfile: str(file_path)
        recompute: discard all hash and recompute them again with current settings
        """
        if csvfile is not None:
            with open(csvfile, 'r') as f:
                csvreader = csv.reader(f)
                headers = next(csvreader, None)  # filepath, hash
                input = [[str(row[0]), str(row[1]), -1] for row in csvreader]
                # append to data_list
                self.data_list = self.data_list + input
                # append to numpy array
                arr = []
                for row in input:
                    arr.append(imagehash.hex_to_hash(row[1]).hash.flatten())
                self.hash_np = np.append(self.hash_np, np.array(arr), axis=0)
        else:
            print(f'CSV file not specified.\n')

    def add_data(self, path=None, hash=None, similar_test=False):
        """Add an entry
        path: str(image path)
        hash: imagehash(imagehash object of the image)
        similar_test: bool(test the image against the others in self.data_list)
        """
        if path is not None and hash is not None:
            # append to data_list
            self.data_list.append([path, str(hash), -1])
            # append to numpy array
            if similar_test is True:
                # do comparision
                self.similar(hash)
            self.hash_np = np.append(self.hash_np, np.array([hash.hash.flatten()]), axis=0)
        else:
            print(f'Input not specified.\n')

    def add_image(self, path: str):
        """Add an image and test its similarity against the others in self.data_list
        path: str(path to the image)
        """
        hashd = imagehash.dhash(Image.open(path), hash_size=self.hash_size)
        self.add_data(path=path, hash=hashd, similar_test=True)

    def clear(self):
        """Clear all dynamically initialized properties"""
        self.bits = 4 * self.hash_size ** 2
        self.data_list = []
        self.difference = 1 - self.similarity
        self.hash_np = np.empty(shape=(0, self.hash_size ** 2))

    def disjoint_add(self, parent=-1, child=-1):
        """Updates disjoint set in self.data_list"""
        assert(child > -1)
        if parent == -1:
            if self.data_list[child][2] == -1:
                self.data_list[child][2] = child
                return
            else:
                parent = self.data_list[child][2]
        if child != parent:
            self.data_list[child][2] = self.disjoint_add(self.data_list[parent][2], parent)
        else:
            return parent

    @staticmethod
    def group_similarity(hash_np=None, target_idx=0):
        """Calculates the similarity of the hash strings against the target
        target_idx: the index of the target in the hash list
        """
        if hash_np is None:
            return None
        target = hash_np[target_idx]
        bits = 4 * target.shape[0]
        diff = hash_np != target
        diff = diff.sum(axis=1)
        diff = diff / bits
        return [1 - x for x in diff]

    def similar(self, hash):
        """Check hash string similarity with existing data
        hash: imagehash(imagehash object of the image)
        """
        if self.hash_np.size <= 0:
            return
        hash_new = np.array(hash.hash.flatten())
        diff = self.hash_np != hash_new
        diff = diff.sum(axis=1)
        diff = diff / self.bits
        # diff = self.__simialr_numba(hash_new)
        # get index
        indices = [i for i, e in enumerate(diff) if self.difference >= e]
        if len(indices) == 0:
            return
        # add the index of the new image to the same tree
        indices.append(len(self.data_list) - 1)
        # check group with disjoint tree
        it = iter(indices)
        parent = next(it)
        self.disjoint_add(child=parent)
        for child in it:
            self.disjoint_add(parent=parent, child=child)

    @jit
    def __simialr_numba(self, hash_new):
        """Numba(Makes not much difference though QAQQQ)"""
        diff = self.hash_np != hash_new
        diff = diff.sum(axis=1)
        diff = diff / self.bits
        return diff

    def finalize(self, verbose=False):
        """Dump self.data_list to 'similage.csv' and similar images to 'similar.json'"""
        # filter out individuals: parent is -1
        similars = [x + [y] for x, y in zip(self.data_list, self.hash_np) if x[2] != -1]
        print(similars[0])
        if similars is None:
            return
        similars = sorted(similars, key=lambda x: x[2])
        # create dictionary
        output = {}
        for x in similars:
            if x[2] not in output:
                output[x[2]] = [{'path': x[0]}]
            else:
                output[x[2]].append({'path': x[0]})
        # headers for csv file
        headers = ['path']
        if verbose is True:
            headers.append('hash')
            hash_dict = {}
            print(len(similars))
            for x in similars:
                if x[2] not in hash_dict:
                    hash_dict[x[2]] = [[x[1]], [x[3]]]
                else:
                    hash_dict[x[2]][0].append(x[1])
                    hash_dict[x[2]][1].append(x[3])
            for series in hash_dict:
                similarity_list = self.group_similarity(hash_np=np.array(hash_dict[series][1]), target_idx=-1)
                for i, (hashstr, similarity) in enumerate(zip(hash_dict[series][0], similarity_list)):
                    output[series][i]['hash'] = hashstr
                    output[series][i]['similarity'] = similarity
        with open('similar.json', 'w') as f:
            json.dump(output, f)
        # t = time.time()
        with open('similage.csv', 'w', newline='') as f:
            csvwriter = csv.writer(f, delimiter=',', lineterminator='\n')
            csvwriter.writerow(['path', 'hash'])
            for row in self.data_list:
                csvwriter.writerow([row[0], row[1]])
        # print(time.time() - t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--imagecsv', nargs='*')
    parser.add_argument('--newimages', nargs='*')
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    csvfiles = parser.parse_args().imagecsv
    image_paths = parser.parse_args().newimages
    verbose = parser.parse_args().verbose

    data = Data()

    if csvfiles is not None:
        for csvfile in csvfiles:
            data.add_csv(csvfile=csvfile)

    if image_paths is not None:
        path_list = []
        for ipath in image_paths:
            p = Path(ipath)
            assert(p.exists() is True)
            if p.is_dir():
                path_list.append([str(x) for x in p.glob('**/*') if x.is_file()])
            elif p.is_file():
                path_list.append(str(p))
        for path in path_list:
            data.add_image(path=path)

    data.finalize(verbose=verbose)
    # cProfile.run('data.finalize(verbose=verbose)')
    # cProfile.run('data.finalize(verbose=False)')

# Notes:
# Conversion between imagehash object and hash string takes a lot of time. Hence, it should be avoided in all costs.
# numba
# k means?
