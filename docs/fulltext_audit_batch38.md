# Full-text audit batch 38: “foundation models” covers several different questions

Updated 2026-10-12. This batch reviews all nine previously unread uniform-random records in the `foundation_models` topic-period cells. Each record was checked against arXiv full text, including PDFs where HTML was unavailable. One independent retrieval benchmark was added as a citation follow-up. These are not nine replications of one method: the bucket spans speech recognition, social-media classification, knowledge injection, customer-service economics, in-context learning, reasoning, organizational analysis, education, and translation.

## Nine sampled records

### 1. Large Scale Language Modeling in Automatic Speech Recognition (arXiv:1210.8440v1; 2012)

[Full text](https://arxiv.org/pdf/1210.8440).

This is an industrial ASR study of large n-gram statistical language models, not a modern neural foundation-model evaluation. Google Voice Search experiments used 230 billion query words; on YouTube, lattice rescoring with large web-trained language models reduced word error rate by 6–10% relatively in the tested systems. It illustrates why outcome, integration, and compute matter: a model-size claim is inseparable from the acoustic model, rescoring pipeline, training data, and operating point. Internal production data also limit independent replication.

### 2. Neural DrugNet (arXiv:1809.01500v1; 2018)

[Full text](https://arxiv.org/pdf/1809.01500).

This shared-task entry ensembles a Wikipedia-pretrained word LSTM with a character-trigram LSTM to classify medication mentions in social-media posts. It ranked second in one shared task. Its reported Task 2 test F1 is 0.505, while Task 4 test F1 is 0.859; the authors acknowledge using accuracy during development for Task 2 before reporting test F1. This is a small task-specific application result, not general evidence about foundation models.

### 3. Teaching Pretrained Models with Commonsense Reasoning: A Preliminary KB-Based Approach (arXiv:1909.09743v2; 2019)

[Full text](https://arxiv.org/pdf/1909.09743).

The authors convert ConceptNet relations into synthetic multiple-choice questions, refine BERT/GPT/XLNet, and then fine-tune on downstream commonsense tasks. On CommonsenseQA with 100 training examples, their refinement improves BERT from 34.94% to 42.54% and XLNet from 25.04% to 43.60% accuracy; reported numbers average five runs. With all fine-tuning data the gains are smaller (about two points). This is a positive, bounded result for that synthetic data construction and older model family; it does not establish that structured knowledge injection generally helps contemporary LLMs.

### 4. The Economic Trade-offs of Large Language Models: A Case Study (arXiv:2306.07402v1; 2023)

[Full text](https://arxiv.org/html/2306.07402).

This paper measures response usefulness using actual customer-service agent ratings for one retail brand, then combines use/edit/ignore probabilities with inference and labor costs in an expected-net-savings calculation. The study reports that a distilled GPT-2 setup can beat GPT-3 economically for this brand despite lower response quality, because serving costs differ. Its central limit is also explicit: human usefulness ratings come from one brand, and some model configurations' usefulness estimates are extrapolated from perplexity because they were not manually rated. The historical cost figures are time-sensitive and should not be reused as present-day prices.

### 5. Why Does In-Context Learning Fail Sometimes? (arXiv:2407.02028v1; 2024)

[Full text](https://arxiv.org/html/2407.02028).

This is the strongest cross-paper signal in this batch. The authors evaluate GPT-4 (gpt-4-1106-preview) on 160 open physics/computer-science questions, with six graders rating correctness/completeness, logic, and truthfulness. In this set, the aggregate score is highest with no added context and lowest with the most relevant context. They then use the same model and evaluation framework on two closed-form sets (MetaICL and NephSAP): similarity between a demonstration and question is positively associated with improvement there, but negatively associated for their open-form set. This is a useful within-paper contrast, but the open set is small, hand-constructed, English-only, and graded; the paper itself notes noisy grader-level trends. It is not evidence that relevant context generally hurts RAG.

### 6. Exploring the Role of Reasoning Structures for Constructing Proofs in Multi-Step Natural Language Reasoning (arXiv:2410.08436v2; 2024)

[Full text](https://arxiv.org/html/2410.08436).

This work constructs explicit proof graphs and compares them with CoT, self-consistency, Tree-of-Thought, and reasoning-via-planning on EntailmentBank, AR-LSAT, and PrOntoQA using GPT-3.5, GPT-4, Llama-2-70B, and Llama-3-70B. The authors report higher evidence/proof F1 and graph-similarity scores in their experiments, with paired-test significance claims. The stated scope is English natural-language proof tasks; math reasoning and other languages were not tested, and the branching process has substantial token/API cost. The result is narrower than a general “structured reasoning works” claim.

### 7. From Model Design to Organizational Design: Complexity Redistribution and Trade-Offs in Generative AI (arXiv:2506.22440v2; 2025)

[Full text](https://arxiv.org/html/2506.22440).

This is a conceptual framework and synthesis that adapts a generality–accuracy–simplicity trade-off to organizational choices. It brings in outside field studies and examples, but the GAS framework itself is not tested as one controlled intervention in this paper. It can generate hypotheses about who bears verification, infrastructure, and compliance costs; it should not be counted as a direct experimental estimate of productivity or LLM accuracy.

### 8. K12-KGraph: A Curriculum-Aligned Knowledge Graph for Benchmarking and Training Educational LLMs (arXiv:2605.09635v4; 2026)

[Full text](https://arxiv.org/html/2605.09635).

This study constructs a knowledge graph and benchmark from official Chinese K–12 textbooks, with 12 subject-qualified annotators, reported Fleiss’ κ=0.84, and a 98.4% correctness rate in a stratified benchmark spot-check. It reports that a strong open model obtains 46% exact match on its curriculum-cognition benchmark. In its training experiments, a roughly 2,300-example curriculum-grounded set beats equally sized general instruction-data subsets on specified educational tests, while multimodal supervision adds gains on its three educational multimodal benchmarks. These are substantial task-specific results; they do not automatically transfer outside Chinese curriculum content, the evaluated models, or the paper's benchmark construction.

### 9. Fluency and Faithfulness in Human and Machine Literary Translation (arXiv:2605.15282v1; 2026)

[Full text](https://arxiv.org/pdf/2605.15282).

The authors analyze 130,486 aligned paragraphs from 106 novels and 16 source languages, comparing human, Google Translate, and TranslateGemma translations. Fluency is operationalized as POS-based “original-likeness”; faithfulness uses COMET-KIWI. The raw association is small (Spearman ρ=-0.0374); after controlling for length it is still modest (partial ρ=-0.0827), and varies by translation source, with TranslateGemma near zero/slightly positive in the reported analysis. This is not a general theorem that fluent output is unfaithful. The authors flag incomplete translator/date metadata and the narrow syntactic definition of fluency; COMET-KIWI is an automatic adequacy score, not human judgment.

## Independent evidence on the context-relevance result

The 2024 BRIGHT benchmark studies a different but related problem: retrieving documents whose usefulness depends on underlying reasoning rather than surface similarity. It includes 1,384 queries across domains and reports poor baseline retrieval; reasoning-aware retrieval improves scores, and the retrieved documents help downstream question answering, although oracle documents help more. This is not a direct replication of the 160-question open/closed ICL experiment, but it is important counterevidence against the broad interpretation that topical relevance is harmful. It instead supports a more precise distinction: shallow semantic similarity and genuinely useful evidence are not the same thing. [BRIGHT full text](https://arxiv.org/html/2407.12883)

## Bounded synthesis and testable follow-up

Across the 160-item open-question set in the ICL paper and its same-model closed-form replication, context similarity changed direction with question format. BRIGHT independently shows that reasoning-relevant documents can improve answer quality, while stronger/oracle retrieval gives larger gains. So the supported statement is conditional: the benefit of supplied context depends on the task and on whether retrieval captures reasoning-relevant evidence, not just topic overlap. That is a credible candidate for further study, but it is not yet a field-level novelty claim.

**Falsifiable follow-up:** On multiple open-ended scientific QA and closed-form QA datasets, keep the answering model fixed and compare no context, topic-similar distractors, semantically similar but non-supporting passages, reasoning-relevant examples, and gold evidence. Randomize context order, use multiple model families and repeated generations, and have blinded human graders score answer correctness, reasoning validity, and unsupported claims. Test interactions with novelty/difficulty and report retrieval cost. The claim that question format changes context utility is weakened if the direction of the relevant-context effect is stable across question formats, model families, and independent datasets after passage quality is held constant.

## Audit boundary

The nine-paper random draw is now complete, but it remains heterogeneous and cannot support a single aggregate “foundation model” effect. The context result is based on a small custom open-question set; BRIGHT is a related retrieval study, not a direct replication. The 198,690-record pool is still only a candidate frame, and audit counts are not corpus prevalence estimates.
