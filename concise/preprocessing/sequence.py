import sklearn.preprocessing
import numpy as np

# vocabularies:
DNA = ["A", "C", "G", "T"]
RNA = ["A", "C", "G", "U"]
AMINO_ACIDS = ["A", "R", "N", "D", "B", "C", "E", "Q", "Z", "G", "H",
               "I", "L", "K", "M", "F", "P", "S", "T", "W", "Y", "V"]
CODONS = ["AAA", "AAC", "AAG", "AAT", "ACA", "ACC", "ACG", "ACT", "AGA",
          "AGC", "AGG", "AGT", "ATA", "ATC", "ATG", "ATT", "CAA", "CAC",
          "CAG", "CAT", "CCA", "CCC", "CCG", "CCT", "CGA", "CGC", "CGG",
          "CGT", "CTA", "CTC", "CTG", "CTT", "GAA", "GAC", "GAG", "GAT",
          "GCA", "GCC", "GCG", "GCT", "GGA", "GGC", "GGG", "GGT", "GTA",
          "GTC", "GTG", "GTT", "TAC", "TAT", "TCA", "TCC", "TCG", "TCT",
          "TGC", "TGG", "TGT", "TTA", "TTC", "TTG", "TTT"]
STOP_CODONS = ["TAG", "TAA", "TGA"]


def _get_vocab_dict(vocab):
    return {l: i for i, l in enumerate(vocab)}


