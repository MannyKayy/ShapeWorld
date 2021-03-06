from models.TFMacros.tf_macros import *


def model(model, inputs, dataset_parameters, cnn_size, cnn_depth, cnn_block_depth, embedding_size, lstm_size, caption_reduction, relnet_size, relnet_depth, relnet_relreduce, relnet_reduce, mlp_size, mlp_depth, soft):

    cnn_sizes = [cnn_size * 2**n for n in range(cnn_depth)]
    cnn_depths = [cnn_block_depth for _ in range(cnn_depth)]
    relnet_sizes = [relnet_size for _ in range(relnet_depth)]
    mlp_sizes = [mlp_size for _ in range(mlp_depth)]

    world = (
        Input(name='world', shape=dataset_parameters['world_shape'], tensor=inputs.get('world')) >>
        ConvolutionalNet(sizes=cnn_sizes, depths=cnn_depths, index=True)
        # Index()
    )

    caption = (
        (
            Input(name='caption', shape=dataset_parameters['caption_shape'], dtype='int', tensor=inputs.get('caption')) >>
            Embedding(indices=dataset_parameters['vocabulary_size'], size=embedding_size),
            Input(name='caption_length', shape=(), dtype='int', tensor=inputs.get('caption_length'))
        ) >>
        Rnn(size=lstm_size, unit=Lstm)
    )

    if caption_reduction == 'state':
        caption >>= Select(index=1) >> Reduction(reduction='concat')
    else:
        caption >>= Select(index=0) >> Reduction(reduction=caption_reduction, axis=1)

    agreement = (
        (world, caption) >>
        Relational(relation_unit=Repeat(layer=Dense, sizes=relnet_sizes), axis=(1, 2), relation_reduction=relnet_relreduce, reduction=relnet_reduce) >>
        Repeat(layer=Dense, sizes=mlp_sizes) >>
        Binary(name='agreement', soft=soft, tensor=inputs.get('agreement'))
    )

    return agreement
