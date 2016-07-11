#!/usr/bin/env python

# --------------------------------------------------------
# Fast R-CNN
# Copyright (c) 2016 CUHK
# Written by Wang Kun
# --------------------------------------------------------

"""Generate txt file as the input to craft::frcnn_train_data_layer"""

import cPickle
import _init_paths
from datasets.factory import get_imdb
from roi_data_layer.roidb import prepare_roidb
from roi_data_layer.roidb import add_bbox_regression_targets

imdb_name = 'coco_2014_val'
proposal_method = 'mcg'

imdb = get_imdb(imdb_name)
imdb.set_proposal_method(proposal_method)
prepare_roidb(imdb)
roidb = imdb.roidb
gt_roidb = imdb.gt_roidb()

# filter roidb
print 'filtering out images with no gt...'
assert len(roidb) == len(gt_roidb)
remove_indices = []
for i in xrange(len(gt_roidb)):
    if gt_roidb[i]['boxes'].shape[0] == 0:
        remove_indices.append(i)
roidb = [i for j, i in enumerate(roidb) if j not in remove_indices]
print '{} images are filtered'.format(len(remove_indices))

# Notice: roidb is list, you can concate two roidbs just by '+'.
# e.g. roidb = roidb_train + roidb_val

mean, std = add_bbox_regression_targets(roidb)

with open('bbox_means.pkl', 'wb') as fid1:
    cPickle.dump(mean, fid1, cPickle.HIGHEST_PROTOCOL)
with open('bbox_stds.pkl', 'wb') as fid2:
    cPickle.dump(std, fid2, cPickle.HIGHEST_PROTOCOL)

with open('rois_' + imdb_name + '.txt', 'w') as f:
    for image_index in xrange(len(roidb)):
        if image_index % 1000 == 0:
            print '{}/{}'.format(image_index, len(roidb))

        # load next item
        item = roidb[image_index]
        if item['channel'] not in (1, 3):
            print '{} has strange channels[{}]!'.format(item['image'], item['channel'])
        # image_index img_path channels height width
        f.write('# {}\n{}\n{}\n{}\n{}\n'.format(
            image_index, item['image'], item['channel'], item['height'], item['width']))
        # flipped
        f.write('{}\n'.format(0))
        # num_windows
        num_windows = item['boxes'].shape[0]
        f.write('{}\n'.format(num_windows))
        class_index = item['max_classes']
        overlap = item['max_overlaps']
        for k in xrange(num_windows):
            # class_index
            f.write('{} '.format(class_index[k]))
            # overlap
            f.write('%.2f ' % overlap[k])
            # x1 y1 x2 y2
            x1 = item['boxes'][k, 0]
            y1 = item['boxes'][k, 1]
            x2 = item['boxes'][k, 2]
            y2 = item['boxes'][k, 3]
            f.write('{} {} {} {} '.format(x1, y1, x2, y2))
            # dx dy dw dh
            dx = item['bbox_targets'][k, 1]
            dy = item['bbox_targets'][k, 2]
            dw = item['bbox_targets'][k, 3]
            dh = item['bbox_targets'][k, 4]
            f.write('%.2f %.2f %.2f %.2f\n' % (dx, dy, dw, dh))
