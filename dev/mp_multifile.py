import sys

# import mss
sys.path.append('../')
from mss import mssmain as msm
from mss import align
import multiprocessing
from timeit import default_timer as timer
import glob
import pandas as pd


def main():
    start = timer()
    input_path = str(input('file path (folder): \n'))
    print(glob.glob(input_path + '*.mzML'))
    output_path = input('output path (.csv): \n')
    noise_thres = int(input('noise threshold: \n'))
    error_ppm = int(input('feature extraction error (ppm): \n'))
    rt_error = float(input('alignment rt error (min): \n'))
    mz_error = float(input('alignment mz error (Da): \n'))
    all_scans, file_names = msm.batch_scans(input_path, remove_noise=True, thres_noise=noise_thres)
    file_list = [input_path + str(i) + '.csv' for i in file_names]
    files = list(zip(all_scans, file_list))
    jobs = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    for scans in files:
        p = multiprocessing.Process(target=msm.mp_peak_list, args=(scans[0], scans[1], error_ppm, return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    df_list = return_dict.values()  # Check the order of the dict value!
    alignment = align.mss_align(df_list, output_path, return_dict.keys(), RT_error=rt_error, mz_error=mz_error)
    end = timer()
    print(f'elapsed time: {end - start}')

    return


if __name__ == '__main__':
    main()
