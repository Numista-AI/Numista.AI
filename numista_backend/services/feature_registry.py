"""
Feature Registry — Dynamic Knowledge & Capability System for Morgan AI
Allows routes and services to register platform capabilities via @register_feature decorator.
Injects active features into Morgan AI's system prompt and RAG index automatically.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable

logger = logging.getLogger("numista_backend.feature_registry")


@dataclass
class FeatureDescriptor:
    name: str
    description: str
    keywords: List[str]
    synonyms: List[str]
    instructions: str
    enabled: bool = True


class FeatureRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeatureRegistry, cls).__new__(cls)
            cls._instance._features: Dict[str, FeatureDescriptor] = {}
            cls._instance._init_default_features()
        return cls._instance

    def _init_default_features(self):
        """Pre-registers core built-in features."""
        self.register(
            FeatureDescriptor(
                name="Lateral Transfer (Passport Protocol)",
                description="Secure account-to-account coin and asset transfer protocol with provenance tracking.",
                keywords=["transfer", "lateral transfer", "passport", "claim pin", "passport certificate"],
                synonyms=["move coins", "send coins", "give to login", "share collection", "account transfer"],
                instructions=(
                    "Users CAN transfer coins and notes directly to another Numista.AI account using Lateral Transfer.\n"
                    "How it works:\n"
                    "1. User opens 'Lateral Transfer' from side menu or coin detail, selects items, and clicks 'Generate Passport Token & PDF'.\n"
                    "2. System generates a 6-digit Claim PIN code and an Official Passport Certificate (PDF).\n"
                    "3. If recipient email is specified, system emails the Passport Certificate & PIN to the recipient. Only that recipient email account can claim it.\n"
                    "4. Recipient signs into Numista.AI (numista.ai), clicks 'Claim / Receive Transfer', enters Transfer ID & PIN, and adopts items into their vault with full legal provenance records."
                ),
                enabled=True
            )
        )
        self.register(
            FeatureDescriptor(
                name="Binder Scan & AI Ingestion",
                description="Instant multi-coin page scanner using computer vision and Gemini multimodal AI.",
                keywords=["binder scan", "scan page", "camera scan", "photo import"],
                synonyms=["scan coins", "scan binder", "upload photo"],
                instructions="Users can scan coin album pages or binder slots to auto-detect and catalog coins.",
                enabled=True
            )
        )
        self.register(
            FeatureDescriptor(
                name="1-Click Insurance & Estate Appraisal",
                description="Generates legal-grade PDF schedules for collection insurance and estate planning.",
                keywords=["estate", "insurance", "appraisal", "estate report", "pdf export"],
                synonyms=["create report", "insurance valuation", "will and estate"],
                instructions="Users can generate 1-Click Estate & Insurance Appraisal PDF reports from the Estate Planning tab or collection options.",
                enabled=True
            )
        )
        self.register(
            FeatureDescriptor(
                name="PCGS Cert Verification & Valuation",
                description="Direct verification of certified slabs via PCGS, NGC, ANACS, and CAC.",
                keywords=["pcgs", "ngc", "anacs", "cac", "cert verification", "slab"],
                synonyms=["verify cert", "cert lookup", "slabbed coin"],
                instructions="Clicking the certification number on any slabbed coin opens official verification pages on PCGS/NGC.",
                enabled=True
            )
        )

    def register(self, feature: FeatureDescriptor):
        """Registers a feature descriptor."""
        self._features[feature.name] = feature
        logger.info(f"Registered feature capability for Morgan AI: {feature.name}")

    def get_feature(self, name: str) -> Optional[FeatureDescriptor]:
        return self._features.get(name)

    def get_all_active_features(self) -> List[FeatureDescriptor]:
        return [f for f in self._features.values() if f.enabled]

    def build_morgan_prompt_context(self) -> str:
        """Formats active feature capabilities for Morgan AI system prompt injection."""
        active = self.get_all_active_features()
        if not active:
            return ""

        lines = ["\nActive Numista.AI Platform Features & Capabilities:"]
        for feat in active:
            keywords_str = ", ".join(feat.keywords + feat.synonyms)
            lines.append(f"• Feature: {feat.name}")
            lines.append(f"  - Key Terms & Intent Matchers: {keywords_str}")
            lines.append(f"  - How to Use & Capabilities: {feat.instructions}")
        return "\n".join(lines)


# Singleton instance
registry = FeatureRegistry()


def register_feature(
    name: str,
    description: str,
    keywords: List[str],
    synonyms: List[str],
    instructions: str,
    enabled: bool = True
):
    """
    Decorator for registering platform features to Morgan AI.
    Usage:
        @register_feature(
            name="My Feature",
            description="...",
            keywords=["..."],
            synonyms=["..."],
            instructions="..."
        )
        def my_route():
            ...
    """
    def decorator(func: Callable):
        registry.register(
            FeatureDescriptor(
                name=name,
                description=description,
                keywords=keywords,
                synonyms=synonyms,
                instructions=instructions,
                enabled=enabled
            )
        )
        return func
    return decorator
