# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# Ω OMEGA 70B - Training Script
# Trains 70B model on farm logs and Omega personality

"""
Ω Omega 70B Training Script

Trains Meta-Llama-3.2-70B-Instruct on:
- Farm logs and data
- Omega personality and mission
- Code analysis patterns
- Farm knowledge

Uses Unsloth for efficient training with LoRA.
"""

import sys
import io
import json
import subprocess
from pathlib import Path
from typing import Optional

# Set UTF-8 encoding
if sys.platform == 'win32':
    try:
        if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.buffer.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if not hasattr(sys.stderr, 'encoding') or sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.buffer.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

OMEGA_HOME = Path.home() / 'omega_70b'
MODELS_DIR = OMEGA_HOME / 'models'
DATA_DIR = OMEGA_HOME / 'data'
OUTPUT_DIR = OMEGA_HOME / 'omega-70b-wiley'

DATASET_FILE = DATA_DIR / 'farm_logs_dataset.jsonl'
MODEL_NAME = "unsloth/Meta-Llama-3.2-70B-Instruct-bnb-4bit"


def check_dependencies():
    """Check if required dependencies are installed."""
    print("=" * 80)
    print("CHECKING DEPENDENCIES")
    print("=" * 80)
    
    required = ['torch', 'unsloth', 'transformers', 'peft', 'trl']
    missing = []
    
    for dep in required:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - MISSING")
            missing.append(dep)
    
    if missing:
        print(f"\n✗ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("\n✓ All dependencies available")
    return True


def download_model():
    """Download the base model if not present."""
    print("\n" + "=" * 80)
    print("CHECKING BASE MODEL")
    print("=" * 80)
    
    # Unsloth will handle model download automatically
    print(f"Model: {MODEL_NAME}")
    print("Unsloth will download the model automatically on first use.")
    print("This may take 30-60 minutes depending on connection speed.")
    print("Model size: ~40GB")
    
    return True


def prepare_training_script():
    """Create the training script."""
    training_script = OMEGA_HOME / 'train_omega.py'
    
    script_content = f'''# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Omega 70B Training Script (Auto-generated)

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

print("=" * 80)
print("Ω OMEGA 70B TRAINING")
print("=" * 80)

# Load model
print("\\n[1/5] Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "{MODEL_NAME}",
    max_seq_length = 8192,
    dtype = None,
    load_in_4bit = True,
)

# Enable LoRA
print("\\n[2/5] Configuring LoRA...")
model = FastLanguageModel.get_peft_model(
    model,
    r = 64,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 64,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = True,
    random_state = 3407,
)

# Load dataset
print("\\n[3/5] Loading dataset...")
dataset = load_dataset("json", data_files=r"{DATASET_FILE}", split="train")

# Training arguments
print("\\n[4/5] Configuring training...")
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = 8192,
    packing = False,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 8,
        warmup_steps = 5,
        num_train_epochs = 1,
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = r"{OUTPUT_DIR}",
        save_strategy = "epoch",
    ),
)

# Train
print("\\n[5/5] Training Omega...")
print("This will take approximately 4 hours on RTX 3050.")
print("Training started at:", __import__("datetime").datetime.now())
trainer.train()

# Save
print("\\n[Saving] Saving trained model...")
model.save_pretrained(r"{OUTPUT_DIR}")
tokenizer.save_pretrained(r"{OUTPUT_DIR}")

print("\\n" + "=" * 80)
print("✓ TRAINING COMPLETE")
print("=" * 80)
print(f"Model saved to: {OUTPUT_DIR}")
print("\\nNext: Run omega_70b_merge.py to merge and convert to GGUF")
'''
    
    training_script.write_text(script_content, encoding='utf-8')
    print(f"✓ Training script created: {training_script.name}")
    return training_script


def main():
    """Main training workflow."""
    print("=" * 80)
    print("Ω OMEGA 70B - TRAINING SETUP")
    print("=" * 80)
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ Please install missing dependencies first.")
        return
    
    # Check dataset
    if not DATASET_FILE.exists():
        print(f"\n✗ Dataset not found: {DATASET_FILE}")
        print("Please run omega_70b_prepare_dataset.py first.")
        return
    
    dataset_size = DATASET_FILE.stat().st_size / 1024 / 1024
    print(f"\n✓ Dataset found: {DATASET_FILE.name} ({dataset_size:.2f} MB)")
    
    # Download model info
    download_model()
    
    # Create training script
    print("\n" + "=" * 80)
    print("CREATING TRAINING SCRIPT")
    print("=" * 80)
    training_script = prepare_training_script()
    
    print("\n" + "=" * 80)
    print("READY TO TRAIN")
    print("=" * 80)
    print(f"\nTraining script: {training_script}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\nTo start training, run:")
    print(f"  python {training_script}")
    print(f"\nEstimated time: 4 hours on RTX 3050")
    print(f"GPU memory required: ~24GB (with 4-bit quantization)")


if __name__ == '__main__':
    main()

