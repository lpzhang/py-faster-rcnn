#!/usr/bin/env python

import argparse
import sys

import numpy as np
import google.protobuf as protobuf

import _init_paths
import caffe
from caffe.proto import caffe_pb2
from fast_rcnn.config import cfg, cfg_from_file

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Train a reasoning network')
    parser.add_argument('--gpu', dest='gpu_id',
                        help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--solver', dest='solver',
                        help='solver file for training the network',
                        default=None, type=str)
    parser.add_argument('--cfg', dest='cfg_file',
                        help='optional config file', default=None, type=str)
    parser.add_argument('--rand', dest='randomize',
                        help='randomize (do not use a fixed seed)',
                        action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()

    print 'Called with args:'
    print args

    if args.cfg_file is not None:
        cfg_from_file(args.cfg_file)

    if not args.randomize:
        # fix the random seeds (numpy and caffe) for reproducibility
        np.random.seed(cfg.RNG_SEED)
        caffe.set_random_seed(cfg.RNG_SEED)

    if args.cpu_mode:
        caffe.set_mode_cpu()
    else:
        cfg.GPU_ID = args.gpu_id
        caffe.set_mode_gpu()
        caffe.set_device(args.gpu_id)

    # read solver file
    solver_param = caffe_pb2.SolverParameter()
    with open(args.solver, 'r') as f:
        protobuf.text_format.Merge(f.read(), solver_param)
    max_iter = solver_param.max_iter

    solver = caffe.SGDSolver(args.solver)
    solver.step(max_iter)
    print 'Optimization Done.'

