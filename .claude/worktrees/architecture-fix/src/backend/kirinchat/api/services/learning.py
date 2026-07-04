from collections import defaultdict
from typing import Dict, List, Optional

from loguru import logger

from kirinchat.api.services.skill import SkillService
from kirinchat.database.dao.interview import (
    EvaluationReportDao,
    InterviewSessionDao,
)


class LearningService:
    """Generate personalized learning recommendations based on interview history."""

    # Score thresholds for overall level (0-10 scale)
    _LEVEL_THRESHOLDS = [
        (8.5, "excellent", "优秀"),
        (7.0, "intermediate", "中级"),
        (5.0, "beginner", "初级"),
        (0, "needs_work", "需努力"),
    ]

    @classmethod
    async def get_user_weak_categories(cls, user_id: str, skill_id: str) -> List[dict]:
        """Analyze all evaluation reports for a user+skill and return
        categories sorted by average score (lowest first).

        Returns:
            [{"category": "mysql", "label": "MySQL", "avg_score": 5.2, "session_count": 3}, ...]
        """
        # Get all completed sessions for this user
        sessions = await InterviewSessionDao.select_sessions_by_user(user_id)
        completed = [s for s in sessions if s.status == "COMPLETED" and s.skill_id == skill_id]

        if not completed:
            return []

        # Aggregate category scores across sessions
        score_sums: Dict[str, float] = defaultdict(float)
        score_counts: Dict[str, int] = defaultdict(int)

        for session in completed:
            report = await EvaluationReportDao.select_report_by_session(session.id)
            if report and report.category_scores:
                for cat, score in report.category_scores.items():
                    score_sums[cat] += float(score)
                    score_counts[cat] += 1

        if not score_sums:
            return []

        # Load skill to get category labels
        skill = SkillService.get_skill_by_id(skill_id)
        label_map = {}
        if skill:
            for cat in skill.get("categories", []):
                label_map[cat["key"]] = cat.get("label", cat["key"])

        # Build result sorted by avg_score ascending
        result = []
        for cat in score_sums:
            avg = score_sums[cat] / score_counts[cat]
            result.append({
                "category": cat,
                "label": label_map.get(cat, cat),
                "avg_score": round(avg, 1),
                "session_count": score_counts[cat],
            })

        result.sort(key=lambda x: x["avg_score"])
        return result

    @classmethod
    def get_learning_resources(cls, skill_id: str, categories: List[str]) -> Dict[str, dict]:
        """Load reference materials for the given categories.

        Returns:
            {"mysql": {"label": "MySQL", "reference": "# MySQL 核心..."}, ...}
        """
        skill = SkillService.get_skill_by_id(skill_id)
        if not skill:
            return {}

        label_map = {}
        ref_map = {}
        for cat in skill.get("categories", []):
            label_map[cat["key"]] = cat.get("label", cat["key"])
            if cat.get("ref"):
                ref_map[cat["key"]] = cat["ref"]

        # Load references (use cached get_skill_by_id which already loads them)
        references = skill.get("references", {})

        resources = {}
        for cat_key in categories:
            ref_content = references.get(cat_key)
            if ref_content:
                resources[cat_key] = {
                    "label": label_map.get(cat_key, cat_key),
                    "reference": ref_content,
                }

        return resources

    @classmethod
    async def get_learning_path(cls, user_id: str, skill_id: str) -> Optional[dict]:
        """Generate a complete personalized learning path.

        Returns None if the skill doesn't exist.
        """
        skill = SkillService.get_skill_by_id(skill_id)
        if skill is None:
            return None

        weak_categories = await cls.get_user_weak_categories(user_id, skill_id)

        # Determine study order (lowest score first)
        study_order = [wc["category"] for wc in weak_categories]

        # Load resources for weak categories
        resources = cls.get_learning_resources(skill_id, study_order)

        # Calculate overall level
        total_sessions = len(set(
            s.id for s in await InterviewSessionDao.select_sessions_by_user(user_id)
            if s.status == "COMPLETED" and s.skill_id == skill_id
        ))

        if weak_categories:
            overall_avg = sum(wc["avg_score"] for wc in weak_categories) / len(weak_categories)
        else:
            overall_avg = 0

        overall_level = "needs_work"
        overall_level_label = "需努力"
        for threshold, level, label in cls._LEVEL_THRESHOLDS:
            if overall_avg >= threshold:
                overall_level = level
                overall_level_label = label
                break

        return {
            "skill_id": skill_id,
            "skill_name": skill.get("name", skill_id),
            "weak_categories": weak_categories,
            "resources": resources,
            "study_order": study_order,
            "total_sessions": total_sessions,
            "overall_avg_score": round(overall_avg, 1),
            "overall_level": overall_level,
            "overall_level_label": overall_level_label,
        }
