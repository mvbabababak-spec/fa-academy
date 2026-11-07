// ===== فا-اکدمی Service Worker v100 =====
const CACHE_NAME = 'fa-academy-v100';
const CORE_FILES = [
  './',
  './index.html',
  './data.json',
  './manifest.json',
  './manifest.json?v=2',
  './assets/icons/intelligence-180-v2.png',
  './assets/icons/intelligence-192-v2.png',
  './assets/icons/intelligence-512-v2.png',
  './assets/icons/intelligence-favicon-v2.webp',
  './sw.js',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './assets/icons/apple-touch-icon.png',
  './assets/icons/favicon-32.png',
  './assets/images/art-science-cover.webp',
  './assets/images/covers/volume-1-cover.webp',
  './assets/images/covers/volume-2-cover.webp',
  './assets/images/covers/volume-3-cover.webp',
  './assets/images/covers/volume-4-cover.webp',
  './assets/images/covers/microsoft-ai-for-beginners-cover.webp',
  './assets/images/covers/microsoft-generative-ai-for-beginners-cover.webp',
  './assets/images/covers/microsoft-ml-for-beginners-cover.webp',
  './assets/images/covers/microsoft-data-science-for-beginners-cover.webp',
  './volume-3-full-fa.md',
  './volume-4-full-fa.md',
  './assets/images/babak-ai/v3-ch01-tokenization.webp',
  './book-engineering/chapters/33-tokenization.md',
  './book-engineering/chapters/33-audit-report-fa.md',
  './book-engineering/answers/33-tokenization-fa.md',
  './book-engineering/projects/33-tokenization/README.md',
  './book-engineering/projects/33-tokenization/tokenizer_bpe.py',
  './book-engineering/projects/33-tokenization/test_tokenizer_bpe.py',
  './book-engineering/projects/33-tokenization/test_embedding_lookup.py',
  './assets/images/babak-ai/v3-ch02-attention.webp',
  './book-engineering/chapters/34-attention.md',
  './book-engineering/chapters/34-audit-report-fa.md',
  './book-engineering/answers/34-attention-fa.md',
  './book-engineering/projects/34-attention/README.md',
  './book-engineering/projects/34-attention/attention.py',
  './book-engineering/projects/34-attention/test_attention.py',
  './assets/images/babak-ai/v3-ch03-self-attention.webp',
  './book-engineering/chapters/35-self-attention.md',
  './book-engineering/chapters/35-audit-report-fa.md',
  './book-engineering/answers/35-self-attention-fa.md',
  './book-engineering/projects/35-self-attention/README.md',
  './book-engineering/projects/35-self-attention/causal_multihead.py',
  './book-engineering/projects/35-self-attention/test_causal_multihead.py',
  './assets/images/babak-ai/v3-ch04-position-block.webp',
  './book-engineering/chapters/36-position-normalization.md',
  './book-engineering/chapters/36-audit-report-fa.md',
  './book-engineering/answers/36-position-normalization-fa.md',
  './book-engineering/projects/36-position-normalization/README.md',
  './book-engineering/projects/36-position-normalization/transformer_block.py',
  './book-engineering/projects/36-position-normalization/test_transformer_block.py',
  './assets/images/babak-ai/v3-ch05-architecture-matrix.webp',
  './book-engineering/chapters/37-encoder-decoder.md',
  './book-engineering/chapters/37-audit-report-fa.md',
  './book-engineering/answers/37-encoder-decoder-fa.md',
  './book-engineering/projects/37-encoder-decoder/README.md',
  './book-engineering/projects/37-encoder-decoder/transformer_architectures.py',
  './book-engineering/projects/37-encoder-decoder/test_transformer_architectures.py',
  './assets/images/babak-ai/v3-ch06-efficiency-map.webp',
  './book-engineering/chapters/38-long-context.md',
  './book-engineering/chapters/38-audit-report-fa.md',
  './book-engineering/answers/38-long-context-fa.md',
  './book-engineering/projects/38-long-context/README.md',
  './book-engineering/projects/38-long-context/efficient_attention.py',
  './book-engineering/projects/38-long-context/test_efficient_attention.py',
  './assets/images/babak-ai/v3-ch07-multimodal-bridge.webp',
  './book-engineering/chapters/39-multimodal-transformer.md',
  './book-engineering/chapters/39-audit-report-fa.md',
  './book-engineering/answers/39-multimodal-transformer-fa.md',
  './book-engineering/projects/39-multimodal-transformer/README.md',
  './book-engineering/projects/39-multimodal-transformer/multimodal_alignment.py',
  './book-engineering/projects/39-multimodal-transformer/test_multimodal_alignment.py',
  './assets/images/babak-ai/v3-ch08-data-pipeline.webp',
  './book-engineering/chapters/40-small-data-project.md',
  './book-engineering/chapters/40-audit-report-fa.md',
  './book-engineering/answers/40-small-data-project-fa.md',
  './book-engineering/projects/40-small-data-project/README.md',
  './book-engineering/projects/40-small-data-project/small_corpus.py',
  './book-engineering/projects/40-small-data-project/test_small_corpus.py',
  './book-engineering/projects/40-small-data-project/sample_corpus.jsonl',
  './assets/images/babak-ai/v3-ch09-training-loop.webp',
  './book-engineering/chapters/41-first-language-model.md',
  './book-engineering/chapters/41-audit-report-fa.md',
  './book-engineering/answers/41-first-language-model-fa.md',
  './book-engineering/projects/41-first-language-model/README.md',
  './book-engineering/projects/41-first-language-model/tiny_lm.py',
  './book-engineering/projects/41-first-language-model/test_tiny_lm.py',
  './book-engineering/create_v3_ch09_image.py',
  './book-engineering/diagrams/v3-ch09-training-loop.svg',
  './assets/images/babak-ai/v3-ch10-mini-gpt-budget.webp',
  './book-engineering/chapters/42-mini-gpt.md',
  './book-engineering/chapters/42-audit-report-fa.md',
  './book-engineering/answers/42-mini-gpt-fa.md',
  './book-engineering/projects/42-mini-gpt-design/README.md',
  './book-engineering/projects/42-mini-gpt-design/mini_gpt_design.py',
  './book-engineering/projects/42-mini-gpt-design/test_mini_gpt_design.py',
  './book-engineering/create_v3_ch10_image.py',
  './book-engineering/diagrams/v3-ch10-mini-gpt-budget.svg',
  './assets/images/babak-ai/v3-ch11-corpus-audit.webp',
  './book-engineering/chapters/43-corpus.md',
  './book-engineering/chapters/43-audit-report-fa.md',
  './book-engineering/answers/43-corpus-fa.md',
  './book-engineering/projects/43-corpus-audit/README.md',
  './book-engineering/projects/43-corpus-audit/corpus_audit.py',
  './book-engineering/projects/43-corpus-audit/test_corpus_audit.py',
  './book-engineering/projects/43-corpus-audit/sample_corpus.jsonl',
  './book-engineering/projects/43-corpus-audit/sample_evaluation.jsonl',
  './book-engineering/create_v3_ch11_image.py',
  './book-engineering/diagrams/v3-ch11-corpus-audit.svg',
  './assets/images/babak-ai/v3-ch12-pretraining.webp',
  './book-engineering/chapters/44-pretraining.md',
  './book-engineering/chapters/44-audit-report-fa.md',
  './book-engineering/answers/44-pretraining-fa.md',
  './book-engineering/projects/44-pretraining/README.md',
  './book-engineering/projects/44-pretraining/pretraining_run.py',
  './book-engineering/projects/44-pretraining/test_pretraining_run.py',
  './book-engineering/create_v3_ch12_image.py',
  './book-engineering/diagrams/v3-ch12-pretraining.svg',
  './assets/images/babak-ai/v3-ch13-precision.webp',
  './book-engineering/chapters/45-precision.md',
  './book-engineering/chapters/45-audit-report-fa.md',
  './book-engineering/answers/45-precision-fa.md',
  './book-engineering/projects/45-precision/README.md',
  './book-engineering/projects/45-precision/precision_lab.py',
  './book-engineering/projects/45-precision/test_precision_lab.py',
  './book-engineering/create_v3_ch13_image.py',
  './book-engineering/diagrams/v3-ch13-precision.svg',
  './assets/images/babak-ai/v3-ch14-scale-training.webp',
  './book-engineering/chapters/46-scale-training.md',
  './book-engineering/chapters/46-audit-report-fa.md',
  './book-engineering/answers/46-scale-training-fa.md',
  './book-engineering/projects/46-scale-training/README.md',
  './book-engineering/projects/46-scale-training/scaling_lab.py',
  './book-engineering/projects/46-scale-training/test_scaling_lab.py',
  './book-engineering/create_v3_ch14_image.py',
  './book-engineering/diagrams/v3-ch14-scale-training.svg',
  './book-engineering/diagrams/v4-ch01-posttraining.svg',
  './book-engineering/chapters/47-posttraining.md',
  './book-engineering/chapters/47-audit-report-fa.md',
  './book-engineering/answers/47-posttraining-fa.md',
  './book-engineering/projects/47-instruction-tuning/README.md',
  './book-engineering/projects/47-instruction-tuning/sft_experiment.py',
  './book-engineering/projects/47-instruction-tuning/test_sft_experiment.py',
  './book-engineering/projects/47-instruction-tuning/sample_sft.jsonl',
  './book-engineering/projects/47-instruction-tuning/requirements-model-demo.txt',
  './book-engineering/diagrams/v4-ch02-peft.svg',
  './book-engineering/chapters/48-peft.md',
  './book-engineering/chapters/48-audit-report-fa.md',
  './book-engineering/answers/48-peft-fa.md',
  './book-engineering/projects/48-peft-lab/README.md',
  './book-engineering/projects/48-peft-lab/peft_lab.py',
  './book-engineering/projects/48-peft-lab/test_peft_lab.py',
  './book-engineering/projects/48-peft-lab/sample_layers.json',
  './book-engineering/diagrams/v4-ch03-preference.svg',
  './book-engineering/chapters/49-preference-optimization.md',
  './book-engineering/chapters/49-audit-report-fa.md',
  './book-engineering/answers/49-preference-optimization-fa.md',
  './book-engineering/projects/49-preference-lab/README.md',
  './book-engineering/projects/49-preference-lab/preference_lab.py',
  './book-engineering/projects/49-preference-lab/test_preference_lab.py',
  './book-engineering/projects/49-preference-lab/sample_preferences.jsonl',
  './book-engineering/projects/49-preference-lab/results.json',
  './book-engineering/diagrams/v4-ch04-synthetic-reasoning.svg',
  './book-engineering/chapters/50-synthetic-reasoning.md',
  './book-engineering/chapters/50-audit-report-fa.md',
  './book-engineering/answers/50-synthetic-reasoning-fa.md',
  './book-engineering/projects/50-synthetic-reasoning/README.md',
  './book-engineering/projects/50-synthetic-reasoning/reasoning_lab.py',
  './book-engineering/projects/50-synthetic-reasoning/test_reasoning_lab.py',
  './book-engineering/projects/50-synthetic-reasoning/sample_traces.jsonl',
  './book-engineering/projects/50-synthetic-reasoning/results.json',
  './book-engineering/diagrams/v4-ch05-vision.svg',
  './book-engineering/chapters/51-vision-models.md',
  './book-engineering/chapters/51-audit-report-fa.md',
  './book-engineering/answers/51-vision-models-fa.md',
  './book-engineering/projects/51-vision-lab/README.md',
  './book-engineering/projects/51-vision-lab/vision_lab.py',
  './book-engineering/projects/51-vision-lab/test_vision_lab.py',
  './book-engineering/projects/51-vision-lab/sample_embeddings.json',
  './book-engineering/projects/51-vision-lab/results.json',
  './book-engineering/diagrams/v4-ch06-audio.svg',
  './book-engineering/chapters/52-audio-models.md',
  './book-engineering/chapters/52-audit-report-fa.md',
  './book-engineering/answers/52-audio-models-fa.md',
  './book-engineering/projects/52-audio-lab/README.md',
  './book-engineering/projects/52-audio-lab/audio_lab.py',
  './book-engineering/projects/52-audio-lab/test_audio_lab.py',
  './book-engineering/projects/52-audio-lab/sample_transcripts.json',
  './book-engineering/projects/52-audio-lab/results.json',
  './book-engineering/diagrams/v4-ch07-diffusion.svg',
  './book-engineering/chapters/53-image-video-generation.md',
  './book-engineering/chapters/53-audit-report-fa.md',
  './book-engineering/answers/53-image-video-generation-fa.md',
  './book-engineering/projects/53-diffusion-lab/README.md',
  './book-engineering/projects/53-diffusion-lab/diffusion_lab.py',
  './book-engineering/projects/53-diffusion-lab/test_diffusion_lab.py',
  './book-engineering/projects/53-diffusion-lab/sample_mixture.json',
  './book-engineering/projects/53-diffusion-lab/results.json',
  './book-engineering/diagrams/v4-ch08-resource-estimation.svg',
  './book-engineering/chapters/54-resource-estimation.md',
  './book-engineering/chapters/54-audit-report-fa.md',
  './book-engineering/answers/54-resource-estimation-fa.md',
  './book-engineering/projects/54-resource-estimation/README.md',
  './book-engineering/projects/54-resource-estimation/resource_estimator.py',
  './book-engineering/projects/54-resource-estimation/test_resource_estimator.py',
  './book-engineering/projects/54-resource-estimation/sample_profiles.json',
  './book-engineering/projects/54-resource-estimation/results.json',
  './book-engineering/diagrams/v4-ch09-lab-design.svg',
  './book-engineering/chapters/55-ai-lab-design.md',
  './book-engineering/chapters/55-audit-report-fa.md',
  './book-engineering/answers/55-ai-lab-design.md',
  './book-engineering/projects/55-ai-lab-design/README.md',
  './book-engineering/projects/55-ai-lab-design/lab_design_planner.py',
  './book-engineering/projects/55-ai-lab-design/test_lab_design_planner.py',
  './book-engineering/projects/55-ai-lab-design/sample_labs.json',
  './book-engineering/projects/55-ai-lab-design/results.json',
  './assets/images/babak-ai/v2-ch07-backprop.webp',
  './assets/images/babak-ai/v2-ch10-cnn.webp',
  './assets/images/babak-ai/v2-ch11-representations.webp',
  './book-engineering/answers/31-cnn-sequences-fa.md',
  './book-engineering/answers/32-representations-fa.md',
  './assets/images/babak-ai/v2-ch08-optimizers.webp',
  './assets/images/babak-ai/v2-ch09-network.webp',
  './book-engineering/answers/28-backprop-fa.md',
  './book-engineering/answers/29-optimizers-fa.md',
  './book-engineering/answers/30-neural-network-fa.md',
  './assets/images/babak-ai/v2-ch04-unsupervised.webp',
  './assets/images/babak-ai/v2-ch05-validation.webp',
  './assets/images/babak-ai/v2-ch06-mlp.webp',
  './book-engineering/answers/25-unsupervised-fa.md',
  './book-engineering/answers/26-validation-fa.md',
  './book-engineering/answers/27-perceptron-mlp-fa.md',
  './assets/images/babak-ai/v2-ch01-split.webp',
  './assets/images/babak-ai/v2-ch02-regression.webp',
  './assets/images/babak-ai/v2-ch03-cross-validation.webp',
  './book-engineering/answers/22-learning-paradigms-fa.md',
  './book-engineering/answers/23-regression-fa.md',
  './book-engineering/answers/24-classical-models-fa.md',
  './book-engineering/LEARNING_PATH_FA.md',
  './book-engineering/answers/01-intelligence-answers-fa.md',
  './book-engineering/answers/21-information-theory-answers-fa.md',
  './book-engineering/answers/20-optimization-answers-fa.md',
  './book-engineering/answers/19-probability-statistics-answers-fa.md',
  './book-engineering/answers/18-calculus-answers-fa.md',
  './book-engineering/answers/17-linear-algebra-answers-fa.md',
  './book-engineering/answers/16-algebra-functions-answers-fa.md',
  './book-engineering/answers/15-data-analysis-answers-fa.md',
  './book-engineering/answers/14-debug-testing-sql-security-answers-fa.md',
  './book-engineering/answers/13-linux-git-environments-answers-fa.md',
  './book-engineering/answers/12-classes-files-json-api-answers-fa.md',
  './book-engineering/answers/11-functions-data-structures-answers-fa.md',
  './book-engineering/answers/10-python-basics-answers-fa.md',
  './book-engineering/answers/09-first-program-answers-fa.md',
  './book-engineering/answers/02-ai-families-answers-fa.md',
  './book-engineering/answers/03-model-lifecycle-answers-fa.md',
  './book-engineering/answers/04-history-answers-fa.md',
  './book-engineering/answers/05-computer-foundations-answers-fa.md',
  './book-engineering/answers/06-gpu-parallelism-answers-fa.md',
  './book-engineering/answers/07-compute-ecosystems-answers-fa.md',
  './book-engineering/answers/08-distributed-infrastructure-answers-fa.md',
  './assets/images/babak-ai/ch02-families.webp',
  './assets/images/babak-ai/ch02-token-cycle.webp',
  './assets/images/babak-ai/ch03-lifecycle.webp',
  './assets/images/babak-ai/ch03-splits.webp',
  './assets/images/babak-ai/ch04-timeline.webp',
  './assets/images/babak-ai/ch05-data-path.webp',
  './assets/images/babak-ai/ch05-capacity.webp',
  './assets/images/babak-ai/ch06-parallel.webp',
  './assets/images/babak-ai/ch07-stack.webp',
  './assets/images/babak-ai/ch07-selection.webp',
  './assets/images/babak-ai/ch08-distributed.webp',
  './assets/images/babak-ai/ch09-flow.webp',
  './assets/images/babak-ai/ch10-condition.webp',
  './assets/images/babak-ai/ch11-function.webp',
  './assets/images/babak-ai/ch12-object.webp',
  './assets/images/babak-ai/ch13-git.webp',
  './assets/images/babak-ai/ch14-tests.webp',
  './assets/images/babak-ai/ch15-study-chart.webp',
  './assets/images/babak-ai/ch16-graph.webp',
  './assets/images/babak-ai/ch14-testing.webp',
  './assets/images/babak-ai/ch15-study.webp',
  './assets/images/babak-ai/ch16-linear.webp',
  './assets/images/babak-ai/ch17-matrix.webp',
  './assets/images/babak-ai/ch18-derivative.webp',
  './assets/images/babak-ai/ch19-bayes.webp',
  './assets/images/babak-ai/ch20-descent.webp',
  './assets/images/babak-ai/ch21-entropy.webp',
  './assets/images/babak-ai/v4-ch10-tco-timeline.svg',
  './book-engineering/chapters/56-ai-compute-budget.md',
  './book-engineering/chapters/56-audit-report-fa.md',
  './book-engineering/answers/56-ai-compute-budget-fa.md',
  './book-engineering/projects/56-ai-compute-budget/README.md',
  './book-engineering/projects/56-ai-compute-budget/budget_model.py',
  './book-engineering/projects/56-ai-compute-budget/test_budget_model.py',
  './book-engineering/projects/56-ai-compute-budget/sample_budget.json',
  './book-engineering/projects/56-ai-compute-budget/results.json',
  './book-engineering/diagrams/v4-ch11-framework-selection.svg',
  './book-engineering/chapters/57-ml-frameworks.md',
  './book-engineering/chapters/57-audit-report-fa.md',
  './book-engineering/answers/57-ml-frameworks-fa.md',
  './book-engineering/projects/57-framework-lab/README.md',
  './book-engineering/projects/57-framework-lab/framework_compare.py',
  './book-engineering/projects/57-framework-lab/test_framework_compare.py',
  './book-engineering/projects/57-framework-lab/sample_problem.json',
  './book-engineering/projects/57-framework-lab/results.json',
  './book-engineering/diagrams/v4-ch12-huggingface-stack.svg',
  './book-engineering/chapters/58-huggingface-stack.md',
  './book-engineering/chapters/58-audit-report-fa.md',
  './book-engineering/answers/58-huggingface-stack-fa.md',
  './book-engineering/projects/58-huggingface-stack/README.md',
  './book-engineering/projects/58-huggingface-stack/pipeline_demo.py',
  './book-engineering/projects/58-huggingface-stack/test_pipeline_demo.py',
  './book-engineering/projects/58-huggingface-stack/sample_data.jsonl',
  './book-engineering/projects/58-huggingface-stack/fixture_manifest.json',
  './book-engineering/projects/58-huggingface-stack/environment.json',
  './book-engineering/projects/58-huggingface-stack/results.json',
  './book-engineering/projects/58-huggingface-stack/requirements.txt',
  './book-engineering/projects/58-huggingface-stack/requirements-cpu.txt',
  './book-engineering/projects/58-huggingface-stack/requirements-lock-linux-py313.txt',
  './book-engineering/diagrams/v4-ch13-gpu-systems.svg',
  './book-engineering/chapters/59-gpu-systems.md',
  './book-engineering/chapters/59-audit-report-fa.md',
  './book-engineering/answers/59-gpu-systems-fa.md',
  './book-engineering/projects/59-gpu-systems/README.md',
  './book-engineering/projects/59-gpu-systems/gpu_systems_demo.py',
  './book-engineering/projects/59-gpu-systems/test_gpu_systems_demo.py',
  './book-engineering/projects/59-gpu-systems/sample_layout.json',
  './book-engineering/projects/59-gpu-systems/fixture_manifest.json',
  './book-engineering/projects/59-gpu-systems/environment.json',
  './book-engineering/projects/59-gpu-systems/results.json',
  './book-engineering/projects/59-gpu-systems/requirements.txt',
  './book-engineering/projects/59-gpu-systems/requirements-cpu.txt',
  './book-engineering/projects/59-gpu-systems/requirements-lock-linux-py313.txt',
  './book-engineering/diagrams/v4-ch14-mlops.svg',
  './book-engineering/chapters/60-mlops.md',
  './book-engineering/chapters/60-audit-report-fa.md',
  './book-engineering/answers/60-mlops-fa.md',
  './book-engineering/projects/60-mlops/README.md',
  './book-engineering/projects/60-mlops/experiment_ops.py',
  './book-engineering/projects/60-mlops/test_experiment_ops.py',
  './book-engineering/projects/60-mlops/sample_experiment.json',
  './book-engineering/projects/60-mlops/fixture_manifest.json',
  './book-engineering/projects/60-mlops/environment.json',
  './book-engineering/projects/60-mlops/results.json',
  './book-engineering/projects/60-mlops/requirements.txt',
  './book-engineering/projects/60-mlops/requirements-cpu.txt',
  './book-engineering/projects/60-mlops/requirements-lock-linux-py313.txt',
  './book-engineering/projects/60-mlops/Dockerfile',
  './book-engineering/projects/60-mlops/job.yaml',
  './book-engineering/diagrams/v4-ch15-inference-serving.svg',
  './book-engineering/chapters/61-inference-serving.md',
  './book-engineering/chapters/61-audit-report-fa.md',
  './book-engineering/answers/61-inference-serving-fa.md',
  './book-engineering/projects/61-inference-serving/README.md',
  './book-engineering/projects/61-inference-serving/inference_lab.py',
  './book-engineering/projects/61-inference-serving/test_inference_lab.py',
  './book-engineering/projects/61-inference-serving/sample_trace.json',
  './book-engineering/projects/61-inference-serving/fixture_manifest.json',
  './book-engineering/projects/61-inference-serving/environment.json',
  './book-engineering/projects/61-inference-serving/results.json',
  './assets/images/covers/volume-5-cover.svg',
  './volume-5-full-fa.md',
  './book-engineering/chapters/62-benchmarking-evaluation.md',
  './book-engineering/chapters/62-audit-report-fa.md',
  './book-engineering/diagrams/v5-ch01-evaluation-protocol.svg',
  './book-engineering/answers/62-benchmarking-evaluation-fa.md',
  './book-engineering/projects/62-evaluation-lab/README.md',
  './book-engineering/projects/62-evaluation-lab/environment.json',
  './book-engineering/projects/62-evaluation-lab/evaluation_lab.py',
  './book-engineering/projects/62-evaluation-lab/human_votes_fixture.json',
  './book-engineering/projects/62-evaluation-lab/requirements.txt',
  './book-engineering/projects/62-evaluation-lab/results.json',
  './book-engineering/projects/62-evaluation-lab/sample_evaluation.jsonl',
  './book-engineering/projects/62-evaluation-lab/test_evaluation_lab.py',
  './book-engineering/projects/62-evaluation-lab/training_corpus_fixture.txt',
  './book-engineering/chapters/63-hallucination-bias-robustness.md',
  './book-engineering/chapters/63-audit-report-fa.md',
  './book-engineering/diagrams/v5-ch02-behavior-audit.svg',
  './book-engineering/answers/63-hallucination-bias-robustness-fa.md',
  './book-engineering/projects/63-model-behavior-lab/README.md',
  './book-engineering/projects/63-model-behavior-lab/environment.json',
  './book-engineering/projects/63-model-behavior-lab/fixture_manifest.json',
  './book-engineering/projects/63-model-behavior-lab/model_behavior_lab.py',
  './book-engineering/projects/63-model-behavior-lab/requirements.txt',
  './book-engineering/projects/63-model-behavior-lab/results.json',
  './book-engineering/projects/63-model-behavior-lab/synthetic_behavior_fixture.json',
  './book-engineering/projects/63-model-behavior-lab/test_model_behavior_lab.py',
  './assets/images/covers/volume-5-cover.png',
  './book-engineering/chapters/64-red-teaming-security.md',
  './book-engineering/chapters/64-audit-report-fa.md',
  './book-engineering/diagrams/v5-ch03-red-team-pipeline.svg',
  './book-engineering/answers/64-red-teaming-security-fa.md',
  './book-engineering/projects/64-red-team-lab/README.md',
  './book-engineering/projects/64-red-team-lab/environment.json',
  './book-engineering/projects/64-red-team-lab/fixture_manifest.json',
  './book-engineering/projects/64-red-team-lab/red_team_lab.py',
  './book-engineering/projects/64-red-team-lab/requirements.txt',
  './book-engineering/projects/64-red-team-lab/results.json',
  './book-engineering/projects/64-red-team-lab/synthetic_security_fixture.json',
  './book-engineering/projects/64-red-team-lab/test_red_team_lab.py',
];

