"""
20-30 hand-written QA pairs from your actual PDFs.
Each entry needs: a question, the expected answer (rough, for judge reference),
and the ground-truth chunk id(s) that SHOULD be retrieved.

Why manual: you need ground truth to know if retrieval worked. Without knowing
"chunk_47 is the right chunk", you can't compute Recall@k or MRR at all —
you're just guessing whether an answer sounds right.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class QAItem:
    question: str
    expected_answer: str      # rough summary, used as reference for the judge
    relevant_chunk_ids: List[str]  # ground truth — which chunks SHOULD be retrieved


QA_DATASET: List[QAItem] = [

    # ---------- BERT paper ----------
    QAItem(
        question="What accuracy improvement did BERT achieve over the prior state of the art on average?",
        expected_answer="BERT obtained roughly 4.5% and 7.0% average accuracy improvement over the prior state of the art (BERTBASE and BERTLARGE respectively).",
        relevant_chunk_ids=["tranformer for language understanfingv2__p6__c4"],
    ),
    QAItem(
        question="How many Cloud TPUs were used to pre-train BERT, and how long did it take?",
        expected_answer="BERT was pre-trained on 16 Cloud TPUs (64 TPU chips total), taking 4 days to complete.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p13__c7"],
    ),
    QAItem(
        question="What batch size and sequence length were used during BERT's pre-training?",
        expected_answer="A batch size of 256 sequences with 512 tokens each (128,000 tokens per batch) was used for 1,000,000 steps.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p13__c5"],
    ),
    QAItem(
        question="What activation function does BERT use instead of ReLU?",
        expected_answer="BERT uses a GELU activation function rather than the standard ReLU.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p13__c6"],
    ),
    QAItem(
        question="What learning rates were tried during BERT's fine-tuning?",
        expected_answer="Learning rates of 5e-5, 3e-5, and 2e-5 were tried, along with 2, 3, and 4 epochs.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p14__c0"],
    ),
    QAItem(
        question="What is the masking strategy BERT uses during pre-training?",
        expected_answer="80% of the time the word is replaced with [MASK], with the remaining time split between keeping the word unchanged and replacing it with a random token.",
        relevant_chunk_ids=[
            "tranformer for language understanfingv2__p12__c7",
            "tranformer for language understanfingv2__p16__c6",
        ],
    ),
    QAItem(
        question="How does removing Next Sentence Prediction (NSP) affect BERT's performance on the Dev set?",
        expected_answer="Removing NSP slightly decreases accuracy across MNLI, QNLI, MRPC, SST-2, and SQuAD compared to the full BERTBASE model.",
        relevant_chunk_ids=[
            "tranformer for language understanfingv2__p8__c0",
            "tranformer for language understanfingv2__p8__c4",
        ],
    ),
    QAItem(
        question="What is the CoLA task evaluating?",
        expected_answer="CoLA (Corpus of Linguistic Acceptability) is a binary classification task predicting whether an English sentence is linguistically acceptable.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p15__c2"],
    ),
    QAItem(
        question="What is MRPC and what does it consist of?",
        expected_answer="MRPC (Microsoft Research Paraphrase Corpus) consists of sentence pairs automatically extracted from online news sources.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p15__c3"],
    ),
    QAItem(
        question="Does increasing model size continue to improve performance on large-scale tasks?",
        expected_answer="Yes, larger models lead to strict accuracy improvements across tasks, even on smaller datasets like MRPC, and this trend is expected to continue for large-scale tasks like machine translation.",
        relevant_chunk_ids=[
            "tranformer for language understanfingv2__p8__c8",
            "tranformer for language understanfingv2__p8__c10",
        ],
    ),
    QAItem(
        question="How many WordPiece tokens are masked in each sequence during BERT's pre-training?",
        expected_answer="15% of all WordPiece tokens in each sequence are masked at random.",
        relevant_chunk_ids=["tranformer for language understanfingv2__p4__c7"],
    ),
    QAItem(
        question="What two unsupervised tasks does BERT use for pre-training?",
        expected_answer="BERT is pre-trained using Masked LM (MLM) and Next Sentence Prediction (NSP).",
        relevant_chunk_ids=[
            "tranformer for language understanfingv2__p4__c4",
            "tranformer for language understanfingv2__p4__c10",
        ],
    ),

    # ---------- Attention Is All You Need (Transformer) paper ----------
    QAItem(
        question="What BLEU score did the Transformer achieve on English-to-German translation, and how long did training take?",
        expected_answer="The Transformer established a new state-of-the-art BLEU score of 41.0, after training for 3.5 days on eight GPUs.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p1__c3"],
    ),
    QAItem(
        question="How many identical layers make up the Transformer's encoder stack?",
        expected_answer="The encoder is composed of a stack of N = 6 identical layers.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p2__c10"],
    ),
    QAItem(
        question="What is the embedding/model dimension used in the base Transformer?",
        expected_answer="The model and embedding layers produce outputs of dimension dmodel = 512.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p3__c1"],
    ),
    QAItem(
        question="What optimizer and hyperparameters did the Transformer use for training?",
        expected_answer="The Adam optimizer was used with beta1 = 0.9, beta2 = 0.98, and epsilon = 10^-9, with warmup_steps = 4000.",
        relevant_chunk_ids=[
            "NIPS-2017-attention-is-all-you-need-Paper__p7__c6",
            "NIPS-2017-attention-is-all-you-need-Paper__p7__c7",
        ],
    ),
    QAItem(
        question="What dropout rate did the Transformer use for regularization?",
        expected_answer="A dropout rate of Pdrop = 0.1 was used.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p7__c8"],
    ),
    QAItem(
        question="What formula does the Transformer use for positional encoding?",
        expected_answer="Sinusoidal functions are used: PE(pos,2i) = sin(pos/10000^(2i/dmodel)) and PE(pos,2i+1) = cos(pos/10000^(2i/dmodel)).",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p6__c2"],
    ),
    QAItem(
        question="What dataset size was used for the English-French translation task?",
        expected_answer="The WMT 2014 English-French dataset was used, consisting of 36M sentences split into a 32000 word-piece vocabulary.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p7__c4"],
    ),
    QAItem(
        question="What GPU hardware was used to train the Transformer models?",
        expected_answer="Training was done on one machine with 8 NVIDIA P100 GPUs.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p7__c5"],
    ),
    QAItem(
        question="What mechanism does the Transformer rely on entirely, instead of recurrence or convolution?",
        expected_answer="The Transformer relies entirely on an attention mechanism to draw global dependencies between input and output.",
        relevant_chunk_ids=["NIPS-2017-attention-is-all-you-need-Paper__p2__c3"],
    ),

    # ---------- Cross-paper question ----------
    QAItem(
        question="How does BERT's use of the Transformer architecture differ from the original Transformer described in Attention Is All You Need?",
        expected_answer="BERT uses a bidirectional Transformer encoder (based on the original implementation), while the original Transformer paper describes a full encoder-decoder architecture used mainly for translation; BERT also uses bidirectional self-attention compared to GPT's constrained left-to-right version.",
        relevant_chunk_ids=[
            "tranformer for language understanfingv2__p3__c6",
            "tranformer for language understanfingv2__p3__c8",
            "NIPS-2017-attention-is-all-you-need-Paper__p2__c10",
        ],
    ),
]