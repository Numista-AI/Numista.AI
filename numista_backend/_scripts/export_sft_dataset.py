"""
CLI Tool: Offline Supervised Fine-Tuning (SFT) Dataset Exporter
Inspects dataset readiness, verifies quality gates, and exports Gemini JSONL manifests.
Usage:
  python _scripts/export_sft_dataset.py --dry-run
  python _scripts/export_sft_dataset.py --out-dir ./data/sft_export
"""

import os
import sys
import json
import argparse
import logging

# Add parent directory to path for service imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.training_export_service import TrainingExportService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_sft_dataset")


def main():
    parser = argparse.ArgumentParser(description="Numista.AI Offline SFT Dataset Exporter")
    parser.add_argument("--dry-run", action="store_true", help="Inspect readiness and metrics without writing files")
    parser.add_argument("--out-dir", default="./data/sft_export", help="Output directory for generated JSONL splits")
    parser.add_argument("--min-count", type=int, default=10, help="Minimum record threshold for validation")
    args = parser.parse_args()

    logger.info("Initializing SFT Dataset Exporter...")
    service = TrainingExportService()
    records = service.load_verified_records()

    logger.info(f"Loaded {len(records)} verified correction records.")

    # Quality Gate Assessment
    quality_report = service.validate_quality_gates(records)
    logger.info("=== Quality Gate Assessment Report ===")
    logger.info(f"Total Records: {quality_report['total_records']}")
    logger.info(f"Average Inter-Annotator Agreement: {quality_report.get('avg_agreement', 0.0):.2f}")
    logger.info(f"Class Distribution: {quality_report.get('class_distribution', {})}")
    logger.info(f"Quality Gates Passed: {quality_report['passed']}")

    if not quality_report["passed"]:
        for reason in quality_report.get("reasons", []):
            logger.warning(f"  [GATE WARNING] {reason}")

    if args.dry_run:
        logger.info("Dry-run complete. No files written.")
        return

    # Export formatting
    formatted = service.format_to_gemini_sft_jsonl(records)
    train_split, val_split, test_split = service.generate_splits(formatted)

    os.makedirs(args.out_dir, exist_ok=True)

    def write_jsonl(filename: str, dataset: list):
        path = os.path.join(args.out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(item) + "\n")
        logger.info(f"Wrote {len(dataset)} lines to {path}")

    write_jsonl("train.jsonl", train_split)
    write_jsonl("val.jsonl", val_split)
    write_jsonl("test.jsonl", test_split)

    logger.info("Dataset export completed successfully.")


if __name__ == "__main__":
    main()