// ===== INSTALL: Cache core files =====
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        // Keep the previous worker active if the offline shell cannot be cached.
        return cache.addAll(['./', './index.html', './data.json']).then(function() {
          return Promise.allSettled(CORE_FILES.slice(3).map(function(url) {
            return cache.add(url).catch(function(err) { console.warn('Failed to cache:', url, err); });
          }));
        });
      })
      .then(function() {
        return self.skipWaiting();
      })
  );
});

// ===== ACTIVATE: Clean old caches =====
self.addEventListener('activate', function(event) {
  var cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.map(function(key) {
          if (key.indexOf('fa-academy-') === 0 && cacheWhitelist.indexOf(key) === -1) {
            return caches.delete(key);
          }
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// ===== FETCH: Network-first for HTML/data, cache-first for assets =====
self.addEventListener('fetch', function(event) {
  var url = new URL(event.request.url);

  if (event.request.method !== 'GET') return;
  if (url.origin !== self.location.origin) return;

  // ===== Network-first for HTML, data.json, and navigation =====
  // Use endsWith to handle subdirectory deployments (e.g. /fa-academy/)
  if (event.request.mode === 'navigate' ||
      url.pathname.endsWith('/data.json') ||
      url.pathname.endsWith('/index.html')) {

    event.respondWith(
      fetch(event.request)
        .then(function(response) {
          if (response.ok) {
            var responseClone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        })
        .catch(function(err) {
          return caches.match(event.request, {ignoreSearch:true}).then(function(cached) {
            if (cached) return cached;
            if (url.pathname.endsWith('/data.json')) return caches.match('./data.json');
            if (event.request.mode === 'navigate') {
              return caches.match('./index.html').then(function(r) {
                if (r) return r;
                return new Response('Offline - please check your connection', {
                  status: 503,
                  statusText: 'Offline',
                  headers: {'Content-Type': 'text/plain'}
                });
              });
            }
            return new Response('Offline', {status: 503, statusText: 'Offline'});
          });
        })
    );
    return;
  }

  // ===== Cache-first for static assets =====
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        if (response.ok) {
          var responseClone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      }).catch(function() {
        return new Response('Resource not available offline', {
          status: 404,
          statusText: 'Not Found'
        });
      });
    })
  );
});

// ===== MESSAGE: Trigger update =====
self.addEventListener('message', function(event) {
  if (event.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
