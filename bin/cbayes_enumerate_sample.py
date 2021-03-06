#!/usr/bin/env python

"""cbayes_enumerate_sample.py

This script generates samples from the prior, or posterior, over model
topologies using the output a specified model probabilities file.

"""
from __future__ import division

import os
import argparse

import cmpy
import cmpy.inference.bayesianem as bayesem

from cbayes import check_positive_float
from cbayes import check_sr_tuple
from cbayes import read_datafile
from cbayes import sample_machines

def report_args(args):
    """Report the requested settings.
    
    Returns
    -------
    arg_str : str
        A summary of the script settings.

    """
    arg_list =[]

    arg_list.append("SETTINGS:\n")
    arg_list.append("-db : Database root directory "
            ">> {:s}\n".format(args.database_directory))
    arg_list.append("-idir : InferEM  sub-directory "
            ">> {:s}\n".format(args.inferem_directory))
    arg_list.append("-mp : Model probabilities "
            ">> {:s}\n".format(args.model_probabilities))
    arg_list.append("-ns : Number of samples to create "
            ">> {:d}\n".format(args.number_samples))
    arg_list.append("--this_is_prior : "
           "is this the prior? >> {:s}\n".format(str(args.this_is_prior)))
    arg_list.append("-nprocs : Number of simultaneous processes to run "
            ">> {:d}\n".format(args.nprocs))
    
    arg_str = ''.join(arg_list)

    return arg_str

def create_parser():
    """Create argparse instance for script.
    
    Returns
    -------
    args : agparse arg instance

    """
    desc_str = (
        """Sample machines using an existing model probabilities file."""
        )
    parser = argparse.ArgumentParser(description=desc_str)
    parser.add_argument('-db', '--database_directory',
            help = 'name of the database directory',
            type = str,
            required = True
            )
    parser.add_argument('-idir', '--inferem_directory',
            help = 'name of subdirectory with desired InferEM pickles',
            type = str,
            required = True
            )
    parser.add_argument('-mp', '--model_probabilities',
            help = 'name of the probabilities file',
            type = str,
            required = True
            )
    parser.add_argument('-ns', '--number_samples',
            help = 'number of machines to sample',
            type = int,
            required = True
            )
    parser.add_argument('--this_is_prior',
            help = 'indicate this is sampling from prior',
            action = 'store_true',
            required = False
            )
    parser.add_argument('-nprocs',
            help = 'number of simultaneous processes to run',
            type = int,
            default = 4)
    
    # do the parsing
    args = parser.parse_args()

    return args

def main():
    """Sample machines using a specified model probabilities file.
    
    """
    # parse command line
    args = create_parser()

    # get command line args and report settings
    arg_str = report_args(args)
    print arg_str

    # do the serious computing...
    if args.this_is_prior:
        # sampling from prior -- send None as data
        summary_str = sample_machines(args.database_directory,
                                      args.inferem_directory,
                                      args.model_probabilities,
                                      args.number_samples,
                                      None,
                                      args.nprocs)
    else:
        # read data
        data = read_datafile(os.path.join(args.database_directory, 'datafile'))

        # extract correct data limits from inferEM directory name
        lower_limit, upper_limit = args.inferem_directory.split('_')[1].split('-')
        ll = int(lower_limit)
        ul = int(upper_limit)

        # send data for sampling from posterior
        summary_str = sample_machines(args.database_directory,
                                      args.inferem_directory,
                                      args.model_probabilities,
                                      args.number_samples,
                                      data[ll:ul],
                                      args.nprocs)
    
    print summary_str

    # write log
    inferemdir = os.path.join(args.database_directory, args.inferem_directory)
    logfile = os.path.join(args.database_directory, 'summary.log')
    if os.path.exists(logfile):
        f = open(logfile, 'a')
    else:
        f = open(logfile, 'w')
     
    f.write('\n*** start: generating machine samples ***\n\n')
    f.write(arg_str)
    f.write('\n')
    f.write(summary_str)
    f.write('\n*** end: generating machine samples ***\n')
    f.close()
    
if __name__ == '__main__':
    main()