def tokenize(seq, vocab, neutral_vocab=[]):
    """Convert sequence to integers

    Arguments:
       seq: Sequence to encode
       vocab: Vocabulary to use
       neutral_vocab: Neutral vocabulary -> assign those values to -1

    Returns:4
       List of length `len(seq)` with integers from `-1` to `len(vocab) - 1`
    """
    # Req: all vocabs have the same length
    if isinstance(neutral_vocab, str):
        neutral_vocab = [neutral_vocab]

    nchar = len(vocab[0])
    for l in vocab + neutral_vocab:
        assert len(l) == nchar
    assert len(seq) % nchar == 0  # since we are using striding

    vocab_dict = _get_vocab_dict(vocab)
    for l in neutral_vocab:
        vocab_dict[l] = -1

    return [vocab_dict[seq[(i * nchar):((i + 1) * nchar)]] for i in range(len(seq) // nchar)]


def token2one_hot(tvec, vocab_size):
    """
    Note: everything out of the vucabulary is transformed to `np.zeros(vocab_size)`
    """
    lb = sklearn.preprocessing.LabelBinarizer()
    lb.fit(range(vocab_size))
    return lb.transform(tvec)


def encodeSequence(seq_vec, vocab, neutral_vocab, maxlen=None,
                   seq_align="start", pad_value="N"):
    if isinstance(neutral_vocab, str):
        neutral_vocab = [neutral_vocab]
    if isinstance(seq_vec, str):
        raise ValueError("seq_vec should be an iterable returning " +
                         "strings not a string itself")
    assert len(vocab[0]) == len(pad_value)
    assert pad_value in neutral_vocab

    seq_vec = pad_sequences(seq_vec, maxlen=maxlen,
                            align=seq_align, value=pad_value)
    seq_vec_one_hot = [token2one_hot(tokenize(seq, vocab, neutral_vocab), len(vocab))
                       for seq in seq_vec]

    return np.stack(seq_vec_one_hot)


def encodeDNA(seq_vec, maxlen=None, seq_align="start"):
    # TODO - update description
    """
    Convert the DNA sequence to 1-hot-encoding numpy array

    parameters
    ----------
    seq_vec: list of chars
        List of sequences that can have different lengths

    seq_align: character; 'end' or 'start'
        To which end should we align sequences?

    maxlen: int or None,
        Should we trim (subset) the resulting sequence. If None don't trim.
        Note that trims wrt the align parameter.
        It should be smaller than the longest sequence.

    returns
    -------
    3D numpy array of shape (len(seq_vec), trim_seq_len(or maximal sequence length if None), 4)

    Examples
    --------
    >>> sequence_vec = ['CTTACTCAGA', 'TCTTTA']
    >>> X_seq = dna_seq_list_to_1hot(sequence_vec, "end", trim_seq_len = 8)
    >>> X_seq.shape
    (2, 1, 8, 4)

    >>> print(X_seq)
    [[[[ 0.  0.  0.  1.]
       [ 1.  0.  0.  0.]
       [ 0.  1.  0.  0.]
       [ 0.  0.  0.  1.]
       [ 0.  1.  0.  0.]
       [ 1.  0.  0.  0.]
       [ 0.  0.  1.  0.]
       [ 1.  0.  0.  0.]]]


     [[[ 0.  0.  0.  0.]
       [ 0.  0.  0.  0.]
       [ 0.  0.  0.  1.]
       [ 0.  1.  0.  0.]
       [ 0.  0.  0.  1.]
       [ 0.  0.  0.  1.]
       [ 0.  0.  0.  1.]
       [ 1.  0.  0.  0.]]]]
    """
    return encodeSequence(seq_vec,
                          vocab=DNA,
                          neutral_vocab="N",
                          maxlen=maxlen,
                          seq_align=seq_align,
                          pad_value="N")


def encodeRNA(seq_vec, maxlen=None, seq_align="start"):
    return encodeSequence(seq_vec,
                          vocab=RNA,
                          neutral_vocab="N",
                          maxlen=maxlen,
                          seq_align=seq_align,
                          pad_value="N")


def encodeCodon(seq_vec, ignore_stop_codons=True, maxlen=None, seq_align="start"):
    return encodeSequence(seq_vec,
                          vocab=CODONS,
                          neutral_vocab=STOP_CODONS + ("NNN"),
                          maxlen=maxlen,
                          seq_align=seq_align,
                          pad_value="NNN")


def encodeAA(seq_vec, maxlen=None, seq_align="start"):
    return encodeSequence(seq_vec,
                          vocab=AMINO_ACIDS,
                          neutral_vocab="_",
                          maxlen=maxlen,
                          seq_align=seq_align,
                          pad_value="_")


def pad_sequences(sequence_vec, maxlen=None, align="end", value="N"):
    """
    See also: https://keras.io/preprocessing/sequence/

    1. Pad the sequence with N's or any other sequence element
    2. Subset the sequence

    Aplicable also for lists of characters

    parameters
    ----------
    sequence_vec: list of chars
        List of sequences that can have different lengths
    value:
        Neutral element to pad the sequence with
    maxlen: int or None,
        Should we trim (subset) the resulting sequence. If None don't trim.
        Note that trims wrt the align parameter.
        It should be smaller than the longest sequence.
    align: character; 'end' or 'start'
        To which end should to align the sequences.

    Returns
    -------
    List of sequences of the same class as sequence_vec

    Examples
    --------
    >>> sequence_vec = ['CTTACTCAGA', 'TCTTTA']
    >>> pad_sequences(sequence_vec, "N", 10, "start")
    """

    # neutral element type checkoing
    assert len(value) == 1
    assert isinstance(value, type(sequence_vec[0]))
    assert isinstance(value, list) or isinstance(value, str)
    assert not isinstance(sequence_vec, str)
    assert isinstance(sequence_vec[0], list) or isinstance(sequence_vec[0], str)

    max_seq_len = max([len(seq) for seq in sequence_vec])

    if maxlen is None:
        maxlen = max_seq_len
    else:
        maxlen = int(maxlen)

    if max_seq_len < maxlen:
        print("WARNING: Maximum sequence length (%s) is less than maxlen (%s)" % (max_seq_len, maxlen))
        max_seq_len = maxlen

        # pad and subset

    def pad(seq, max_seq_len, value="N", align="end"):
        seq_len = len(seq)
        assert max_seq_len >= seq_len
        if align is "end":
            n_left = max_seq_len - seq_len
            n_right = 0
        elif align is "start":
            n_right = max_seq_len - seq_len
            n_left = 0
        elif align is "center":
            n_left = (max_seq_len - seq_len) // 2 + (max_seq_len - seq_len) % 2
            n_right = (max_seq_len - seq_len) // 2
        else:
            raise ValueError("align can be of: end, start or center")
        return value * n_left + seq + value * n_right

    def trim(seq, maxlen, align="end"):
        seq_len = len(seq)

        assert maxlen <= seq_len
        if align is "end":
            return seq[-maxlen:]
        elif align is "start":
            return seq[0:maxlen]
        elif align is "center":
            dl = seq_len - maxlen
            n_left = dl // 2 + dl % 2
            n_right = seq_len - dl // 2
            return seq[n_left:-n_right]
        else:
            raise ValueError("align can be of: end, start or center")

    padded_sequence_vec = [pad(seq, max(max_seq_len, maxlen),
                               value=value, align=align) for seq in sequence_vec]
    padded_sequence_vec = [trim(seq, maxlen, align=align) for seq in padded_sequence_vec]

    return padded_sequence_vec